#!/usr/bin/python

# division returns float always; use // for integer division
from __future__ import division
from __future__ import print_function

import csv
import sys
import os
import math
import datetime
import unittest

import price_and_yield_lib as py


prices_filenames = ["prices150_2001-1-1_to_2006-1-1.csv",
                    "prices150_2006-1-1_to_2010-1-1.csv",
                    "prices150_2010-1-1_to_2014-1-1.csv",
                    "prices150_2014-1-1_to_2016-6-1.csv",
                    "prices150_2016-6-1_to_2018-9-1.csv",
                    "prices150_2018-9-1_to_2021-1-1.csv",
                    "prices150_2021-1-1_to_2024-4-1.csv"]

if len(sys.argv) != 4:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 4.  Program bondfile input_directory output_directory")
bonds_filename = sys.argv[1]
infile_directory = sys.argv[2]
outfile_directory = sys.argv[3]


x = py.BondLibrary()

# read bonds

with open(bonds_filename, 'rb') as csv_infile:
    csv_reader = csv.reader(csv_infile)
    first_line = csv_reader.next()

    for row in csv_reader:
        # "issuer" is at index 0
        # "ISIN" is at index 3
        # "Cpn" is at index 4
        # "Maturity" is at index 5
        # "Currency" is at index 6
        # "Amount Issued" is at index 7
        # Moody's initial rating is at index 8
        # S&P's initial rating is at index 9
        # "Issue Date" DOES NOT EXIST
        # "Price at Issue" is at index 10
        # "Yield at Issue" is at index 11  # BUT USUALLY EMPTY
        # "Duration" is at index 12

        issuer = row[0]

        if row[3] == "#N/A Field Not Applicable":
            print("BOND WITHOUT ISIN: " + str(row), file=sys.stderr)
            continue
        isin = row[3]

        if row[4] == "#N/A N/A":
            print("BOND WITHOUT COUPON: " + str(isin), file=sys.stderr)
            continue
        coupon = float( row[4] )

        if row[5] == "#N/A Field Not Applicable":
            print("BOND WITHOUT MATURITY: " + str(isin), file=sys.stderr)
            continue
        maturity = datetime.datetime.strptime( row[5], "%m/%d/%Y").date()

        currency = row[6]
        # replace German Deutchmarks with Euros here.
        if currency == "DEM":
            currency = "EUR"

        moody_rating = row[8]
        sandp_rating = row[9]

        if row[12] == "#N/A N/A":
            print("BOND WITHOUT DURATION: " + str(isin), file=sys.stderr)
            continue
        duration = float( row[12] )
        issue_date = maturity - datetime.timedelta(days=(int(round(duration*365.25))))

        if not py.isMajorCurrency(currency):
            continue

        x.insertBond(isin, coupon/100.0, py.convertToQLDate(maturity), py.convertToQLDate(issue_date), currency, issuer, moody_rating, sandp_rating)



# map from date to files for each.
output_files = dict()
output_counts = dict()


