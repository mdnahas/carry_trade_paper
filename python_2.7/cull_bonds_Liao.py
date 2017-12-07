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
from sets import Set

infilenames = [ "bonds150_2001-1-1_to_2006-1-1.csv", 
        "bonds150_2006-1-1_to_2010-1-1.csv",
        "bonds150_2010-1-1_to_2014-1-1.csv",
        "bonds150_2014-1-1_to_2016-6-1.csv",
        "bonds150_2016-6-1_to_2018-9-1.csv",
        "bonds150_2018-9-1_to_2021-1-1.csv",
        "bonds150_2021-1-1_to_2024-4-1.csv" ]

    
if len(sys.argv) != 3:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 3.  Program raw_directory outputfilename")
infile_directory = sys.argv[1]
outfilename = sys.argv[2]
    

# keep a dictionary of firms -> set of currencies
firms_to_currencies = dict()

# read all the bonds from raw_data/bonds150...csv
for infilename in infilenames:
    with open(infile_directory + infilename, 'rb') as csv_infile:
        csv_reader = csv.reader(csv_infile)
        first_line = csv_reader.next()
        for row in csv_reader:
            issuer = row[0]
            curr = row[6]

            if issuer not in firms_to_currencies:
                firms_to_currencies[issuer] = Set()  # set with just this currency
            firms_to_currencies[issuer].add( curr )

firms_used = Set()
written_header = False

with open(outfilename, 'wb') as f:
    writer = csv.writer(f)
    for infilename in infilenames:
        with open(infile_directory + infilename, 'rb') as csv_infile:
            csv_reader = csv.reader(csv_infile)
            first_line = csv_reader.next()

            if not written_header:
                writer.writerow(first_line)
                written_header = True
            
            for row in csv_reader:
                issuer = row[0]
                isin = row[3]
                coupon = row[4]
                maturity = row[5]
                currency = row[6]
                sandp_rating = row[9]

                # Skip a badly formatted bond: JP389840ATB2
                if sandp_rating == "*-":
                    continue

                # missing ISIN
                if isin == "#N/A Field Not Applicable":
                    continue

                # missing coupon
                if coupon == "#N/A N/A":
                    continue

                # missing maturity
                if maturity == "#N/A Field Not Applicable":
                    continue
                                
                # Skip JPY and AUD
                # if currency == "JPY" or currency == "AUD":
                #     continue
                
                    
                # issuer must be in dictionary!  Dying is fine if it isn't.
                if len(firms_to_currencies[issuer]) >= 2:
                    writer.writerow(row)
                    firms_used.add( issuer )

print("Number of firms: " + str(len(firms_used)))
