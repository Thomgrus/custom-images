from argparse import ArgumentParser, Namespace
from crypt import methods
import datetime
import json
from zipfile import ZipFile
import pytz
import requests
import os
import xml.etree.ElementTree as ET
import locale
from flask import Flask, request

app = Flask(__name__)

SOURCE_PROGRAMME = 'https://xmltv.ch/xmltv/xmltv-tnt.zip'

NOW = pytz.timezone('Europe/Paris').localize(datetime.datetime.now())
DATETIME_FORMAT = "%Y%m%d%H%M%S %z"
TARGET_CHANNELS = {
    'tf1': 'C192.api.telerama.fr', # TF1
    'france2': 'C4.api.telerama.fr', # France 2
    'm6': 'C118.api.telerama.fr', # M6
    'c8': 'C445.api.telerama.fr', # C8
    'w9': 'C119.api.telerama.fr', # W9
    'tmc': 'C195.api.telerama.fr', # TMC
    'tfx': 'C446.api.telerama.fr', # TFX
    'nrj12': 'C444.api.telerama.fr', # NRJ 12
    'gulli': 'C482.api.telerama.fr', # Gulli
    'tf1serie': 'C1404.api.telerama.fr', # TF1 Serie Film
    '6ter': 'C1403.api.telerama.fr', # 6Ter
}
locale.setlocale(locale.LC_ALL, os.getenv('LC_ALL', 'fr_FR'))

def fetch_xmltv():
    xml_filename = 'xmltv-tnt.xml'
    if os.path.exists(xml_filename):
        tree = ET.parse(xml_filename)
        last_program = tree.find('programme[last()]')
        start_date = datetime.datetime.strptime(last_program.attrib['start'], DATETIME_FORMAT)
        if not start_date < NOW:
            print('Fetch skip')
            return
    r = requests.get(SOURCE_PROGRAMME)
    dest_zipfile = 'xmltv-tnt.zip'
    with open(dest_zipfile, 'wb') as xmltv_zipfile:
        xmltv_zipfile.write(r.content)
    with ZipFile(dest_zipfile, 'r') as zip_obj:
        zip_obj.extractall()
    os.remove(dest_zipfile)
    print('Fetch applied')

def filter_program(channel_program: ET.Element):
    stop_prog = datetime.datetime.strptime(channel_program.attrib['stop'], DATETIME_FORMAT)
    if stop_prog < NOW:
        return False
    start_prog = datetime.datetime.strptime(channel_program.attrib['start'], DATETIME_FORMAT)
    if not (20 <= start_prog.hour <= 21):
        return False
    if (start_prog.hour == 20 and start_prog.minute < 40) or (start_prog.hour == 21 and start_prog.minute > 15):
        return False
    duration = (stop_prog - start_prog).total_seconds()/60
    if duration < 20:
        return False
    if start_prog.day != NOW.day:
        return False
    return True

def transform_channel_program(channel_program: ET.Element):
    if not channel_program:
        return None
    stop_prog = datetime.datetime.strptime(channel_program.attrib['stop'], DATETIME_FORMAT)
    start_prog = datetime.datetime.strptime(channel_program.attrib['start'], DATETIME_FORMAT)
    program = {
        'key': datetime.datetime.strftime(start_prog, '%Y%m%d'),
        'title': channel_program.find('title').text,
        'full_day': datetime.datetime.strftime(start_prog, '%A %d %B'),
        'start': datetime.datetime.strftime(start_prog, '%H:%M'),
        'stop': datetime.datetime.strftime(stop_prog, '%H:%M'),
        'icon': channel_program.find('icon').attrib['src']
    }
    desc_node = channel_program.find('desc')
    if (desc_node is not None):
        program['description'] = desc_node.text
    return program


def process_channel_program(tree: ET.ElementTree, channel_id):
    all_channel_programs = tree.findall(f'programme[@channel=\'{channel_id}\']')
    channel_programs = filter(filter_program, all_channel_programs)
    first_channel_program = next(channel_programs, None)
    app_program = transform_channel_program(first_channel_program)
    programs = []
    if app_program:
        programs.append(app_program)
    return programs

