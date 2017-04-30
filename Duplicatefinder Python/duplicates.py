#!/usr/local/bin/python3
#python 3.6
#Berkay Özerbay
#2016400270

import subprocess
import argparse
import hashlib
import sys
import pwd
import os
import re


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


def hash_file(filename):
    # return hash of the file by reading it contents

    BLOCKSIZE = 65536
    hasher = hashlib.sha256()
    with open(filename, 'rb') as afile:
        buf = afile.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = afile.read(BLOCKSIZE)

    return hasher.hexdigest()





def gethash(string):
    # returns hash of given string, used for getting hash of directory
    hash_object = hashlib.sha256(string.encode("utf-8"))
    return hash_object.hexdigest()




def findDuplicates(adict, alist):  # returns a list of duplicates

    duplist = list()  # will be returned
    for i in range(len(alist) - 1):
        k = i + 1

        if (alist[i] not in duplist and (pattern == "None" or re.search(pattern, alist[i].split("/")[-1]))):
            # if the file/dir were not already in duplist or the matching is succesfull

            tempduplist = list()
            # set of duplicates, it will be added if its lenght exceed 1

            tempduplist.append(alist[i])
            for filename in alist[k:]:
                # compare other file/dirs with alist[i]

                if (adict[filename] == adict[alist[i]] and (
                        pattern == "None" or re.search(pattern, filename.split("/")[-1])) and filename != alist[i]):
                    # if their hashs are same and filename match with pattern, append it
                    tempduplist.append(filename)

            if (len(tempduplist) > 1):
                # if set of duplicates is greater than 1, add it to duplist
                tempduplist.sort()
                duplist += tempduplist

    return duplist


def makeFullName(dirs):
    for dname in dirs:
        if not os.path.isabs(dname):
            loc = dirs.index(dname)
            dname = cwd + '/' + dname
            dirs[loc] = dname


def DoCommands(duplicates):
    for dup in duplicates:

        cmd = args.c + " " + '"' + dup + '"'
        os.system(cmd)



cwd = os.getcwd()  # current directory(full path)

parser = argparse.ArgumentParser(description='project.')

group1 = parser.add_mutually_exclusive_group(required=False)
group1.add_argument('-c', type=str)
group1.add_argument('-p', action="store_true",default=True)

group2 = parser.add_mutually_exclusive_group()
group2.add_argument('-d', action='store_false', dest='which')
group2.add_argument('-f', action='store_true', dest='which')
parser.set_defaults(which=True)

parser.add_argument('optarg', nargs='?')
parser.add_argument('dirnames', nargs='*')

args = parser.parse_args()

dirs = list()  # it will contain name of directory argument
pattern = str()  # pattern which will be given to re.search as argument for patttern matching
if args.optarg is not None:

    # if optarg exists
    if args.optarg.startswith('"') and args.optarg.endswith('"'):
        # if optarg is pattern
        pattern = args.optarg[1:-1]
    else:
        # if optarg is not pattern ,so append it to dirs(directory arguments)
        dirs.append(args.optarg)
        pattern = "None"
else:
    pattern = "None"

if len(args.dirnames) == 0:
    if len(dirs) == 0:
        # if there is no optarg(patten) and dir argument, dirs contain only current directory
        dirs.append(cwd)

else:
    # else if arg.dirnames exist add it to dirs
    dirs = dirs + args.dirnames

"""
print(args.optarg)
print(pattern)
print(dirs)
print(43)
print(args.which)
"""
# if some names are not fullpath, they are converted to fullpaths
makeFullName(dirs)

flist = list()  # will be list for all files
alldirlist = list()
dirlist = list(dirs)  # a copy of directory argument list
dlist = list(dirs)  # a copy of directory argument list, will be list for all directories

hdict = {}  # hash dictionary for files
hdict2 = {}  # hash dictionary for directories

for rootDir in dirlist:
    hashlist = []

    if rootDir in hdict2:
        continue

    for dirName, subdirList, fileList in os.walk(rootDir, topdown=False):
        dirhashstr = ""
        # empty string, if directory is empty,its hash will be hash of empty string

        if dirName in hdict2:
            continue

        # bottomup walking because it will first look at leaf files and find their hash
        # then from these hashes, the hash of the directory, which these file exist, will be found
        hashlist = []

        for fname in fileList:  # look at all files in a directory
            temp = dirName + '/' + fname  # temp is fullpath
            hdict[temp] = hash_file(temp)  # insert the hash of this file
            hashlist.append(hdict[temp])  # also add it to hashlist
            flist.append(temp)
        for subdir in subdirList:  # look at all subdir if exist
            temp = dirName + '/' + subdir  # temp is fullpath
            hashlist.append(hdict2[temp])
            if temp not in dlist:
                dlist.append(temp)

        # after all, hashlist contain all hashes of files and subdirs in a specific directory
        # they will be sorted,so the order become unimportant
        hashlist.sort()
        for string in hashlist:
            dirhashstr += string  # convert it a single string
        hdict2[dirName] = gethash(dirhashstr)

        # find and insert the hash of this directory

if args.which == True:  # if duplicates of files should be found
    duplist = findDuplicates(hdict, flist)
else:  # else duplicates of directories should be found
    duplist = findDuplicates(hdict2, dlist)

# merge file and directory dictionaries
fulldict = merge_two_dicts(hdict, hdict2)

if args.c is  None:  # print statement
    i = 0
    while i < len(duplist):
        tempdupset = []  # stores a set of duplicates in it
        temp = duplist[i]
        tempdupset.append(temp)
        i += 1
        while i < len(duplist) and fulldict[temp] == fulldict[duplist[i]]:
            tempdupset.append(duplist[i])
            i += 1
            # if lenght of the set of duplicates is more than 0
            # some duplicates cannot pass the pattern test
            # that's why this algorith is needed

        if len(tempdupset) > 1:
            for dup in tempdupset:
                print(dup)
            print("")
else:  # command statement
    DoCommands(duplist)
