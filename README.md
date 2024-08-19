# birdkeeper
Bird keeper project manages LUKS encripted HDD drives HDD hard drives.

Used for backing up information from one encrypted file to other using the rsync linux 
functionality.

usage: birdkeeper.py [-h] [-b BIRD] [--mount] [--umount] [--health] [--backup] [--space] [--src SRC] [--to TO]

options:
  -h, --help            show this help message and exit
  -b BIRD, --bird BIRD  choose angry bird.
  --mount               mount hdd.
  --umount              umount hdd.
  --health              check disk health.
  --backup              backup hdd disks.
  --space               show disk space.
  --src SRC             backup from disk.
  --to TO               backup to disk.