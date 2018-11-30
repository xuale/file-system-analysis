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
#key: iblock number value: array of error message if dup
block_references = {}

def dump_error(msg):
	sys.stderr.write(msg)
	exit(1)

def scan_block(i_block, inode_no, offset, block_type):
	global haserror, block_references, superblock
	if i_block == 0:
		return
	if i_block > int(superblock[1]) - 1:
		print("INVALID {}BLOCK {} IN INODE {} AT OFFSET {}".format(block_type, i_block, inode_no, offset))
	elif i_block < 8:
		print("RESERVED {}BLOCK {} IN INODE {} AT OFFSET {}".format(block_type, i_block, inode_no, offset))
		haserror = True
	elif i_block not in block_references:
		block_references[i_block] = ["DUPLICATE {}BLOCK {} IN INODE {} AT OFFSET {}".format(block_type, i_block, inode_no, offset)]
	elif "DUPLICATE {}BLOCK {} IN INODE {} AT OFFSET {}".format(block_type, i_block, inode_no, offset) not in block_references[i_block]:
		block_references[i_block].append("DUPLICATE {}BLOCK {} IN INODE {} AT OFFSET {}".format(block_type, i_block, inode_no, offset))

def check_block():
	global haserror, inodes, block_references, indirects, freeblocks
	for inode in inodes:
		count = 0
		for i in range(12, 27):
			if i == 24:
				scan_block(int(inode[i]), inode[1], 12, "INDIRECT ")
			elif i == 25:
				scan_block(int(inode[i]), inode[1], 268, "DOUBLE INDIRECT ")
			elif i == 26:
				scan_block(int(inode[i]), inode[1], 65804, "TRIPLE INDIRECT ")
			else:
				scan_block(int(inode[i]), inode[1], count, "")
			count = count + 1
	for indirect in indirects:
		indirect_level = ""
		if indirect[2] == "1":
			indirect_level = "INDIRECT "
		elif indirect[2] == "2":
			indirect_level = "DOUBLE INDIRECT "
		elif indirect[2] == "3":
			indirect_level = "TRIPLE INDIRECT "
		scan_block(int(indirect[5]), indirect[1], int(indirect[3]), indirect_level)
	for iblock in range(8, int(superblock[1])):
		if iblock in freeblocks and iblock in block_references:
			print("ALLOCATED BLOCK {} ON FREELIST".format(iblock))
			haserror = True
		if iblock not in freeblocks and iblock not in block_references:
			print("UNREFERENCED BLOCK {}".format(iblock))
			haserror = True
		if iblock in block_references and len(block_references[iblock]) > 1:
			for msg in block_references[iblock]:
				print(msg)
				haserror = True

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
	offset = int(superblock[2])
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
	global haserror
	inodecnt = int(superblock[2])
	linkdict = {}
	parentdict = {2: 2}

	for dirent in dirents:
		entrynum = int(dirent[3])
		entryname = dirent[6].rstrip()
		parentnum = int(dirent[1])
		if entrynum > inodecnt:
			print("DIRECTORY INODE {} NAME {} INVALID INODE {}".format(parentnum, entryname, entrynum))
			haserror = True
		elif entrynum in freeinodes:
			print("DIRECTORY INODE {} NAME {} UNALLOCATED INODE {}".format(parentnum, entryname, entrynum))
			haserror = True
		else:
			if entrynum in linkdict:
				linkdict[entrynum] = linkdict[entrynum] + 1
			else:
				linkdict[entrynum] = 1

			if entryname != "'..'" and entryname != "'.'":
				parentdict[entrynum] = parentnum

	for inode in inodes:
		inodenum = int(inode[1])
		linkcount = int(inode[6])
		if inodenum not in linkdict:
			if linkcount != 0:
				print("INODE {} HAS 0 LINKS BUT LINKCOUNT IS {}".format(inodenum, linkcount))
				haserror = True
		else:
			currcount = linkdict[inodenum]
			if linkcount != currcount:
				print("INODE {} HAS {} LINKS BUT LINKCOUNT IS {}".format(inodenum, currcount, linkcount))
				haserror = True
		
	for dirent in dirents:
		entrynum = int(dirent[3])
		entryname = dirent[6].rstrip()
		parentnum = int(dirent[1]) 
		if entryname == "'..'":
			grandparent = parentdict[parentnum]
			if entrynum != grandparent:
				print ("DIRECTORY INODE {} NAME {} LINK TO INODE {} SHOULD BE {}".format(parentnum, entryname, entrynum, grandparent))
				haserror = True
		elif entryname == "'.'":
			if entrynum != parentnum:
				print ("DIRECTORY INODE {} NAME {} LINK TO INODE {} SHOULD BE {}".format(parentnum, entryname, entrynum, parentnum))
				haserror = True

if __name__ == "__main__":
	if len(sys.argv) != 2:
		dump_error("Only 1 argument")
	if not os.path.isfile(sys.argv[1]):
		dump_error("File does not exist")
	
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
