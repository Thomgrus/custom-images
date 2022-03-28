from argparse import ArgumentParser

import ikea_api
import asyncio
import locale
import os
import requests

locale.setlocale(locale.LC_ALL, os.getenv('LC_ALL', 'fr_FR'))

constants = ikea_api.Constants(country="fr", language="fr")
token = ikea_api.run(ikea_api.Auth(constants).get_guest_token())

def to_blocks(deliveries, product):
    result = [{
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": ':muscle: Votre produit est disponible :'
                }
            }]
    type_to_deliveries = { delivery.type : [] for delivery in deliveries }
    for delivery in deliveries:
        type_to_deliveries[delivery.type].append(delivery)
        
    for type in type_to_deliveries:
        for delivery in type_to_deliveries[type]:
            result.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f':star: *{delivery.type}* -> *{delivery.service_provider}* ({delivery.date})\n'
                }
            })
        result.append({"type": "divider"})
    result.append({"type": "divider"})
    product_link = f'https://www.ikea.com/fr/fr/catalog/products/{product}'
    result.append({
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f'Vous pouvez vous rendre ici:\n{product_link}'
        }
    })
    return result


def send_delivery_to_slack(webhook, deliveries, product):
    if (not webhook):
        print('No webhook set: no notification sent.')
        return
    r = requests.post(webhook, json={
        'text': 'Produit IKEA disponible !',
        'username': 'IKEA',
        'icon_emoji': ':white_check_mark:',
        'blocks': to_blocks(deliveries, product)
        })
    if r.status_code == 200:
        print('Successfully send to slack')
    else:
        print('Error occurs sending to slack channel')

async def get_deliveries(product, zip_code):
    services = await ikea_api.get_delivery_services(
        constants=constants,
        token=token,
        items={
            product: 1
        },
        zip_code=zip_code)
    return services.delivery_options

def ikea(args):
    deliveries = asyncio.run(get_deliveries(args.product, args.zip_code))
    for delivery in deliveries:
        print(f'{delivery.type} -> {delivery.service_provider} ({delivery.date})')
    if len(deliveries):
        send_delivery_to_slack(args.webhook, deliveries, args.product)
        print('🎊')
    else:
        print('No delivery available')
        if not args.batch:
            exit(1)


parser = ArgumentParser(prog='ikea-checker')
parser.add_argument('-p', '--product', help='product you want to check availability', required=True)
parser.add_argument('-z', '--zip-code', help='zip-code used by the home check', required=True)
parser.add_argument('-w', '--webhook', help="Slack webhook to send program. Default env SLACK_WEBHOOK", default=os.getenv('SLACK_WEBHOOK'))
parser.add_argument('-b', '--batch', help="Do not failed if no delivery options are available", action="store_true", default=False)
parser.set_defaults(func=ikea)

def main(args):
    '''ikea-checker allows you to check product availability'''
    args.func(args)


if __name__ == '__main__':
    main(parser.parse_args())
