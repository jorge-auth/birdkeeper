#!/usr/bin/python3
import subprocess
import re
import argparse
import logging
import sys
from pprint import pprint
import getpass
from time import sleep
import configparser
import os


config = configparser.ConfigParser()
fn = "birds.ini"

try:
    config_path = os.path.join("/etc/birdkeeper", fn)
    config.read(config_path)
except configparser.ParsingError as e:
    logging.error("Missing configuration file {e}")
    sys.exit()

try:
    UUID = config['UUID']
except:
    logging.error("Error parsing file /etc/birdkeeper/bird.ini")
    sys.exit()

#utils
def parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--bird",type=str, help="choose angry bird.")
    parser.add_argument("--mount", action="store_true", help="mount hdd.")
    parser.add_argument("--umount", action="store_true", help="umount hdd.")
    parser.add_argument("--health", action="store_true", help="check disk health.")
    parser.add_argument("--backup", action="store_true", help="backup hdd disks.")

    parser.add_argument("--space", action="store_true", help="show disk space.")
    parser.add_argument("--src", type=str, help="backup from disk.")
    parser.add_argument("--to", type=str, help="backup to disk.")
    return parser

def logger():
    Logger = logging.getLogger()
    Logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    Logger.addHandler(handler)
    return Logger

Logger = logger()

#funcs
class BK:
    def __init__(self):
        pass

    def get_identifiers(self, uuid):
        mount_point = None
        p = subprocess.Popen('blkid', shell=True, stdout=subprocess.PIPE)
        output = p.stdout.read()
        lines = output.decode().split('\n')
        rgx1 = re.compile('^(.*?):')
        rgx2 = re.compile('^.*: UUID=\"(\w+-\w+-\w+-\w+-\w+)\".*$')

        for l in lines:
            match_mount = rgx1.search(l)
            match_uuid = rgx2.search(l)
            if match_mount and match_uuid:
                if match_uuid.group(1) == uuid:
                    mount_point = match_mount.group(1)
        return mount_point

    def get_all_identifiers(self):
        for i, j in UUID.items():
            mount_id = bk.get_identifiers(j)
            if mount_id:
                Logger.info( '{0} bird uuid {1} mounted in {2}'.format(i, j, mount_id ) )

    def mount_device(self, bird, mount_id):
        subprocess.Popen( 'cryptsetup -d /etc/luks-keys/labhdd1key.file luksOpen {0} {1}'.format(mount_id, bird), shell=True )
        subprocess.Popen( 'mkdir -p /{}'.format(bird), shell=True)

        count = 0
        while( not self.verify_mounted(bird)):
            print("Device mounting...")
            subprocess.Popen( 'mount /dev/mapper/{0} /{1}'.format(bird, bird), shell=True)
            if count >= 5:
                break
            count+=1
            sleep(3)
        else:
            Logger.info("Device mounted!")

    def umount_device(self, bird):
        count = 0
        while( bk.verify_mounted(bird)):
            print("Device still mounted...")
            subprocess.Popen('umount /{}'.format(bird), shell=True)
            if count >= 5:
                break
            count+=1
            sleep(3)
        else:
            Logger.info("Device unmounted!")

        subprocess.Popen('cryptsetup luksClose /dev/mapper/{}'.format(bird), shell=True)

    def verify_mounted(self, bird):
        p = subprocess.Popen('mount -l', shell=True, stdout=subprocess.PIPE)
        output = p.stdout.read()
        lines = output.decode().split('\n')
        rgx = re.compile('^/dev/mapper/{0} on /{1}.*$'.format(bird, bird) )
        
        for l in lines:
            match_mount = rgx.search(l)
            if match_mount:
                Logger.info(l)
                return True
    
        return False

    def backup(self, src, to):
        proc = subprocess.Popen( 'rsync -avP --delete --delete-excluded /{0}/* /{1}'.format(src, to), shell=True, 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE
            )

        while True:
            output = proc.stdout.readline()
            Logger.info(output)
            if output == b'':
                break

    def health_check(self, bird): 
        subprocess.Popen( 'fsck /dev/mapper/{}'.format(bird), shell=True)


    def disk_space(self, bird):
        lines= subprocess.Popen(['df', '-h'], stdout=subprocess.PIPE)
        output = lines.communicate()[0].decode('utf-8')
        output = output.split('\n')

        if not self.verify_mounted(bird):
            Logger.info("Bird {} not mounted".format(bird))

        for line in output:
            if "/dev/mapper/{}".format(bird) in line:
                Logger.info(line)
                break


if __name__ == "__main__":
    bird, mount_id = None, None
    username = getpass.getuser()
    bk = BK()

    parser = parser()
    args = parser.parse_args()
    
    if args.bird:
        bird = args.bird
        uuid = UUID[bird]
        mount_id = bk.get_identifiers(uuid)
        print( '{0} bird uuid {1} mounted in {2}'.format(bird, uuid, mount_id ) )

    if args.mount and args.bird:
        if username != "root":
            print('You need root permissions to mount the device.')
            sys.exit()
        bk.mount_device( bird, mount_id )
        sys.exit()

    if args.umount and args.bird:
        if username != "root":
            print('You need root permissions to mount the device.')
            sys.exit()

        bk.umount_device(bird)
        sys.exit()
    
    if args.health and args.bird:
        bk.health_check(args.bird)

    if args.space and args.bird:
        bk.disk_space(args.bird)
    
    if args.backup and args.src and args.to:
        if username == 'root':
            print('Dont user root permissions for the backup!')
            sys.exit()
        
        src_bird = None
        dest_bird = None
        src_bird = bk.verify_mounted(args.src)
        dest_bird = bk.verify_mounted(args.to)
        
        if(src_bird and dest_bird):
            bk.backup(args.src, args.to)
        else:
            if not src_bird:
                print("{} is not mounted.".format(args.src))
            if not dest_bird:
                print("{} is not mounted.".format(args.to))
    
    if not args.bird:
        bk.get_all_identifiers()
        sys.exit()