def process_xmltv(target_channels):
    result = []
    tree = ET.parse('xmltv-tnt.xml')
    for ch_elem in tree.findall('channel'):
        channel_id = ch_elem.attrib['id']
        if not channel_id in target_channels:
            continue
        channel = {
            'name': ch_elem.find('display-name').text,
            'icon': ch_elem.find('icon').attrib['src'],
            'programs': process_channel_program(tree, channel_id)
        }
        result.append(channel)
    return result

def to_blocks(today_program, verbose):
    result = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Programme TV* de ce soir ({datetime.datetime.strftime(NOW, '%A %d %B')}):"
            }
        },
        {
            "type": "divider"
        }
    ]
    channels_to_send = filter(lambda c: c['programs'], today_program)
    for channel in channels_to_send:
        program = channel['programs'][0]
        program_message = f"Sur *{channel['name']}* \n *{program['title']}* \n {program['start']} - {program['stop']}"
        if 'description' in program and verbose:
            program_message += f" \n\n {program['description']}"
        result.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": program_message
            },
            "accessory": {
                "type": "image",
                "image_url": program['icon'],
                "alt_text": f"{program['title']} icon"
            },
        })
        result.append({"type": "divider"})
    return result

def to_texts(today_program):
    channels_to_send = filter(lambda c: c['programs'], today_program)
    res = ':tv:'
    for channel in channels_to_send:
        program = channel['programs'][0]
        res += f' | {channel["name"]}: {program["title"]}'
    return res

def send_today_program(args, today_program):
    r = requests.post(args.webhook, json={
        'text': to_texts(today_program),
        'username': 'Programme TNT',
        'icon_emoji': ':tv:',
        'blocks': to_blocks(today_program, args.verbose)
        })
    if r.status_code == 200:
        print('Successfully send to slack')
    else:
        print('Error occurs sending to slack channel')


def fetch_program(args):
    global NOW
    NOW = pytz.timezone('Europe/Paris').localize(datetime.datetime.now())
    print(f'Fetch programs for {args.channels}')
    target_channels = list(TARGET_CHANNELS[x] for x in args.channels)
    fetch_xmltv()
    today_program = process_xmltv(target_channels)
    send_today_program(args, today_program)

@app.route('/send', methods=['GET'])
def send_program():
    args = Namespace(
        force_refresh=(request.args.get('force', 'False') == 'True'),
        webhook=os.getenv('PROGRAMME_TNT_SLACK_WEBHOOK'),
        verbose=os.getenv('PROGRAMME_TNT_VERBOSE') == 'True',
        channels=request.args.getlist('channels')
    )
    fetch_program(args)
    return json.dumps({'success': True})

def server_program(args):
    os.environ['PROGRAMME_TNT_SLACK_WEBHOOK'] = args.webhook
    os.environ['PROGRAMME_TNT_VERBOSE'] = str(args.verbose)
    if args.expose:
        app.run(host="0.0.0.0")
    else:
        app.run()
    


parser = ArgumentParser(prog='programme-tnt')
subparsers = parser.add_subparsers(title='subcommands', help='target goal for programme', required=True)

cli_parser = subparsers.add_parser('cli', help='cli version of programme-tnt')
cli_parser.add_argument('-f', '--force-refresh', help="Force the refresh of programme tv database", action="store_true", default=False)
cli_parser.add_argument('-w', '--webhook', help="Slack webhook to send program. Default env SLACK_WEBHOOK", default=os.getenv('SLACK_WEBHOOK'))
cli_parser.add_argument('-v', '--verbose', help="Display many information like description", action="store_true", default=False)
cli_parser.add_argument('-c', '--channels', nargs='+', help="Select specific channels. Default ALL available by app.", default=list(TARGET_CHANNELS.keys()))
cli_parser.set_defaults(func=fetch_program)

server_parser = subparsers.add_parser('server', help='server version of programme-tnt')
server_parser.add_argument('-w', '--webhook', help="Slack webhook to send program. Default env SLACK_WEBHOOK", default=os.getenv('SLACK_WEBHOOK'))
server_parser.add_argument('-v', '--verbose', help="Display many information like description", action="store_true", default=False)
server_parser.add_argument('-e', '--expose', help="Expose the server", action="store_true", default=False)
server_parser.set_defaults(func=server_program)

def main(args):
    '''Backuper allows you to backup / restore a path'''
    args.func(args)


if __name__ == '__main__':
    main(parser.parse_args())