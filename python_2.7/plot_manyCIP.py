#!/usr/bin/python

# division returns float always; use // for integer division
from __future__ import division
from __future__ import print_function

import sys
import datetime

import pandas as pd  
import matplotlib
import matplotlib.pyplot as plt  
from scipy.stats import sem
import numpy as np

# Check num of args - note sys.argv[0] is the script name
if len(sys.argv) != 5:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 5: programname infile column_suffix data_description outfile")


# sys.argv[0] is the script name
infilename = sys.argv[1]
column_suffix = sys.argv[2]
data_description = sys.argv[3]
outfilename = sys.argv[4]


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

  
# read data
dates_raw = data["date"].tolist()
dates = [ datetime.datetime.strptime( d, "%Y-%m-%d").date() for d in dates_raw]

CIPs = dict()
for curr_index in range(0,9):
    curr = currencies_except_USD[curr_index]
    CIPs[curr] = np.array([ 10000*d for d in data[curr + column_suffix].tolist()])

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
plt.ylabel("CIP Basis (in basis points)", fontsize=16)  
  
# plot CIP basis
for curr_index in range(0,9):
    curr = currencies_except_USD[curr_index]
    plt.plot(dates, CIPs[curr], lw=2, label=curr, color=color_map[curr])  
  
  
# Make the title big enough so it spans the entire plot, but don't make it  
# so big that it requires two lines to show.  
plt.title("CIP Basis, " + data_description, fontsize=22)  

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
