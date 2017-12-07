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

currencies_except_USD = [ 
             "AUD",
             "CAD",
             "CHF",
             "EUR", 
             "GBP",
             "JPY",
             "NOK",
             "NZD",
             "SEK"]

if len(sys.argv) != 4:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 4.  Program raw_data_dir input_filename")
raw_data_directory = sys.argv[1]
input_filename = sys.argv[2]
output_filename = sys.argv[3]

duration = 5

swap_rates = srl.SwapRateLibrary()
swap_rates.read_swap_file(duration, raw_data_directory + "/currencies" + str(duration) + "Y.csv")

with open(input_filename, 'rb') as infile:
    csv_reader = csv.reader(infile)
    with open(output_filename, 'wb') as outfile:
        csv_writer = csv.writer(outfile)

        # copy header
        first_line = csv_reader.next()
        first_line.extend(  [ "CIP_basis_XCBS_" + curr for curr in currencies_except_USD] )
        csv_writer.writerow(first_line)

        for row in csv_reader:

            # "date" is at index 0

            date = datetime.datetime.strptime( row[0], "%Y-%m-%d").date()

            row_addendum = []
            for curr in currencies_except_USD:
                try:
                    row_addendum.append( str(swap_rates.get_xcbs_rate(curr, date, duration)) )
                except Exception:
                    row_addendum.append( "" )

            row.extend(row_addendum)
            csv_writer.writerow(row)

    

            

