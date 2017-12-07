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

if len(sys.argv) != 6:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 6.  Program swap_data_dir govt_data_dir duration input_filename output_filename")
swap_data_directory = sys.argv[1]
govt_data_directory = sys.argv[2]
duration = int(sys.argv[3])
input_filename = sys.argv[4]
output_filename = sys.argv[5]

swap_rates = srl.SwapRateLibrary()
swap_rates.read_swap_file(duration, swap_data_directory + "/currencies" + str(duration) + "Y.csv")
swap_rates.read_govt_file(duration, govt_data_directory + "/govt" + str(duration) + ".csv")

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
                    row_addendum.append( str(swap_rates.get_CIP_basis_XCBS_GOVT2(curr, date, duration)) )
                except Exception:
                    row_addendum.append( "" )

            row.extend(row_addendum)
            csv_writer.writerow(row)

    

            

