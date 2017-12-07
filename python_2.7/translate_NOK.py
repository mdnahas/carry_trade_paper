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

        # DATES,FOLIO.NOM,RESERVE.NOM,DLAAN.NOM,STATSVKL.3M.EFF,STATSVKL.6M.EFF,STATSVKL.9M.EFF,STATSVKL.12M.EFF,STATSOBL.3Y.EFF,STATSOBL.5Y.EFF,STATSOBL.10Y.EFF,NOWA.RATE,NOWA.VOLUME,NOWA.QUALIFIER
        if header1[7] != "STATSVKL.12M.EFF" or header1[10] != "STATSOBL.10Y.EFF":
            raise Exception("bad file format!")
        
        for row in csv_reader:
            if len(row) < 11:    # last line is empty
                continue
            
            # date at index 0
            date = datetime.datetime.strptime(row[0], "%d-%b-%y").date()

            value1_str = row[7]
            if value1_str[0] == "N":
                value1_str = ""
            output_files[ 1 ].write("NOK1 govt," + str(date) + "," +  value1_str + "\n")

            value3_str = row[8]
            if value3_str[0] == "N":
                value3_str = ""
            output_files[ 3 ].write("NOK3 govt," + str(date) + "," +  value3_str + "\n")

            value5_str = row[9]
            if value5_str[0] == "N":
                value5_str = ""
            output_files[ 5 ].write("NOK5 govt," + str(date) + "," +  value5_str + "\n")

            value10_str = row[10]
            if value10_str[0] == "N":
                value10_str = ""
            output_files[ 10 ].write("NOK10 govt," + str(date) + "," +  value10_str + "\n")

process_file(infile_directory + "/daily_bond_yields.csv")


# close files
for duration in output_files:
    output_files[ duration ].close()

