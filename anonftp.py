#!/usr/bin/python

import ftplib
import argparse
import os
import binascii

#actually make the login attempt
def anonLogin(hostname):
    try:
        ftp = ftplib.FTP(hostname)
        email = binascii.b2a_hex(os.urandom(3)) + '@' + binascii.b2a_hex(os.urandom(3)) + '.com'
        ftp.login('anonymous', email)
        print "\n[*] " + str(hostname) + ': Anon FTP login succeeded!'
        ftp.quit()
        if ofile:
            ofile.write(hostname + "\n")
        return True
    except Exception, e:
        return False

#called when a list is provided then iterates through the list and call anonLogin()
def hitlist(list):
    if os.path.isfile(list):
        pass
    else: 
        print "List not found. Check path and try again!"
        exit(0)
    f = open(list, 'r')
    for line in f.readlines():
        line = line.strip('\n').strip('\r')
        anonLogin(line)

def main():
    #setup args
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--target', help="Check a single target IP")
    parser.add_argument('-l', '--list', help="Check all targets in a list. List should be one target IP per line")
    parser.add_argument('-o', '--outfile', help="Output found targets to a file")
    args = parser.parse_args()
    target = args.target
    list = args.list
    outfile = args.outfile
    
    #check if outfile exists and prompt for overwrite if so
    if outfile:
        if os.path.isfile(outfile):
            overwrite = raw_input("[!] File exists! Are you sure you want to continue? If you do the existing file will be overwritten! (y/n): ")
            if overwite == "y" or overwrite == "Y" or overwrite == "Yes":
                pass
            else:
                print "[!] Exiting now!"
                exit()
        #open the output file
        ofile = open(outfile, 'a')
    
    #
    if target == None and list == None:
        parser.print_help()
        print "\n[!] You must specify either a single target or a list of targets\n"
        exit(0)
    
    #check args and decide whether to handle a list or single ip then 
    #actually start the login attempts
    if list: hitlist(list)
    if target: anonLogin(target)
    
    #cleanup
    if ofile:
        ofile.close()
    
if __name__ == '__main__':
    main()
