#!/usr/bin/python

# division returns float always; use // for integer division
from __future__ import division
from __future__ import print_function

import csv
import sys
import os
import math
import datetime
import calendar
from sets import Set
import unittest


# Reads Treasury files and appends to output in data/govt

if len(sys.argv) != 3:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 3.  Program infile_directory output_directory")
infile_directory = sys.argv[1]
outfile_directory = sys.argv[2]


# maps duration AS INT to file
output_files = dict()

for duration in [1, 2, 3, 5, 7, 10, 20]:
    out_filename = os.path.join(outfile_directory, "govt" + str(duration) + ".csv")
    output_files[duration] = open(out_filename, "ab")


def process_file(filename):
    with open(filename, 'rb') as csv_infile:
        csv_reader = csv.reader(csv_infile)

        # read header, do not write one.
        header1 = csv_reader.next()
        header2 = csv_reader.next()
        header3 = csv_reader.next()
        header4 = csv_reader.next()
        header5 = csv_reader.next()

        # Header 5 has the template, for which columns are what years.
        old_data = (header2[6] == "1 year" and header2[9] == "10 year")
        new_data = (header2[1] == "1 year" and header2[4] == "10 year")
        
        if not old_data and not new_data:
            raise Exception("file had bad format!")

        if old_data:
            offset = 6
        else:
            offset = 1
        
        for row in csv_reader:
            # date at index 0
            date_str = row[0]
            if date_str == "":
                continue
            date = datetime.datetime.strptime(date_str, "%d %b %Y").date()

            if row[offset+0] == "" and row[offset+1] == "" and row[offset+2] == "" and row[offset+03] == "":
                continue
            
            for i in range(0,4):
                value_str = row[offset + i]
                duration_local = [1, 2, 5, 10][i]
                output_files[duration_local].write("NZD" + str(duration_local) + " govt," + str(date) + "," +  value_str + "\n")


process_file(infile_directory + "/hb2-daily-1985-2013.csv")
process_file(infile_directory + "/hb2-daily-close.csv")


# close files
for duration in output_files:
    output_files[ duration ].close()

