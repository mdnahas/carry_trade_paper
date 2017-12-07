#!/usr/bin/python

# division returns float always; use // for integer division
from __future__ import division
from __future__ import print_function

import sys
import csv
import datetime

import pandas as pd  
import matplotlib
import matplotlib.pyplot as plt  
from scipy.stats import sem
import numpy as np

import swap_rate_lib as srl


# Check num of args - note sys.argv[0] is the script name
if len(sys.argv) != 8:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 8: programname swap_data_dir govt_data_dir datesfile reference_currency duration govt_or_swap outfile")

GOVT_SWAP_RATE = 0
SWAP_RATE = 1
XCBS_RATE = 2
GOVT_XCBS_RATE = 3

# sys.argv[0] is the script name
swap_data_directory = sys.argv[1]
govt_data_directory = sys.argv[2]
datesfilename = sys.argv[3]
ref_curr = sys.argv[4]
duration = float(sys.argv[5])
if sys.argv[6] == "govt_swap":
    which_rate = GOVT_SWAP_RATE
elif sys.argv[6] == "swap":
    which_rate = SWAP_RATE
elif sys.argv[6] == "xcbs":
    which_rate = XCBS_RATE
elif sys.argv[6] == "govt_xcbs":
    which_rate = GOVT_XCBS_RATE
else:
    raise Exception("argument had to be govt or swap or xcbs and was: " + sys.argv[6])
outfilename = sys.argv[7]



currencies = [
             "USD",
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


swap_rates = srl.SwapRateLibrary()
#if duration == 1:
#    swap_rates.read_swap_file(duration, swap_data_directory + "/currencies" + str(duration) + "Y_faked.csv")
#else:
if duration < 1.0:
    duration_in_months = int(round(12*duration))
    swap_rates.read_swap_file(duration, swap_data_directory + "/currencies" + str(duration_in_months) + "M.csv")
else:
    swap_rates.read_swap_file(duration, swap_data_directory + "/currencies" + str(int(duration)) + "Y.csv")
    swap_rates.read_govt_file(duration, govt_data_directory + "/govt" + str(int(duration)) + ".csv")


dates = []
CIP_lists = dict()
for curr_index in range(0,10):
    curr = currencies[curr_index]
    if curr == ref_curr:
        continue
    CIP_lists[curr] = []

with open(datesfilename, 'rb') as infile:
    csv_reader = csv.reader(infile)

    # no header
    
    for row in csv_reader:
        date = datetime.datetime.strptime( row[0], "%Y-%m-%d").date()
        dates.append( date )

        for curr_index in range(0,10):
            curr = currencies[curr_index]
            if curr == ref_curr:
                continue
            # NOTE: scale to basis points
            try:
                if which_rate == GOVT_SWAP_RATE:
                    CIP_lists[curr].append( 10000 * swap_rates.get_CIP_basis_GOVT_ANY2(ref_curr, curr, date, duration) )
                elif which_rate == SWAP_RATE:
                    CIP_lists[curr].append( 10000 * swap_rates.get_CIP_basis_SWAP_ANY2(ref_curr, curr, date, duration) )
                elif which_rate == XCBS_RATE:
                    CIP_lists[curr].append( 10000 * swap_rates.get_CIP_basis_XCBS_ANY2(ref_curr, curr, date, duration) )
                else:
                    if ref_curr != "USD":
                        raise Exception("GOVT_XCBS only supports ref_curr=USD, not: " + ref_curr)
                    CIP_lists[curr].append( 10000 * swap_rates.get_CIP_basis_XCBS_GOVT2(curr, date, duration) )
            except Exception as e:
                print("Exception: " + str(e))
                CIP_lists[curr].append( float("NaN") )
    
CIPs = dict()
for curr_index in range(0,10):
    curr = currencies[curr_index]
    if curr == ref_curr:
        continue
    CIPs[curr] = np.array( CIP_lists[curr] )

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
#    plt.ylim(-200, 100)  
  
# Make sure your axis ticks are large enough to be easily read.  
# You don't want your viewers squinting to read your plot.  
#plt.xticks(range( datetime.date(1998,1,1), datetime.date(2017,4,30)), fontsize=14)  
#plt.yticks(range(-0.1, 0.1, 0.01), fontsize=14)  


# x-axis at zero
plt.axhline(0, color='black', linestyle="dotted")

# Along the same vein, make sure your axis labels are large  
# enough to be easily read as well. Make them slightly larger  
# than your axis tick labels so they stand out.  
plt.ylabel("CIP Basis (in basis points)", fontsize=16)  
  
# plot CIP basis
for curr_index in range(0,10):
    curr = currencies[curr_index]
    if curr == ref_curr:
        continue
    plt.plot(dates, CIPs[curr], lw=2, label=curr, color=color_map[curr])  
  
  
# Make the title big enough so it spans the entire plot, but don't make it  
# so big that it requires two lines to show.
if duration < 1.0:
    duration_str = str(int(round(12*duration))) + " month"
else:
    duration_str = str(int(duration)) + " year"

if which_rate == GOVT_SWAP_RATE:
    plt.title("CIP Basis, " + duration_str + ", govt. rate (using forward rates)", fontsize=22)  
elif which_rate == SWAP_RATE:
    if duration >= 1.0:
        plt.title("CIP Basis, " + duration_str + ", swap rate (using forward rates)", fontsize=22)
    else:
        plt.title("CIP Basis, " + duration_str + ", interbank rate", fontsize=22)
elif which_rate == XCBS_RATE:
    plt.title("CIP Basis, " + duration_str + ", swap rate", fontsize=22)
else:
    plt.title("CIP Basis, " + duration_str + ", govt. rate", fontsize=22)

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
