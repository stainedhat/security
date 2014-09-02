__author__ = 'blaze'

import sqlite3
import re
import platform
import os
import argparse


def getgooglesearches(places, outtype, ofile):
    conn = sqlite3.connect(places)
    cur = conn.cursor()
    cur.execute("SELECT url, datetime(last_visit_date/1000000, 'unixepoch') from moz_places;")
    if outtype == "console":
        print '[+] Google Searches '
        for row in cur:
            url = str(row[0])
            date = str(row[1])
            if 'google' in url.lower():
                q = re.findall(r'q=.*\&', url)
                if q:
                    query = q[0].split('&')[0]
                    query = query.replace('q=', '').replace('+', ' ')
                    print '[q] ' + date + ": " + query
    elif outtype == "file":
        f = open(ofile, 'a')
        f.write('[+] Google Searches \n')
        for row in cur:
            url = str(row[0])
            date = str(row[1])
            if 'google' in url.lower():
                q = re.findall(r'q=.*\&', url)
                if q:
                    query = q[0].split('&')[0]
                    query = query.replace('q=', '').replace('+', ' ')
                    f.write('[q] %s: %s \n' % (date, query))
        f.close()


def getvalidcookies(cookiefile, outtype, ofile):
    conn = sqlite3.connect(cookiefile)
    cur = conn.cursor()
    cur.execute("SELECT basedomain, name, value, datetime(creationTime/1000000, 'unixepoch'), "
                "datetime(expiry, 'unixepoch') FROM moz_cookies WHERE datetime(expiry, 'unixepoch') > datetime();")
    if outtype == "console":
        print '[!] Currently Valid Cookies '
        for row in cur:
            print '[+] Cookie Found'
            print '\tDomain: ', str(row[0])
            print '\tName: ', str(row[1])
            print '\tValue: ', str(row[2])
            print '\tCreation Date: ', str(row[3])
            print '\tExpiration Date: ', str(row[4])
    elif outtype == "file":
        f = open(ofile, 'a')
        f.write('[!] Currently Valid Cookies \n')
        for row in cur:
            f.write('[+] Cookie Found \n')
            f.write('\tDomain: %s \n' % str(row[0]))
            f.write('\tName: %s \n' % str(row[1]))
            f.write('\tValue: %s \n' % str(row[2]))
            f.write('\tCreation Date: %s \n' % str(row[3]))
            f.write('\tExpiration Date: %s \n' % str(row[4]))
        f.close()


def getformhistory(formfile, outtype, ofile):
    conn = sqlite3.connect(formfile)
    cur = conn.cursor()
    cur.execute("SELECT fieldname, value, timesUsed, datetime(lastUsed/1000000, 'unixepoch') from moz_formhistory;")
    if outtype == "console":
        print '[!] Saved Form Data '
        gsearches = []
        for row in cur:
            if 'q' in row or 'as_q' in row:
                gsearches.append(str(row[1]))
            else:
                print '[+] Saved form data found '
                print '\tName: ', str(row[0])
                print '\tValue: ', str(row[1])
                print '\tTimes Used: ', str(row[2])
                print '\tLast Used: ', str(row[3])
        if len(gsearches) > 0:
            print "[+] Google searches found"
            for search in gsearches:
                print "Search term: ", search
    elif outtype == "file":
        f = open(ofile, 'a')
        f.write('[!] Saved Form Data \n')
        gsearches = []
        for row in cur:
            if 'q' in row or 'as_q' in row:
                gsearches.append(str(row[1]))
            else:
                f.write('[+] Saved form data found \n')
                f.write('\tName: %s \n' % str(row[0]))
                f.write('\tValue: %s \n' % str(row[1]))
                f.write('\tTimes Used: %s \n' % str(row[2]))
                f.write('\tLast Used: %s \n' % str(row[3]))
        if len(gsearches) > 0:
            f.write("[+] Google searches found \n")
            for search in gsearches:
                f.write("\tSearch term: %s \n" % search)
        f.close()


