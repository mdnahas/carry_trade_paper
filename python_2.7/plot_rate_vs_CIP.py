#!/usr/bin/python

# division returns float always; use // for integer division
from __future__ import division
from __future__ import print_function

import sys
import os
import csv
import datetime

import swap_rate_lib as srl

import pandas as pd  
import matplotlib
import matplotlib.pyplot as plt  
from scipy.stats import sem
import numpy as np

# Check num of args - note sys.argv[0] is the script name
if len(sys.argv) != 7:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 7: programname raw_data_dir data_dir duration swap_or_govt infile outfile")


# sys.argv[0] is the script name
raw_data_directory = sys.argv[1]
data_directory = sys.argv[2]
duration = int(sys.argv[3])
swap_or_govt = sys.argv[4]
infilename = sys.argv[5]
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

    

data = pd.read_csv(infilename)  # do not parse dates.

swap_rates = srl.SwapRateLibrary()
if duration == 1:
    swap_rates.read_swap_file(1, os.path.join(raw_data_directory, "currencies1Y_faked.csv"))
else:
    swap_rates.read_swap_file(duration, raw_data_directory + "/currencies" + str(duration) + "Y.csv")
swap_rates.read_govt_file(duration, os.path.join(data_directory, "govt" + str(duration) + ".csv"))

  
# read data
dates_raw = data["date"].tolist()
dates = [ datetime.datetime.strptime( d, "%Y-%m-%d").date() for d in dates_raw]

# scale to basis points and convert to array
CIPs = dict()
RateSpreads = dict()
for curr_index in range(0,9):
    curr = currencies_except_USD[curr_index]
    CIPs[curr] = np.array([ 10000*d for d in data[curr].tolist()])
    # missing values reported as NaN by swap_rates
    if swap_or_govt == "swap":
        RateSpreads[curr] = np.array([ 10000*(swap_rates.get_swap_rate(curr, d, duration)) for d in dates])
        #RateSpreads[curr] = np.array([ 10000*(swap_rates.get_swap_rate(curr, d, duration) - swap_rates.get_swap_rate("USD", d, duration)) for d in dates])
    elif swap_or_govt == "govt":
        RateSpreads[curr] = np.array([ 10000*(swap_rates.get_govt_rate(curr, d, duration)) for d in dates])
        #RateSpreads[curr] = np.array([ 10000*(swap_rates.get_govt_rate(curr, d, duration) - swap_rates.get_govt_rate("USD", d, duration)) for d in dates])
    else:
        raise Exception("bad value for swap_or_govt:" + swap_or_govt)
        

# indices = []
# for i in range(0, len(dates)):
#     if dates[i] > datetime.date(2008,1,1):
#         indices.append(i)

# old_dates = dates
# dates = [ old_dates[i] for i in indices]
# old_CIPs = CIPs
# old_RateSpreads = RateSpreads
# CIPs = dict()
# RateSpreads = dict()
# for curr_index in range(0,9):
#     curr = currencies_except_USD[curr_index]
#     CIPs[curr] = [ old_CIPs[curr][i] for i in indices]
#     RateSpreads[curr] = [ old_RateSpreads[curr][i] for i in indices]

    
#years = chess_data.groupby("Year").PlyCount.mean().keys()  
#mean_PlyCount = sliding_mean(chess_data.groupby("Year").PlyCount.mean().values,  
#sem_PlyCount = sliding_mean(chess_data.groupby("Year").PlyCount.apply(sem).mul(1.96).values,  
  
# You typically want your plot to be ~1.33x wider than tall.  
# Common sizes: (10, 7.5) and (12, 9)  
plt.figure(figsize=(10,7.5))
  
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
#if bounds.lower() == "true":
plt.ylim(-200, 200)  
#    plt.xlim(-150, 50)  
  
# Make sure your axis ticks are large enough to be easily read.  
# You don't want your viewers squinting to read your plot.  
#plt.xticks(range( datetime.date(1998,1,1), datetime.date(2017,4,30)), fontsize=14)  
#plt.yticks(range(-0.1, 0.1, 0.01), fontsize=14)  


# x-axis and y-axis at zero
plt.axhline(0, color='black', linestyle="dotted")
plt.axvline(0, color='black', linestyle="dotted")

# Along the same vein, make sure your axis labels are large  
# enough to be easily read as well. Make them slightly larger  
# than your axis tick labels so they stand out.  
plt.ylabel("CIP Basis (in basis points)", fontsize=16)  
  
# Use matplotlib's fill_between() call to create error bars.  
# Use the dark blue "#3F5D7D" as a nice fill color.  
#plt.fill_between(dates, means - error_margin, means + error_margin, color="#B0B0B0") 

# plot
marker_size = plt.rcParams['lines.markersize'] ** 2  ## The default.  Area.
marker_size *= .4
for curr_index in range(0,9):
    curr = currencies_except_USD[curr_index]
    plt.scatter(RateSpreads[curr], CIPs[curr], color=color_map[curr], label=curr, s=marker_size)  
#    plt.plot(dates, cip_basis, color="#BB0000", lw=2)  
  
# Make the title big enough so it spans the entire plot, but don't make it  
# so big that it requires two lines to show.  
plt.title("Rate vs. CIP Basis", fontsize=22)  

plt.xlabel("Rate - USD Rate (in basis points)", fontsize=16)  

# Legend
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

# Finally, save the figure as a PNG.  
# You can also save it as a PDF, JPEG, etc.  
# Just change the file extension in this call.  
# bbox_inches="tight" removes all the extra whitespace on the edges of your plot.  
plt.savefig(outfilename, bbox_inches="tight");  
