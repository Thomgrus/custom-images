from argparse import ArgumentParser
from ast import arg
import json
import os
import time
import tarfile
import shutil
from pathlib import Path
from ftplib import FTP

METADATA_FILENAME = 'last_backup.json'

def process_metadata(target_path):
    file_path = os.path.join(target_path, METADATA_FILENAME)
    try:
        with open(file_path) as f:
            json_data = json.load(f)
            return json_data
    except OSError:
        print(f'Error when trying to load {file_path}')
    return False

def uncompress_tarfile(input_filename, target_dir):
    with tarfile.open(input_filename, "r:gz") as tar:
        tar.extractall(path=target_dir)

def ftp_restore(args, metadata):
    ftp_config = process_ftp_config_file(args.ftp_file)
    ftp = FTP(host=ftp_config["host"])
    ftp.login(user=ftp_config["user"],passwd=ftp_config["password"])

    # Move into backups folder on ftp server
    path = os.path.normpath(args.backup_path)
    path.split(os.sep)
    for directory in path.split(os.sep):
        ftp.cwd(directory)

    l = ftp.nlst()
    l.sort()
    l.remove('..')

    last_backup = l[-1]
    if metadata and last_backup == f'{metadata["current_time"]}.tar.gz':
        print(f'👍 Already at last backup')
    else:
        with open(last_backup, 'wb') as fp:
            ftp.retrbinary(f'RETR {last_backup}', fp.write)
        ftp.close()
        try:
            shutil.rmtree(args.target)
            print(f'✅ Target dir removed')
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
        uncompress_tarfile(last_backup, Path(os.path.join(args.target)).parent.absolute())
        print(f'✅ Backup restored')

def local_restore(args, metadata):
    l = os.listdir(args.backup_path)
    l.sort()
    last_backup = l[-1]
    if metadata and last_backup == f'{metadata["current_time"]}.tar.gz':
        print(f'👍 Already at last backup')
    else:
        try:
            shutil.rmtree(args.target)
            print(f'✅ Target dir removed')
        except OSError as e:
            print("Error: %s - %s." % (e.filename, e.strerror))
        uncompress_tarfile(os.path.join(args.backup_path, last_backup), Path(os.path.join(args.target)).parent.absolute())
        print(f'✅ Backup restored')
        os.remove(last_backup)

def restore(args):
    metadata = process_metadata(args.target)
    if not args.ftp_file:
        local_restore(args, metadata)
    else:
        ftp_restore(args, metadata)

def make_tarfile(output_filename, source_dir):
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

def process_ftp_config_file(file_path):
    try:
        with open(file_path) as f:
            json_data = json.load(f)
            return json_data
    except OSError:
        print(f'Error when trying to load {file_path}')
    return False

def ftp_backup(args, tar_name):
    ftp_config = process_ftp_config_file(args.ftp_file)
    ftp = FTP(host=ftp_config["host"])
    ftp.login(user=ftp_config["user"],passwd=ftp_config["password"])

    make_tarfile(tar_name, args.target)
    print(f'✅ backup created {tar_name}')

    # Ensure backup path is present on ftp server
    path = os.path.normpath(args.backup_path)
    path.split(os.sep)
    for directory in path.split(os.sep):
        if not directory in ftp.nlst():
            ftp.mkd(directory)
        ftp.cwd(directory)
    
    # Send tar
    with open(tar_name, 'rb') as f:
        ftp.storbinary(f'STOR {tar_name}', f)
    print(f'✅ backup send to ftp {ftp_config["host"]}')
    
    os.remove(tar_name)

    # Apply retention
    l = ftp.nlst()
    l.sort(reverse=True)
    l.remove('..')
    for backup in l[args.retention:]:
        ftp.delete(backup)
    print(f'✅ retention {args.retention} applied')

    ftp.close()

def local_backup(args, tar_name):
    Path(args.backup_path).mkdir(parents=True, exist_ok=True)
    tarfile_path = os.path.join(args.backup_path, tar_name)
    make_tarfile(tarfile_path, args.target)
    print(f'✅ backup created {tarfile_path}')
    l = os.listdir(args.backup_path)
    l.sort(reverse=True)
    for backup in l[args.retention:]:
        os.remove(os.path.join(args.backup_path, backup))
    print(f'✅ retention {args.retention} applied')

def backup(args):
    t = time.localtime()
    current_time = time.strftime('%Y-%m-%d-%H-%M-%S', t)
    file_path = os.path.join(args.target, METADATA_FILENAME)
    with open(file_path, 'w') as outfile:
        metadata = {"current_time": current_time}
        json.dump(metadata, outfile)
    print(f'✅ metadata created {file_path}')
    tar_name = f'{current_time}.tar.gz'
    if not args.ftp_file:
        local_backup(args, tar_name)
    else:
        ftp_backup(args, tar_name)

parser = ArgumentParser(prog='backuper')
subparsers = parser.add_subparsers(title='subcommands', help='target goal for backup', required=True)

backup_parser = subparsers.add_parser('backup', help='backup a folder')
backup_parser.add_argument('-t', '--target', help='target path to backup', required=True)
backup_parser.add_argument('-b', '--backup-path', help='backup path where backup will be created', required=True)
backup_parser.add_argument('-r', '--retention', help='number max of backup stored', default=4)
backup_parser.add_argument('-s', '--ftp-file', help='ftp config json file', default=False)
backup_parser.set_defaults(func=backup)

restore_parser = subparsers.add_parser('restore', help='restore a folder')
restore_parser.add_argument('-t', '--target', help='target path to restore', required=True)
restore_parser.add_argument('-b', '--backup-path', help='backup path where backup are located', required=True)
restore_parser.add_argument('-f', '--force', help='force restore even if not needed', action='store_true')
restore_parser.add_argument('-s', '--ftp-file', help='ftp config json file', default=False)
restore_parser.set_defaults(func=restore)

def main(args):
    '''Backuper allows you to backup / restore a path'''
    args.func(args)


if __name__ == '__main__':
    main(parser.parse_args())