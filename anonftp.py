#!/usr/bin/python

import ftplib
import argparse
import os
import binascii
from multiprocessing import *

#actually make the login attempt
def anonLogin(ip, timeout):
    try:
        ftp = ftplib.FTP()
        ftp.connect(ip, 21, timeout)
        email = binascii.b2a_hex(os.urandom(3)) + '@' + binascii.b2a_hex(os.urandom(3)) + '.com'
        ftp.login('anonymous', email)
        print "[*] " + str(ip) + ' : Anonymous FTP login succeeded!'
        success = ip + "\n"
        ftp.quit()
        return success
    except Exception, e:
        if verbose:
            print ip, e
        else:
            pass
        #print ip, e

def worker(ip_queue, found_queue, timeout):
    try:
        for ip in iter(ip_queue.get, 'STOP'):
            result = anonLogin(ip, timeout)
            if result:
                found_queue.put(result)
    except:
        pass

#called when a list is provided then iterates through the list and call anonLogin()
def hitlist(list, timeout, threads):
    #setup queues and threads
    ip_queue = Queue()
    found_queue = Queue()
    global processes
    processes = []
    
    #build ip_queue
    if os.path.isfile(list):
        f = open(list, 'r')
        for line in f.readlines():
            line = line.strip('\n').strip('\r')
            ip_queue.put(line)
        f.close()
    else: 
        print "List '%s' not found. Check path and try again!" % list
        exit(0)
    
    #start threads
    for x in xrange(threads):
        p = Process(target=worker, args=(ip_queue, found_queue, timeout))
        p.start()
        processes.append(p)
        ip_queue.put('STOP')
    
    #wait for processes to complete and put end tag into found_queue
    for p in processes:
        p.join()
    found_queue.put('STOP')
    
    #create output file
    if outfile:
        ofile = open(outfile, 'a')
        for found in iter(found_queue.get, 'STOP'):
            ofile.write(found)
        ofile.close()
        

def main():
    #setup args
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip', help="Check a single target IP")
    parser.add_argument('-l', '--list', help="Check all targets in a list. List should be one target IP per line")
    parser.add_argument('-o', '--outfile', help="Output found targets to a file")
    parser.add_argument('-t', '--threads', default=5, type=int, help="Number of threads to use for scanning [default: 5]")
    parser.add_argument('-n', '--timeout', default=10, type=int, help="Check a single target IP [default: 10]")
    parser.add_argument('-v', '--verbose', action='store_true', help="Verbose output which includes errors and failure messages")
    args = parser.parse_args()
    ip = args.ip
    list = args.list
    threads = args.threads
    timeout = args.timeout
    global outfile
    global verbose
    outfile = args.outfile
    verbose = args.verbose
    if ip:
        verbose = True #set this so that a single IP scan has an output
    
    #check if outfile exists and prompt for overwrite if so
    if outfile:
        if os.path.isfile(outfile):
            overwrite = raw_input('''[!] File exists! Are you sure you want to continue? 
            If you do the existing file will have the new data appended to it! (y/n): ''')
            if overwrite == "y" or overwrite == "Y" or overwrite == "Yes":
                pass
            else:
                print "[!] Exiting now!"
                exit()
    
    #check to make sure user has specified target(s)
    if ip == None and list == None:
        parser.print_help()
        print "\n[!] You must specify either a single target or a list of targets\n"
        exit(0)
    
    #check args and decide whether to handle a list or single ip then 
    #actually start the login attempts
    print "[!] Testing Anonymous FTP Login.."
    if list: hitlist(list, timeout, threads)
    if ip: anonLogin(ip, timeout)
    
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "\nKeyboard interrupt caught! Exiting now....."
        exit(0)