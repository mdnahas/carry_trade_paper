#!/usr/bin/python

# division returns float always; use // for integer division
from __future__ import division
from __future__ import print_function

import math
import sys
import datetime

import swap_rate_lib as srl

import pandas as pd  
import matplotlib
import matplotlib.pyplot as plt  
from scipy.stats import sem
import numpy as np

# Check num of args - note sys.argv[0] is the script name
if len(sys.argv) != 5 and len(sys.argv) != 6:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 5 or 6: programname dates_filename swap_dir govt_dir outfile corp_file")


# sys.argv[0] is the script name
dates_filename = sys.argv[1]
swap_data_directory = sys.argv[2]
govt_data_directory = sys.argv[3]
outfilename = sys.argv[4]
if len(sys.argv) >= 6:
    infilename = sys.argv[5]
else:
    infilename = ""

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

color_map = {
             "USD":"#FF0000",
             "AUD":"#F45F5A",
             "CAD":"#A88F04",
             "CHF":"#2DB12A",
             "EUR":"#2AB3B7",
             "GBP":"#4F87FE",
             "JPY":"#EF43DB",
             "NOK":"#2B8A53",
             "NZD":"#BF80FE",
             "SEK":"#FDC30B"}


data = pd.read_csv(dates_filename)  # do not parse dates.
if infilename != "" and infilename != "swapsonly":
    data_corp = pd.read_csv(infilename)  # do not parse dates.


duration = 5

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


if infilename != "" and infilename != "swapsonly":
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
    corp_maxCIPspread = np.array(corp_maxCIPspread_list)
    corp_maxCIPspread_err = np.array(corp_maxCIPspread_err_list)
    

#years = chess_data.groupby("Year").PlyCount.mean().keys()  
#mean_PlyCount = sliding_mean(chess_data.groupby("Year").PlyCount.mean().values,  
#sem_PlyCount = sliding_mean(chess_data.groupby("Year").PlyCount.apply(sem).mul(1.96).values,  
  
# You typically want your plot to be ~1.33x wider than tall.  
# Common sizes: (10, 7.5) and (12, 9)  
plt.figure(figsize=(12, 6))  
  
# Remove the plot frame lines. They are unnecessary chart
ax = plt.subplot(111)  
ax.spines["top"].set_visible(False)  
ax.spines["right"].set_visible(False)  
  
# Ensure that the axis ticks only show up on the bottom and left of the plot.  
# Ticks on the right and top of the plot are generally unnecessary chartjunk.  
matplotlib.rcParams.update({'font.size': 14}) 
ax.get_xaxis().tick_bottom()  
ax.get_yaxis().tick_left()  
  
# Limit the range of the plot to only where the data is.  
# Avoid unnecessary whitespace.  
#if col_mean == "CHF":
#plt.ylim(-400, 200)  
  
# Make sure your axis ticks are large enough to be easily read.  
# You don't want your viewers squinting to read your plot.  
#plt.xticks(range( datetime.date(1998,1,1), datetime.date(2017,4,30)), fontsize=14)  
#plt.yticks(range(-0.1, 0.1, 0.01), fontsize=14)  


# x-axis at zero
plt.axhline(0, color='black', linestyle="dotted")

# Along the same vein, make sure your axis labels are large  
# enough to be easily read as well. Make them slightly larger  
# than your axis tick labels so they stand out.  
plt.ylabel("Max CIP Basis Spread (in basis points)", fontsize=16)  

# plot error margins
if infilename != "" and infilename != "swapsonly":
    plt.fill_between(dates, corp_maxCIPspread - corp_maxCIPspread_err, corp_maxCIPspread + corp_maxCIPspread_err, color="#D9D9D9") 
# plot CIP basis
if infilename != "" and infilename != "swapsonly":
    plt.plot(dates, corp_maxCIPspread, lw=2, label="Corp.", color="#000000")  
plt.plot(dates, swap_maxCIPspread, lw=2, label="Swap", color="#FF0000")  
if infilename != "swapsonly":
    plt.plot(dates, govt_maxCIPspread, lw=2, label="Govt.", color="#8080FF")  
  
# Make the title big enough so it spans the entire plot, but don't make it  
# so big that it requires two lines to show.  
plt.title("Max CIP Basis Spread", fontsize=22)  

plt.xlabel("Years", fontsize=16)  

# add a legend?
# above:
# plt.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)
# to right:
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)


# Finally, save the figure as a PNG.  
# You can also save it as a PDF, JPEG, etc.  
# Just change the file extension in this call.  
# bbox_inches="tight" removes all the extra whitespace on the edges of your plot.  
plt.savefig(outfilename, bbox_inches="tight")
