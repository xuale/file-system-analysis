#!/usr/bin/python

import csv
import sys
import os

superblock = []
freeblocks = []
freeinodes = []
dirents = []
indirents = []
inodes = []


def dump_error(msg):
	sys.stderr.write(msg)
	exit(1)

def check_block():
    print("check block")
def check_inode():
    print("check inode")
def check_directory():
    print("check directory")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        dump_error("Only 1 argument")
    if not os.path.isfile(sys.argv[1]):
	print_error("File does not exist")
    
    # getting data into global vars
    with open(sys.argv[1], 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) <= 0:
		dump_error("Error: file contains blank line\n")
	    if row[0] == 'SUPERBLOCK':
		superblock = row
	    elif row[0] == 'BFREE':
		freeblocks.append(int(row[1]))
	    elif row[0] == 'IFREE':
		freeinodes.append(int(row[1]))
	    elif row[0] == 'DIRENT':
		dirents.append(row)
	    elif row[0] == 'INODE':
		inodes.append(row)
	    elif row[0] == 'INDIRECT':
		indirects.append(row)
	    elif row[0] != 'GROUP':
		dump_error("Error: unrecognized line in csv\n")
    check_block()
    check_inode()
    check_directory()
    exit(0)