def gethistory(places, outtype, ofile):
    conn = sqlite3.connect(places)
    cur = conn.cursor()
    cur.execute("SELECT url, title, visit_count, datetime(last_visit_date/1000000, 'unixepoch') from moz_places;")
    if outtype == "console":
        print '[!] Browser History '
        for row in cur:
            title = u'%s' % row[1]
            url = u'%s' % row[0]
            numvisits = u'%s' % row[2]
            lastvisit = u'%s' % row[3]
            print '[+] Page title: ', title.encode('utf8')
            print '\tURL: ', url.encode('utf8')
            print '\tTimes visited: ' + numvisits + "\t Last visited: " + lastvisit
    elif outtype == "file":
        f = open(ofile, 'a')
        f.write('[!] Browser History \n')
        for row in cur:
            title = u'%s' % row[1]
            url = u'%s' % row[0]
            numvisits = u'%s' % row[2]
            lastvisit = u'%s' % row[3]
            f.write('[+] Page title: %s \n' % title.encode('utf8'))
            f.write('\tURL: %s \n' % url.encode('utf8'))
            f.write('\tTimes visited: %s \t Last Visited: %s \n' % (numvisits.encode('utf8'), lastvisit.encode('utf8')))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    main = parser.add_argument_group('Extraction Options')
    main.add_argument('-u', '--urls', dest='urls', action='store_true', help='Extract recent URL browsing history')
    main.add_argument('-g', '--google', dest='google', action='store_true',
                      help='Extract recent google searches from history')
    main.add_argument('-c', '--cookies', dest='cookies', action='store_true',
                      help='Extract non-expired cookies from current sessions')
    main.add_argument('-f', '--forms', dest='forms', action='store_true', help='Extract recent stored forms values')
    out = parser.add_argument_group('Output Options')
    out.add_argument('-o', '--output', dest='output', help='Specify the name of the text file to output data into')
    #output.add_argument('-d', '--db', dest='db', default='firesnoop.sqlite', help='Store output in sqlite db '
                                                                       #'[Default: firesnoop.sqlite]')
    profile = parser.add_argument_group('Profile Options')
    profile.add_argument('-p', '--profile', dest='profile', help='Choose a specific profile to target '
                                                 '[Default: All current user profiles]')

    #parse args
    args = parser.parse_args()
    #assign vars from args
    urls = args.urls
    google = args.google
    cookies = args.cookies
    forms = args.forms
    outfile = args.output
    profile = args.profile

    #Check outfile
    if outfile:
        output = "file"
    else:
        output = "console"
        outfile = ""

    #Make sure at least one option is specified
    if not urls and not google and not cookies and not forms:
        parser.print_help()
        print "[!] Error, you must specify at least one Extraction Option!"
        exit(0)

    #determine OS and appropriate paths for mozilla profiles
    systemos = platform.system()
    if systemos == 'Windows':
        if profile:
            if os.path.exists(profile):
                placesdb = os.path.join(profile, 'places.sqlite')
                cookiesdb = os.path.join(profile, 'cookies.sqlite')
                formsdb = os.path.join(profile, 'formhistory.sqlite')
                if outfile:
                    out = open(outfile, 'a')
                    out.write("=" * 25)
                    out.write("Gathering data on profile %s...\n" % profile)
                    out.close()
                if urls:
                    gethistory(placesdb, output, outfile)
                if cookies:
                    getvalidcookies(cookiesdb, output, outfile)
                if google:
                    getgooglesearches(placesdb, output, outfile)
                if forms:
                    getformhistory(formsdb, output, outfile)
                if outfile:
                    out = open(outfile, 'a')
                    out.write("=" * 25)
                    out.close()
            else:
                print "[!] Error! The profile you specified does not exist! "
                print "[!] Specify the entire path of the profile folder!"
                exit(1)
        else:
            profiles = {}
            exclude = ['All Users', 'Default', 'Default User', 'desktop.ini', 'Public']
            users = os.listdir('C:\\Users')
            for user in users:
                if user not in exclude:
                    path = os.path.join('C:\\', 'Users', user, 'AppData', 'Roaming', 'Mozilla', 'Firefox', 'Profiles')
                    if os.path.exists(path):
                        dirs = os.listdir(path)
                        for d in dirs:
                            profiles[d] = user
            for p in profiles:
                user = profiles[p]
                path = os.path.join('C:\\', 'Users', user, 'AppData', 'Roaming', 'Mozilla', 'Firefox', 'Profiles', p)
                if outfile:
                    out = open(outfile, 'a')
                    out.write("=" * 25)
                    out.write("Gathering data on %s from profile %s...\n" % (user, p))
                    out.close()
                print "Gathering data on %s from profile %s..." % (user, p)
                placesdb = os.path.join(path, 'places.sqlite')
                cookiesdb = os.path.join(path, 'cookies.sqlite')
                formsdb = os.path.join(path, 'formhistory.sqlite')
                if urls:
                    gethistory(placesdb, output, outfile)
                if cookies:
                    getvalidcookies(cookiesdb, output, outfile)
                if google:
                    getgooglesearches(placesdb, output, outfile)
                if forms:
                    getformhistory(formsdb, output, outfile)
                if outfile:
                    out = open(outfile, 'a')
                    out.write("=" * 25)
                    out.close()

    if systemos == 'Linux':
        profiles = {}
        exclude = ['.ecryptfs']
        excludedirs = ['Crash Reports', 'profiles.ini']
        users = os.listdir('/home/')
        for user in users:
            if user not in exclude:
                path = os.path.join('/', 'home', user, '.mozilla', 'firefox')
                if os.path.exists(path):
                    dirs = os.listdir(path)
                    for d in dirs:
                        if d not in excludedirs:
                            profiles[d] = user
        for p in profiles:
            user = profiles[p]
            path = os.path.join('/', 'home', user, '.mozilla', 'firefox', p)
            if outfile:
                    out = open(outfile, 'a')
                    out.write("=" * 25)
                    out.write("Gathering data on %s from profile %s...\n" % (user, p))
                    out.close()
            print "Gathering data on %s from profile %s..." % (user, p)
            placesdb = os.path.join(path, 'places.sqlite')
            cookiesdb = os.path.join(path, 'cookies.sqlite')
            formsdb = os.path.join(path, 'formhistory.sqlite')
            if urls:
                gethistory(placesdb, output, outfile)
            if cookies:
                getvalidcookies(cookiesdb, output, outfile)
            if google:
                getgooglesearches(placesdb, output, outfile)
            if forms:
                getformhistory(formsdb, output, outfile)
            if outfile:
                    out = open(outfile, 'a')
                    out.write("=" * 25)
                    out.close()