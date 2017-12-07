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

def process_file(duration, filename):
    with open(filename, 'rb') as csv_infile:
        csv_reader = csv.reader(csv_infile, delimiter=";")

        # NOTE: opening to append
        with open(os.path.join(outfile_directory, "govt" + str(duration) + ".csv"), 'ab') as outfile:
            csv_writer = csv.writer(outfile)
    
            # read header, do not write one.
            first_line = csv_reader.next()
        
            for row in csv_reader:
                # date; sector; product; value
                date = datetime.datetime.strptime(row[0], "%d/%m/%Y").date()
                value_str = row[3]

                if value_str == "n/a":
                    value_str = ""
                
                output_row = [ "SEK" + str(duration) + " govt", str(date), value_str ]
                csv_writer.writerow(output_row)
            
process_file(1, infile_directory + "/12M_1998_to_2008.csv")
process_file(1, infile_directory + "/12M_2008_to_2017.csv")
process_file(2, infile_directory + "/2Y_1998_to_2008.csv")
process_file(2, infile_directory + "/2Y_2008_to_2017.csv")
process_file(5, infile_directory + "/5Y_1998_to_2008.csv")
process_file(5, infile_directory + "/5Y_2008_to_2017.csv")
process_file(7, infile_directory + "/7Y_1998_to_2008.csv")
process_file(7, infile_directory + "/7Y_2008_to_2017.csv")
process_file(10, infile_directory + "/10Y_1998_to_2008.csv")
process_file(10, infile_directory + "/10Y_2008_to_2017.csv")
