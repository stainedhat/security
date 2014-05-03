#!/usr/bin/python
import re
import argparse
import textwrap

#setup argparser
options = argparse.ArgumentParser(usage='%(prog)s [-h,-o,-d,-u,-p,-t] input', formatter_class=argparse.RawDescriptionHelpFormatter, description=textwrap.dedent("[*] ParseFoFum parses android WiFoFum logs generated in XML format and either outputs the results to a file or stores it in a database. [*]"), epilog='''
Examples: 
  %(prog)s -o output.txt wifofum.xml (Output to file)
  %(prog)s -d wifofum -u username -p pass -t area1 wifofum.xml (Output to database)''', conflict_handler='resolve')
#create subgroups
required = options.add_argument_group("Required", "The input file is required to be in .xml format")
output = options.add_argument_group("Output", "These options will direct where the program send the output")
help = options.add_argument_group("Help")
#add arguments
#required input file
required.add_argument("input", help="Input file generated from WiFoFum")
#output args
output.add_argument("-o","--output", default="output.txt", help="Output of parsed wifi log in text file [default: %(default)s]")
output.add_argument("-d", "--db-name", default="wifofum", help="Database name to store results in [default: %(default)s]")
output.add_argument("-u", "--user", default="wifofum", help="Database username [default: %(default)s]")
output.add_argument("-p", "--pass", default="wifofum", help="Database password [default: %(default)s]")
output.add_argument("-t", "--table", default="found", help="Database table name [default: %(default)s]")
#help
help.add_argument("-h", "--help", action="help", help="Show this help message and exit")

args = options.parse_args()

input_file = args.input
output_file = args.output

def cleanup(infile, outfile):
    try:
        f = open(infile, "r")
    except IOError, e:
        print e
        exit(1)
    c = open(outfile, "a")
    for line in f.readlines():
        line = line.strip("\n")
        line = line.strip(" ")
        if line == "</AP>":
            c.write(line+"\n")
            pass
        else:
            c.write(line)

def find_open(outfile):
    f = open(outfile, "r")
    for line in f.readlines():
        openwifi = re.findall("Open", line)
        if openwifi:
            ssid = re.search(r"(CDATA\[.*\]\])", line)
            ssid = re.search(r"\[.*?\]", ssid.group(), re.I)
	    ssid = re.sub(r"(\[|\])", "", ssid.group())
            print ssid

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
    if not input_file and output_file:
        print options.print_help()
        exit(1)
    cleanup(input_file, output_file)
    find_open(output_file)

    
