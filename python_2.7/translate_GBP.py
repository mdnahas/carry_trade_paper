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


# maps duration AS FLOAT to file
output_files = dict()

for duration in [1, 2, 3, 5, 7, 10, 20]:
    out_filename = os.path.join(outfile_directory, "govt" + str(duration) + ".csv")
    output_files[float(duration)] = open(out_filename, "ab")


def process_file(filename):
    with open(filename, 'rb') as csv_infile:
        csv_reader = csv.reader(csv_infile)

        # read header, do not write one.
        header1 = csv_reader.next()
        header2 = csv_reader.next()
        header3 = csv_reader.next()
        header4 = csv_reader.next()
        header5 = csv_reader.next()

        # Header 4 has the template, for which columns are what years.
        
        for row in csv_reader:
            # date at index 0
            date = datetime.datetime.strptime(row[0], "%d %b %y").date()

            for i in range(1, min(len(header4), len(row))):
                if float(header4[i]) in output_files:
                    duration_localscope = int(float(header4[i]))
                    value_str = row[i]
            
                    output_files[float(duration_localscope)].write("GBP" + str(duration_localscope) + " govt," + str(date) + "," +  value_str + "\n")



process_file(infile_directory + "/uknom16_mdaily.csv")
process_file(infile_directory + "/uknom05_mdaily.csv")
# data from 2000 to 2004
process_file(infile_directory + "/uknom0004.csv")
# data from 1995 to 1999
process_file(infile_directory + "/uknom9599.csv")


# close files
for duration in output_files:
    output_files[ duration ].close()

