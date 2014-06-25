#!/usr/bin/python

################################################################
# Feel free to copy and use this code or share it with others. #
# Do not charge for it and if you re-use it please just link   #
# back here. Thanks! Johnny_b14z3                              #
################################################################

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
dbopts.add_argument("-y", "--yes", action="store_true", help="Automatically update all existing db entries")
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
    if args.password == True:
        db_pass = getpass.getpass()
    else:
        db_pass = args.password
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
    f.write("[+] SSID: "+d["SSID"]+" | Security: "+d["Security"]+" | MAC: "+d["MAC"]+" | Type: "+d["Type"]+" | Channel: "+d["Channel"]+" | RSSI: "+d["RSSI"]+" | Longitude: "+d["Lon"]+" | Latitude: "+d["Lat"]+" | Altitude: "+d["Altitude"]+" | First Seen: "+d["FirstSeen"]+" | Last Seen: "+d["LastSeen"]+" | HDOP: "+d["HDOP"]+"\n")
    f.write("====================================================================\n")
    f.close()

#process the dict for each line and insert it into the db or write to file
def parse_line(line):
    d = format_line(line)
    security = d["Security"]
    if args.database:
        db_insert(d, db_name, db_table)
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

#create db and table if not exists
def create_db(dbname, tblname):
    checkdb = "SELECT schema_name FROM information_schema.schemata WHERE schema_name = '%s';" % (dbname)
    #try:
    db.execute(checkdb)
    data = db.fetchone()
    if data:
        print "Database %s exists. Attempting to insert into it!\n" % (dbname)
    else:
        try:
            createdb = "CREATE DATABASE IF NOT EXISTS %s" % (dbname)
            db.execute(createdb)
        except:
            print "failed to create database. Check your settings and permissions and try again!"
            db.close()
            exit(1)
    #check if table exists
    tablechk = "SHOW TABLES LIKE '%s';" % (tblname)
    try:
        usedb = "USE %s;" % (dbname)
        db.execute(usedb)
        do_chk = db.execute(tablechk)
        if do_chk:
            print "[!] Table exists.. attempting to insert data. If it fails you should specify a different table name."
        else:
            createtbl = """CREATE TABLE %s (id INT NOT NULL AUTO_INCREMENT, ssid VARCHAR(255) NOT NULL, security VARCHAR(4) NOT NULL, mac VARCHAR(17) NOT NULL, type VARCHAR(50) NOT NULL, channel TINYINT NOT NULL, rssi VARCHAR(5) NOT NULL, latitude VARCHAR(25) NOT NULL, longitude VARCHAR(25) NOT NULL, altitude VARCHAR(7) NOT NULL, first_seen VARCHAR(28) NOT NULL, last_seen VARCHAR(28) NOT NULL, hdop VARCHAR(4) NOT NULL, UNIQUE (mac), PRIMARY KEY (id))""" % (tblname)
            db.execute(createtbl)
            conn.commit()
    except:
        "Failed to verify or create the table! Exiting... "
        exit(1)

#function to insert lines into the db. input is a dict from format_line
def db_insert(d, dbname, tblname):
    usedb = "USE %s;" % (dbname)
    db.execute(usedb)
    for key in d.keys():
        d[key] = re.sub(r"[%_']", "", d[key]) #cleanup some sql chars
    sql = ''' INSERT INTO %s (ssid, security, mac, type, channel, rssi, latitude, longitude, altitude, first_seen, last_seen, hdop) VALUES ('%s', '%s', '%s', '%s', %s, '%s', '%s', '%s', '%s', '%s', '%s', '%s')''' % (tblname, d["SSID"], d["Security"], d["MAC"], d["Type"], int(d["Channel"]), d["RSSI"], d["Lon"], d["Lat"], d["Altitude"], d["FirstSeen"], d["LastSeen"], d["HDOP"])
    try:
        db.execute(sql)
        conn.commit()
    except MySQLdb.ProgrammingError, e:
        conn.rollback()
        print e
        print "\n[!] Error inserting into the database! Exiting now...\n"
        exit(1)
    except MySQLdb.IntegrityError, e:
        detect_dup = re.search(r"Duplicate entry", e[1])
        if detect_dup:
            if args.yes:
                update = "UPDATE %s SET ssid='%s', security = '%s', type = '%s', channel = %d, rssi = '%s', longitude = '%s', latitude = '%s', altitude = '%s', first_seen = '%s', last_seen = '%s', hdop = '%s' where mac = '%s'" % (tblname, d["SSID"], d["Security"], d["Type"], int(d["Channel"]), d["RSSI"], d["Lon"], d["Lat"], d["Altitude"], d["FirstSeen"], d["LastSeen"], d["HDOP"], d["MAC"])
            else:
                print "\n[!] Error inserting into the database! This MAC address already exists!"
                print "SSID: %s | MAC: %s" % (d["SSID"], d["MAC"])
                while True:
                    confirm = raw_input("Would you like to update the entry? (y/n): ")
                    if confirm == "y" or confirm == "n":
                        break
                if confirm == "y":
                    update = "UPDATE %s SET ssid='%s', security = '%s', type = '%s', channel = %d, rssi = '%s', longitude = '%s', latitude = '%s', altitude = '%s', first_seen = '%s', last_seen = '%s', hdop = '%s' where mac = '%s'" % (tblname, d["SSID"], d["Security"], d["Type"], int(d["Channel"]), d["RSSI"], d["Lon"], d["Lat"], d["Altitude"], d["FirstSeen"], d["LastSeen"], d["HDOP"], d["MAC"])
                else:
                    print e + "\n [!] Exiting..."
                    exit(0)
            try:
                db.execute(update)
                conn.commit()
            except:
                print "[!] Error updating database entry!"

#main
if __name__ == "__main__":
    if args.database is True: 
        if args.username is None or args.password is None:
            options.error("-db requires at least a username and password!")
            exit(1)

        try:
            conn = MySQLdb.connect(db_host, db_user, db_pass)
            db = conn.cursor()
            print "\n[+] Connected to the database..."
        except:
            print "Failed to connect to database. Check your username and password!"
            exit(1)
        create_db(db_name, db_table)
#start processing
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
    elif args.database:
        print "[+] Data has been entered into the %s database in a table named %s \n" % (db_name, db_table)
        db.close()
    
    
