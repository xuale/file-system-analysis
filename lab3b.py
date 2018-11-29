#!/usr/bin/python

import csv
import sys
import os

superblock = []
freeblocks = []
freeinodes = []
dirents = []
indirects = []
inodes = []

haserror = False

def dump_error(msg):
	sys.stderr.write(msg)
	exit(1)

def check_block():
  global indirects, haserror
	#for inode in inodes:
	#for indirect in indirects:

def check_inode():
	
	global freeinodes, inodes, haserror
	unallocated = freeinodes
	allocated = []

	for inode in inodes:
		number = int(inode[1])
		filetype = inode[2]
		isallocated = filetype != '0'
		if isallocated:
			if number in freeinodes:
				print("ALLOCATED INODE {} ON FREELIST".format(number))
				haserror = True
				unallocated.remove(number)
			allocated.append(inode)
		else:
			if number not in freeinodes:
				print("UNALLOCATED INODE {} NOT ON FREELIST".format(number))
				haserror = True
				unallocated.append(number)

	start = int(superblock[7])
	offset = int(superblbock[2])
	for number in range(start, offset):
		usedcount = 0
		for inode in inodes:
			usednum = int(inode[1])
			if usednum == number:
				usedcount += 1
		if number not in freeinodes and usedcount <= 0:
			print("UNALLOCATED INODE {} NOT ON FREELIST".format(number))
			haserror = True
			unallocated.append(number)
	
	# reset global values
	inodes = allocated
	freeinodes = unallocated

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
						elif row[0] == 'SUPERBLOCK':
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
							dump_error("Invalid line in CSV\n")
    check_block()
    check_inode()
    check_directory()
    
	if haserror:
		exit(2)
	else:
		exit(0)
