#!/usr/bin/python
import re
import os
import argparse
import textwrap

#setup argparser
options = argparse.ArgumentParser(usage='%(prog)s [(-h, --help), (-db -u,-p,-s,-d,-t), (-o -a, -wpa, -wpa2, -wep, -open)] input_file.xml', formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent("[*] ParseFoFum parses android WiFoFum logs generated in XML format and either outputs the results to a file or stores it in a database. [*]"), epilog='''
Examples: 
*Output to files*
  # %(prog)s -o  wifofum.xml (Output to default files)
  # %(prog)s -o -open pwnd.txt -wep pwnd.txt wifofum.xml (Output wpa/wpa2 to default files and open/wep to pwnd.txt)
  # %(prog)s -o -a area1.txt wifofum.xml (All output goes into area1.txt)
*Output to database*
  # %(prog)s -db -s localhost -d wifofum -u username -p pass -t area1 wifofum.xml (Output to database named wifofum in table 'area1')''', conflict_handler='resolve')
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
dbopts.add_argument("-u", "--username", help="Database username")
dbopts.add_argument("-p", "--password", help="Database password")
dbopts.add_argument("-s", "--server", default="localhost", help="Database server address [default: %(default)s]")
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

input_file = args.input
tmpfile = "/tmp/parsefofum.tmp"
db_name = args.db_name
db_user = args.username
db_pass = args.password
db_host = args.server
db_table = args.table
output_all = args.all
output_wpa = args.wpa
output_wpa2 = args.wpa2
output_wep = args.wep
output_open = args.open

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

def write_line(d, filename):
    f = open(filename, "a")
    f.write("====================================================================\n")
    f.write("[+] SSID: "+d["SSID"]+" | Security: "+d["Security"]+" | MAC: "+d["MAC"]+" | Type: "+d["Type"]+" | Channel: "+d["Channel"]+" | RSSI: "+d["RSSI"]+" | Longitude: "+d["Lon"]+" | Lattitude: "+d["Lat"]+" | Altitude: "+d["Altitude"]+" | First Seen: "+d["FirstSeen"]+" | Last Seen: "+d["LastSeen"]+" | HDOP: "+d["HDOP"]+"\n")
    f.write("====================================================================\n")
    f.close()

def parse_line(line):
    d = format_line(line)
    security = d["Security"]
    if args.database == "True":
        print "Put into database"
    elif output_all:
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

if __name__ == "__main__":
    if args.database is True: 
        if args.username is None or args.password is None:
            options.error("-db requires at least a username and password!")
            exit(1)
    cleanup(input_file, tmpfile)
    with open(tmpfile, "r") as f:
        for i in f:
            parse_line(i)
    try:
        os.remove(tmpfile)
    except OSError, e:
        print e
    
    
