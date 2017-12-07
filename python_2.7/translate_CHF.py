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
        csv_reader = csv.reader(csv_infile, delimiter=";")  #quotechar='"'

        # read header, do not write one.
        header1 = csv_reader.next()
        header2 = csv_reader.next()
        header3 = csv_reader.next()
        header4 = csv_reader.next()

        for row in csv_reader:
            # date at index 0
            date = datetime.datetime.strptime(row[0], "%Y-%m-%d").date()
            ticker = row[1]
            value_str = row[2]

            if ticker[-1:] == "J":
                duration_local = int(ticker[:-1])
            elif ticker == "10J0":
                duration_local = 10
            else:
                continue

            if duration_local in output_files:
                output_files[duration_local].write("CHF" + str(duration_local) + " govt," + str(date) + "," +  value_str + "\n")


process_file(infile_directory + "/snb-data-rendoblid-en-selection-20170703_1430.csv")


# close files
for duration in output_files:
    output_files[ duration ].close()

