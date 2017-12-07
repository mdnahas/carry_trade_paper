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


# Reads Bundesbank files and appends to output in data/govt

if len(sys.argv) != 3:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 3.  Program infile_directory output_directory")
infile_directory = sys.argv[1]
outfile_directory = sys.argv[2]

def process_file(duration, filename):
    with open(filename, 'rb') as csv_infile:
        csv_reader = csv.reader(csv_infile)

        # NOTE: opening to append
        with open(os.path.join(outfile_directory, "govt" + str(duration) + ".csv"), 'ab') as outfile:
            csv_writer = csv.writer(outfile)
    
            # read 5 lines of header, do not write any
            first_line = csv_reader.next()
            first_line = csv_reader.next()
            first_line = csv_reader.next()
            first_line = csv_reader.next()
            first_line = csv_reader.next()
        
            for row in csv_reader:
                # date, value
                date_str = row[0]
                value_str = row[1]
                comment_str = row[2]

                # NOTE: date uses 01 and 04 for month and day.
                
                if comment_str == "No value available":
                    value_str = ""
                elif comment_str == "":
                    pass
                else:
                    print("WARNING: Unknown comment: " + comment_str, file=sys.stderr)
                
                output_row = [ "EUR" + str(duration) + " govt", date_str, value_str ]
                csv_writer.writerow(output_row)
            
process_file(1, infile_directory + "/Bund_1Y.csv")
process_file(2, infile_directory + "/Bund_2Y.csv")
process_file(3, infile_directory + "/Bund_3Y.csv")
process_file(5, infile_directory + "/Bund_5Y.csv")
process_file(7, infile_directory + "/Bund_7Y.csv")
process_file(10, infile_directory + "/Bund_10Y.csv")
process_file(20, infile_directory + "/Bund_20Y.csv")