for prices_filename in prices_filenames:
    print("Reading new file: " + prices_filename, file=sys.stderr)
    
    with open(os.path.join(infile_directory, prices_filename), 'rb') as csv_infile:
        csv_reader = csv.reader(csv_infile)

        # No header on these files
        #first_line = csv_reader.next()

        for row in csv_reader:
            # "security id" with ISIN is at index 0
            # "date" is at index 1
            # "price" is at index 2

            sec_id = row[0]    # Example: /isin/US022249AT36
            isin = sec_id[6:]

            date = datetime.datetime.strptime( row[1], "%Y-%m-%d").date()

            if row[1] not in output_counts:
                output_counts[ row[1] ] = dict()
                output_counts[ row[1] ]["noprice"] = 0
                output_counts[ row[1] ]["bondmissing"] = 0
                output_counts[ row[1] ]["maturity"] = 0
                output_counts[ row[1] ]["extreme"] = 0
                output_counts[ row[1] ]["success"] = 0
                output_counts[ row[1] ]["exception"] = 0
                output_counts[ row[1] ]["eitherway"] = 0
                output_counts[ row[1] ]["all"] = 0
            output_counts[ row[1] ]["all"] += 1

            if row[2] == "":
                output_counts[ row[1] ]["noprice"] += 1
                continue
            clean_price = float( row[2] )

            if not x.containsIsin(isin):
                output_counts[ row[1] ]["bondmissing"] += 1
                continue

            currency = x.currencyFromIsin(isin)

            maturity_date = x.pythonMaturityFromIsin(isin)
            duration_in_days = (maturity_date - date).days
            #if duration_in_days < 3*365.25 or 7*365.25 < duration_in_days:
            #    output_counts[ row[1] ]["maturity"] += 1
            #    continue

            # create files/csvwriter for output
            if row[1] not in output_files:
                print("Writing new file: " + row[1], file=sys.stderr)
                output_files[ row[1] ] = open(os.path.join(outfile_directory, row[1]), 'wb')
                #output_csvwriters[ row[1] ] = csv.writer(output_files[ row[1] ])
                output_files[ row[1] ].write("ISIN,date,price,yield," + x.csvDescriptionOfBondHeader() + "\n")

            try:
                common_yield = x.commonYieldFromCleanPrice(isin, py.convertToQLDate(date), clean_price)
            except RuntimeError as e:
                #print("EXCEPTION WHILE CALCULATING YIELD for " + isin + "," + str(date), file=sys.stderr)
                #print(e, file=sys.stderr)
                #print("<END EXCEPTION WHILE CALCULATING YIELD>", file=sys.stderr)
                #output_counts[ row[1] ]["exception"] += 1
                #continue
                common_yield = float("NaN")

            # If valid both ways, drop.
            if (currency == "AUD" or currency == "JPY") and ((not math.isnan(common_yield)) and common_yield >= -.10 and common_yield <= .30) and (clean_price/100.0 >= -.10 and clean_price/100.0 <= .30):
                output_counts[ row[1] ]["eitherway"] += 1
                continue
                
            if (currency == "AUD" or currency == "JPY") and (math.isnan(common_yield) or common_yield < -.10 or common_yield > .30) and (clean_price/100.0 >= -.10 and clean_price/100.0 <= .30):
                common_yield = clean_price / 100.0

            if math.isnan(common_yield):
                print("EXCEPTION WHILE CALCULATING YIELD for " + isin + "," + str(date), file=sys.stderr)
                output_counts[ row[1] ]["exception"] += 1
                continue

            if common_yield < -.10 or common_yield > .30:
                # print("WARNING: Extreme yield " + str(common_yield) + " on " + isin + " with " + currency + " on " + str(date), file=sys.stderr)
                # SKIP EXTREME VALUES
                output_counts[ row[1] ]["extreme"] += 1
                continue

            # date will always be the same, but include it anyway.
            output_files[ row[1] ].write(isin + "," + str(date) + "," + str(clean_price) + "," + str(common_yield) + "," + x.csvDescriptionOfBond(isin) + "\n")
            output_counts[ row[1] ]["success"] += 1


# close files
for date in output_files:
    output_files[ date ].close()

# output counts
print("date, all, no price, bond missing, maturity issue, extreme value, success, exception, eitherway")
for date in output_counts:
    print(date + ", " + str(output_counts[ date ]["all"]) + ", " +
          str(output_counts[ date ]["noprice"]) + ", " +
          str(output_counts[ date ]["bondmissing"]) + ", " +
          str(output_counts[ date ]["maturity"]) + ", " +
          str(output_counts[ date ]["extreme"]) + ", " +
          str(output_counts[ date ]["success"]) + ", " +
          str(output_counts[ date ]["exception"]) + ", " +
          str(output_counts[ date ]["eitherway"]))

    
