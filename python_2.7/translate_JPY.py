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


# maps duration AS STRING PLUS Y to file
output_files = dict()

for duration in [1, 2, 3, 5, 7, 10, 20]:
    out_filename = os.path.join(outfile_directory, "govt" + str(duration) + ".csv")
    output_files[str(duration) + "Y"] = open(out_filename, "ab")


def process_file(filename):
    with open(filename, 'rb') as csv_infile:
        csv_reader = csv.reader(csv_infile)

        # read header, do not write one.
        header1 = csv_reader.next()
        header2 = csv_reader.next()

        # Header 2 has durations as 1Y, 2Y, ...
                
        for row in csv_reader:
            # date at index 0
            date = datetime.datetime.strptime(row[0], "%Y/%m/%d").date()

            for i in range(1, min(len(header2), len(row))):
                if header2[i] in output_files:
                    duration_str = header2[i][:-1]
                    value_str = row[i]

                    if value_str == "-":
                        value_str = ""
            
                    output_files[header2[i]].write("JPY" + duration_str + " govt," + str(date) + "," +  value_str + "\n")



process_file(infile_directory + "/Japanese_Ministry_of_Finance_yield_curve.csv")


# close files
for duration in output_files:
    output_files[ duration ].close()

