#!/usr/bin/python
import re
import argparse

options = argparse.ArgumentParser()
options.add_argument("-i", "--input", help="Input file generated from WiFoFum")
options.add_argument("-o", "--output", default="output.txt", help="Output of open wifi names [default: output.txt]")
args = options.parse_args()

input_file = args.input
output_file = args.output

def cleanup(infile, outfile):
    f = open(infile, "r")
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

if __name__ == "__main__":
    if not input_file and output_file:
        print options.parse_args()
        exit(0)
    cleanup(input_file, output_file)
    find_open(output_file)

    
