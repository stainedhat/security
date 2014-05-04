#!/usr/bin/python
import re
import os
import argparse
import textwrap
import getpass
import MySQLdb

#setup argparser
options = argparse.ArgumentParser(usage='%(prog)s [(-h, --help), (-db -u,-p,-s,-d,-t), (-o -a, -wpa, -wpa2, -wep, -open)] input_file.xml', formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent("[*] ParseFoFum parses android WiFoFum logs generated in XML format and either outputs the results to a file or stores it in a database. [*]"), epilog='''
Examples: 
*Output to files*
  # %(prog)s -o  wifofum.xml (Output to default files)
  # %(prog)s -o -open pwnd.txt -wep pwnd.txt wifofum.xml (Output wpa/wpa2 to default files and open/wep to pwnd.txt)
  # %(prog)s -o -a area1.txt wifofum.xml (All output goes into area1.txt)

*Output to database*
  # %(prog)s -db -s localhost -d wifofum -u username -p -t area1 wifofum.xml (Output to database named wifofum in table 'area1')''', conflict_handler='resolve')
#create subgroups
required = options.add_argument_group("Required", "The input file is required to be in .xml format")
output = options.add_argument_group("Output", "These options will direct where the program send the output")
dbopts = options.add_argument_group("Database options", "These options will allow you to set your database information. You should have mysql installed and a valid user and password already setup!")
outfiles = options.add_argument_group("Output Filenames", "These options will allow you to change the default output file names")
help = options.add_argument_group("Help")
#add arguments
#required input file
required.add_argument("input", help="Input file generated from WiFoFum")
#output args
output.add_argument("-o","--output", action="store_true", help="Output of parsed wifi log in text files wpa2.txt, wpa.txt, wep.txt, open.txt")
output.add_argument("-db", "--database", action="store_true", help="Output is put into a mysql database. Minimally, args -u and -p are required with this option.")
#databse options
dbopts.add_argument("-d", "--db-name", default="wifofum", help="Database name to store results in [default: %(default)s]")
dbopts.add_argument("-u", "--username", help="Database username. This is required to connect")
dbopts.add_argument("-p", "--password", action="store_true", help="Required to connect to the db. D0 NOT SUPPLY ON COMMAND LINE!! You will be prompted for the password when you use -p or --password")
dbopts.add_argument("-s", "--server", default="127.0.0.1", help="Database server address [default: %(default)s]")
dbopts.add_argument("-t", "--table", default="found", help="Database table name [default: %(default)s]")
#output file options
outfiles.add_argument("-a","--all", help="All results will be stored in this file.")
outfiles.add_argument("-wpa","--wpa", default="wpa.txt", help="Any results with security type of WPA will be stored in this file. [default: %(default)s]")
outfiles.add_argument("-wpa2","--wpa2", default="wpa2.txt", help="Any results with security type of WPA2 will be stored in this file. [default: %(default)s]")
outfiles.add_argument("-wep","--wep", default="wep.txt", help="Any results with security type of WEP will be stored in this file. [default: %(default)s]")
outfiles.add_argument("-open","--open", default="open.txt", help="Any results with no security will be stored in this file. [default: %(default)s]")
#help
help.add_argument("-h", "--help", action="help", help="Show this help message and exit")

args = options.parse_args()

#do some file checking and create an output directory
input_file = args.input

if args.output:
    if os.path.isfile(input_file):
        newdir = input_file.split(".")
        newdir = newdir[0]
        if os.path.isdir(newdir):
            while True:
                confirm = raw_input("\n[!] The directory where output will be generated already exists. If you continue you will append the current data to the existing files which may result in duplicate entries. Are you SURE you want to continue? (y/n): ")
                if confirm == "y" or confirm == "n":
                    break
            if confirm == "y":
                pass
            else:
                print "\nPlease rename your xml file or remove the existing directory before running this program again!"
        else:
            try:
                os.mkdir(newdir)
            except OSError, e:
                print e
                exit(1)

