#!/usr/bin/python

# division returns float always; use // for integer division
from __future__ import division
from __future__ import print_function

import csv
import sys
import math
import datetime
import calendar
import unittest
import os

import swap_rate_lib as srl

curr_map = { "USD":0,
             "AUD":1,
             "CAD":2,
             "CHF":3,
#             "DEM":4,
             "EUR":4,   # same as DEM
             "GBP":5,
             "JPY":6,
             "NOK":7,
             "NZD":8,
             "SEK":9
             }

    
if len(sys.argv) != 5:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 5.  Program processed_prices_dir lower_limit input_filename output_filename")
processed_prices_directory = sys.argv[1]
lower_limit = int(sys.argv[2])
infilename = sys.argv[3]
outfilename = sys.argv[4]


date_currnum_count_map = dict()
    
for filename in os.listdir(processed_prices_directory):

    print("Processing " + filename)

    date_currnum_count_map[filename] = dict()
    for curr in curr_map:
        date_currnum_count_map[filename][curr_map[curr]] = 0

    
    with open(os.path.join(processed_prices_directory, filename), 'rb') as infile:
        csv_reader = csv.reader(infile)
        first_line = csv_reader.next()

        for row in csv_reader:
            currency = row[7]

            date_currnum_count_map[filename][int(currency)] += 1

            
with open(infilename, 'rb') as infile:
    csv_reader = csv.reader(infile)
    with open(outfilename, 'wb') as outfile:
        csv_writer = csv.writer(outfile)

        # copy header
        first_line = csv_reader.next()
        csv_writer.writerow(first_line)

        # create map for columns
        col_map = dict()
        for i in range(0,len(first_line)):
            col_map[first_line[i]] = i
        
        for row in csv_reader:

            # "date" is at index 0
            date_str = row[0]
            date = datetime.datetime.strptime( date_str, "%Y-%m-%d").date()

            for curr in curr_map:
                try:
                    if row[col_map[curr + "_err"]] != "":
                        err_margin = float(row[col_map[curr + "_err"]])
                        if err_margin < .000001:
                            row[col_map[curr]] = ""
                            row[col_map[curr + "_err"]] = ""
                except ValueError:
                    # not a float value
                    print("Excepted float and found " + row[col_map[curr + "_err"]])
                
                if date_currnum_count_map[date_str][curr_map[curr]] < lower_limit:
                    row[col_map[curr]] = ""
                    row[col_map[curr + "_err"]] = ""

                    
            csv_writer.writerow(row)
    
