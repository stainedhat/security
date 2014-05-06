#!/usr/bin/python

import zipfile
import argparse
from threading import Thread


def extractZip(zip, password):
    try:
        zip.extractall(pwd=password)
        print '[+] Found password ' + password + '\n'
    except:
        pass
    
def crackZip(zfile, dfile):
    zip = zipfile.ZipFile(zfile)
    dict = open(dfile, "r")
    for line in dict.readlines():
        password = line.strip("\n")
        t = Thread(target=extractZip, args=(zip, password))
        t.start()
    
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', dest='file', help='The name of the file to crack')
    parser.add_argument('-d', '--dict', dest='dict', help='A dictionary to use for cracking')
    parser.add_argument('-z', '--zip', dest='zip', help='Crack a Zip file')    
    args = parser.parse_args()
    if args.file is None or args.dict is None:
        print parser.usage
        exit(0)
    else:
        crackfile = args.file
        dfile = args.dict
        print dfile, crackfile
    if args.zip:
        crackZip(crackfile, dfile)

if __name__ == '__main__':
    main()