#setup args
tmpfile = "/tmp/parsefofum.tmp"
if args.database:
    db_name = args.db_name
    db_user = args.username
    if args.password:
        db_pass = getpass.getpass()
    db_host = args.server
    db_table = args.table
if args.output:
    if args.all:
        output_all = newdir+"/"+args.all
    else:
        output_all = args.all
    output_wpa = newdir+"/"+args.wpa
    output_wpa2 = newdir+"/"+args.wpa2
    output_wep = newdir+"/"+args.wep
    output_open = newdir+"/"+args.open

#cleanup the main file and put the data into a tmp file for processing
def cleanup(infile, tmpfile):
    try:
        f = open(infile, "r")
    except OSError, e:
        print "Error! %s - %s" % (e.filename, e.strerror)
        exit(1)
    c = open(tmpfile, "a")
    for line in f.readlines():
        wline = True
        line = line.strip("\n")
        if line == '<?xml version="1.0" standalone="yes"?>':
            wline = None
        line = line.strip(" ")
        if line == "</AP>":
            c.write(line+"\n")
            pass
        elif line == "<DocumentElement>" or line == "</DocumentElement>":
            pass
        else:
            if wline:
                c.write(line)
    c.close()
    f.close()

#write each block to file
def write_line(d, filename):
    f = open(filename, "a")
    f.write("====================================================================\n")
    f.write("[+] SSID: "+d["SSID"]+" | Security: "+d["Security"]+" | MAC: "+d["MAC"]+" | Type: "+d["Type"]+" | Channel: "+d["Channel"]+" | RSSI: "+d["RSSI"]+" | Longitude: "+d["Lon"]+" | Lattitude: "+d["Lat"]+" | Altitude: "+d["Altitude"]+" | First Seen: "+d["FirstSeen"]+" | Last Seen: "+d["LastSeen"]+" | HDOP: "+d["HDOP"]+"\n")
    f.write("====================================================================\n")
    f.close()

#process the dict for each line and insert it into the db or write to file
def parse_line(line):
    d = format_line(line)
    security = d["Security"]
    if args.database:
        pass
        #print "Put into database"
    elif args.output:
        if output_all:
            write_line(d, output_all)
        else:
            if security == "Open":
                write_line(d, output_open)
            if security == "WPA":
                write_line(d, output_wpa)
            if security == "WPA2":
                write_line(d, output_wpa2)
            if security == "WEP":
                write_line(d, output_wep)
        
#clean up each line and return a dict with each key/val for processing
def format_line(line):
    fmt = re.split(r"(<.*?>.*?<\/.*?>)", line)
    fmt = filter(None, fmt)
    fmt.remove("</AP>\n")
    fmt[0] = re.sub(r"<AP>", "", fmt[0])
    fmt[1] = re.sub(r"(<!\[CDATA\[|\]\]>)", "", fmt[1])
    data = {}
    for i in range(0,12):
        key = re.search(r"<.*?>", fmt[i])
        key = re.sub(r"(<|>)", "", key.group())
        value = re.search(r">.*<", fmt[i])
        value = re.sub(r"(>|<)", "", value.group())
        data[key] = value
    return data

#connect to the database
def db_conn(db_host, db_user, db_pass):
    try:
        conn = MySQLdb.connect(db_host, db_user, db_pass)
        db = conn.cursor()
        print "Connected..."
    except:
        print "Failed to connect to database. Check your username and password!"
#main
if __name__ == "__main__":
    if args.database is True: 
        if args.username is None or args.password is None:
            options.error("-db requires at least a username and password!")
            exit(1)
        db_conn(db_host, db_user, db_pass)
    cleanup(input_file, tmpfile)
    with open(tmpfile, "r") as f:
        for i in f:
            parse_line(i)
    try:
        os.remove(tmpfile)
    except OSError, e:
        print e
    
    print "\n[+] Parsing completed!\n"
    if args.output:
        print "[+] Check the output file(s) in %s\n" % (os.path.abspath(newdir))
    
    
