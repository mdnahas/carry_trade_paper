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
from sets import Set

import rating_lib as rl
import swap_rate_lib as srl

curr_map = { "USD":0,
             "AUD":1,
             "CAD":2,
             "CHF":3,
             "DEM":4,
             "EUR":4,   # same as DEM
             "GBP":5,
             "JPY":6,
             "NOK":7,
             "NZD":8,
             "SEK":9
             }

    
if len(sys.argv) != 8:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 8.  Program swap_data_dir govt_data_dir input_directory duration lower_bound upper_bound output_directory")
swap_data_directory = sys.argv[1]
govt_data_directory = sys.argv[2]
infile_directory = sys.argv[3]
reference_duration = float(sys.argv[4]) # 5.0
lower_bound = float(sys.argv[5]) # 3.0
upper_bound = float(sys.argv[6]) # 7.0
outfile_directory = sys.argv[7]

        
swap_rates = srl.SwapRateLibrary()
swap_rates.load_files(swap_data_directory, govt_data_directory)
for filename in os.listdir(infile_directory):
    firms_to_currencies = dict()

    print("Processing " + filename)
    with open(os.path.join(infile_directory, filename), 'rb') as infile:
        csv_reader = csv.reader(infile)
        first_line = csv_reader.next()

        for row in csv_reader:
            currency = row[7]
            firm = row[8]

            date = datetime.datetime.strptime( row[1], "%Y-%m-%d").date()
            maturity = datetime.datetime.strptime( row[5], "%Y-%m-%d").date()

            # compute duration, lookup swap rate, subtract from yield
            duration_in_days = (maturity-date).days
            duration = duration_in_days / 365.25

            # Window of 3 to 7 years
            if duration < lower_bound or duration > upper_bound:
                continue

            if math.isnan(swap_rates.get_govt_rate(currency, date, duration)):
                continue

            if math.isnan(swap_rates.get_govt_rate(currency, date, reference_duration)):
                continue
            
            try:
                swap_rates.get_Method2_factor("USD", currency, date, reference_duration)
            except Exception as e:
                continue
            
            if firm not in firms_to_currencies:
                firms_to_currencies[firm] = Set()  # set with just this currency
            firms_to_currencies[firm].add( currency )
            
    # close file and read it again

    firm_identifiers = dict()
    next_identifier = 1
                        
    with open(os.path.join(infile_directory,filename), 'rb') as infile:
        csv_reader = csv.reader(infile)
        with open(os.path.join(outfile_directory,filename), 'wb') as outfile:
            csv_writer = csv.writer(outfile)

            # copy header
            first_line = csv_reader.next()
            first_line.extend([ "swap_rate", "credit_spread", "combined_rating", "rating_bucket", "duration_bucket", "adjusted_yield", "duration_diff", "fx_term" ])
            csv_writer.writerow(first_line)

            for row in csv_reader:

                # "isin" is at index 0
                # "date" is at index 1
                # "yield" is at index 3
                # "maturity" is at index 5
                # "currency" is at index 7
                # "firm" is at index 8
                # "moody" is at index 9
                # "sandp" is at index 10

                isin = row[0]
                date = datetime.datetime.strptime( row[1], "%Y-%m-%d").date()
                yyield = float(row[3])
                maturity = datetime.datetime.strptime( row[5], "%Y-%m-%d").date()
                currency = row[7]
                firm = row[8]
                
                # over write currency with index
                row[7] = curr_map[ currency ]

                moody_rating = row[9]
                sandp_rating = row[10]
                moody_rating_int = rl.moody_as_int(moody_rating, isin)
                sandp_rating_int = rl.sandp_as_int(sandp_rating, isin)
                row[9] = str(moody_rating_int)
                row[10] = str(sandp_rating_int)

                # compute duration, lookup swap rate, subtract from yield
                duration_in_days = (maturity-date).days
                duration = duration_in_days / 365.25

                # Window of 3 to 7 years
                if duration < lower_bound or duration > upper_bound:
                    continue

                # legacy
                if duration < 1.0:
                    continue
                elif duration < 3.0:
                    duration_bucket = 1
                elif duration < 7.0:
                    duration_bucket = 0
                elif duration < 10.0:
                    duration_bucket = 2
                else:
                    duration_bucket = 3
                
                govt_rate = swap_rates.get_govt_rate(currency, date, duration)
                if math.isnan(govt_rate):
                    print("Skipping " + isin + " on " + currency + "," + str(date) + "," + str(duration) + "Y because of missing govt rate", file=sys.stderr)
                    continue

                govt_ref_rate = swap_rates.get_govt_rate(currency, date, reference_duration)
                if math.isnan(govt_ref_rate):
                    print("Skipping " + isin + " on " + currency + "," + str(date) + "," + str(duration) + "Y because of missing govt ref rate", file=sys.stderr)
                    continue
                
                try:
                    fx_adjustment = swap_rates.get_Method2_factor("USD", currency, date, reference_duration)
                except Exception as e:
                    print("Skipping " + isin + " on " + currency + "," + str(date) + "," + str(duration) + "Y because of exception while getting fx_adjustment:" + str(e))
                    continue

                # Only include bonds when the issuer has issued in multiple currencies.
                if len(firms_to_currencies[firm]) < 2:
                    continue

                # This must be done last, after all possibilities
                # of "continue"ing the loop are passed.  That's because
                # it updates the next_identifier variable.
                if firm not in firm_identifiers:
                    firm_identifiers[ firm ] = next_identifier
                    next_identifier += 1
                row[8] = str( firm_identifiers[ firm ] )

                                
                combined_rating = rl.combine_rating(moody_rating_int, sandp_rating_int) 
                row.extend([ str(govt_rate),
                             str(yyield - govt_rate),
                             str(combined_rating),
                             str(rl.rating_bucket2(combined_rating)),
                             str(duration_bucket),
                             str(fx_adjustment - (yyield - govt_rate + govt_ref_rate)), 
                             str(duration - reference_duration),
                             str(fx_adjustment) ])
                
                csv_writer.writerow(row)
    

            

