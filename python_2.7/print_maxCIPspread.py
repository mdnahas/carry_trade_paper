#!/usr/bin/python

# division returns float always; use // for integer division
from __future__ import division
from __future__ import print_function

import math
import sys
import datetime

import swap_rate_lib as srl

import pandas as pd  
from scipy.stats import sem
import numpy as np

# Check num of args - note sys.argv[0] is the script name
if len(sys.argv) != 7:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 7 programname dates_filename swap_dir govt_dir corp_file duration outfile")


# sys.argv[0] is the script name
dates_filename = sys.argv[1]
swap_data_directory = sys.argv[2]
govt_data_directory = sys.argv[3]
infilename = sys.argv[4]
duration = int(sys.argv[5])
outfilename = sys.argv[6]

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

data = pd.read_csv(dates_filename)  # do not parse dates.
if infilename != "":
    data_corp = pd.read_csv(infilename)  # do not parse dates.



swap_rates = srl.SwapRateLibrary()
swap_rates.read_swap_file(duration, swap_data_directory + "/currencies" + str(duration) + "Y.csv")
swap_rates.read_govt_file(duration, govt_data_directory + "/govt" + str(duration) + ".csv")

  
# read data
dates_raw = data["date"].tolist()
dates = [ datetime.datetime.strptime( d, "%Y-%m-%d").date() for d in dates_raw]

swap_maxCIPspread_list = []
for i in range(0, len(dates)):
    # IMPORTANT - not set to -inf and +inf.  USD has CIP basis of 0.
    swap_max = 0
    swap_min = 0
    for curr_index in range(0,9):
        curr = currencies_except_USD[curr_index]
        try:
            swap = 10000*swap_rates.get_xcbs_rate(curr, dates[i], duration)
        except Exception:
            swap = float("NaN")
        if not math.isnan(swap):
            swap_max = max(swap_max, swap)
            swap_min = min(swap_min, swap)
    if swap_max - swap_min == 0:
        swap_maxCIPspread_list.append(float("NaN"))
    else:
        swap_maxCIPspread_list.append(swap_max - swap_min)
swap_maxCIPspread = np.array(swap_maxCIPspread_list)

govt_maxCIPspread_list = []
for i in range(0, len(dates)):
    # IMPORTANT - not set to -inf and +inf.  USD has CIP basis of 0.
    govt_max = 0
    govt_min = 0
    for curr_index in range(0,9):
        curr = currencies_except_USD[curr_index]
        try:
            govt = 10000*swap_rates.get_CIP_basis_GOVT2(curr, dates[i], duration)
        except Exception:
            swap = float("NaN")
        if not math.isnan(govt):
            govt_max = max(govt_max, govt)
            govt_min = min(govt_min, govt)
    if govt_max - govt_min == 0:
        govt_maxCIPspread_list.append(float("NaN"))
    else:
        govt_maxCIPspread_list.append(govt_max - govt_min)
govt_maxCIPspread = np.array(govt_maxCIPspread_list)


corp_maxCIPspread_list = []
corp_maxCIPspread_err_list = []
for i in range(0, len(dates)):
    # IMPORTANT - not set to -inf and +inf.  USD has CIP basis of 0.
    corp_max = 0
    corp_max_err = 0
    corp_min = 0
    corp_min_err = 0
    for curr_index in range(0,9):
        curr = currencies_except_USD[curr_index]
        corp = 10000*data_corp[curr][i]
        corp_err = 10000*data_corp[curr + "_err"][i]
        if not math.isnan(corp) and not math.isnan(corp_err):
            if corp > corp_max:
                corp_max = corp
                corp_max_err = corp_err
            if corp < corp_min:
                corp_min = corp
                corp_min_err = corp_err
    if corp_max - corp_min == 0:
        corp_maxCIPspread_list.append(float("NaN"))
        corp_maxCIPspread_err_list.append(float("NaN"))
    else:
        corp_maxCIPspread_list.append(corp_max - corp_min)
        corp_maxCIPspread_err_list.append(1.96 * math.sqrt( corp_max_err**2 + corp_min_err**2))
        #print("date=" + str(dates[i]) + "  max_err=" + str(corp_max_err) + " min_err=" + str(corp_min_err) + "  error=" + str(corp_maxCIPspread_err_list[i]))
corp_maxCIPspread = np.array(corp_maxCIPspread_list)
corp_maxCIPspread_err = np.array(corp_maxCIPspread_err_list)
    

output_file = open(outfilename, 'wb')
output_file.write("date,swap,govt,corp,corp_err\n")
for i in range(0,len(dates)):
    output_file.write(str(dates[i]) + "," + str(swap_maxCIPspread[i]) + "," + str(govt_maxCIPspread[i]) + "," + str(corp_maxCIPspread[i]) + "," + str(corp_maxCIPspread_err[i]) + "\n")
output_file.close()
