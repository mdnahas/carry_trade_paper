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

dur_list = [1, 2, 3, 5, 7, 10, 20]
for duration in dur_list:
    out_filename = os.path.join(outfile_directory, "govt" + str(duration) + ".csv")
    output_files[duration] = open(out_filename, "ab")


def process_file(filename):
    with open(filename, 'rb') as csv_infile:
        csv_reader = csv.reader(csv_infile)

        # read header, do not write one.
        header1 = csv_reader.next()

        if header1[1] != " ZC025YR":
            raise Exception("file had bad format!")
        
        for row in csv_reader:
            # date at index 0
            date_str = row[0]
            if date_str == "":
                continue
            date = datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

            for duration_local in dur_list:
                value_str = row[4*duration_local]
                if value_str == " na":
                    value_str = ""
                else:
                    value_str = str(100 * float(value_str))  # Convert to percent (SAD!)
                output_files[duration_local].write("CAD" + str(duration_local) + " govt," + str(date) + "," +  value_str + "\n")


process_file(infile_directory + "/yield_curves.csv")


# close files
for duration in output_files:
    output_files[ duration ].close()

