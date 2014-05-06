#!/usr/bin/python

import zipfile
import argparse
import pyPdf  
from threading import Thread

def extractZip(zip, password):
    try:
        zfile = zipfile.ZipFile(zip)
        zfile.extractall(pwd=password)
        print '[+] Found password: ' + password + '\n'
    except:
        pass

def openPdf(pdfile, password):
    try:
        pdf = pyPdf.PdfFileReader(open(pdf))
        pdf.decrypt(password)  
        print '[+] Found password: ' + password + '\n'
    except:
        pass
    
def crackMain(function, file, dict):
    dictfile = open(dict, "r")
    for line in dictfile.readlines():
        password = line.strip("\n")
        t = Thread(target=function, args=(file, password))
        t.start() 
   
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', dest='file', required=True, help='The name of the file to crack (Required)')
    parser.add_argument('-d', '--dict', dest='dict', required=True, help='A dictionary to use for cracking (Required)')
    parser.add_argument('-z', '--zip', dest='zip', help='Crack a Zip file')
    parser.add_argument('-p', '--pdf', dest='pdf', help='Crack a PDF file') 
    args = parser.parse_args()
    if args.file is None or args.dict is None:
        print parser.usage
        print "\n [!] You must specify a file to crack and a dictionary! \n"
        exit(0)
    else:
        crackfile = args.file
        dfile = args.dict
        print dfile, crackfile
    if args.zip:
        crackMain('extractZip', crackfile, dfile)
    elif args.pdf:
        crackMain('openPdf', crackfile, dfile)
    else:
        print parser.usage
        print "\n [!] Please specify the file type to crack! \n"
        exit(0)

if __name__ == '__main__':
    main()