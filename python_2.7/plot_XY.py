#!/usr/bin/python

# division returns float always; use // for integer division
from __future__ import division
from __future__ import print_function

import math
import sys
import datetime

import pandas as pd  
import matplotlib
import matplotlib.pyplot as plt  
from scipy.stats import sem
from scipy.stats import linregress
import numpy as np

# Check num of args - note sys.argv[0] is the script name
if len(sys.argv) != 4:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 3: programname TRUE/FALSE infile outfile")


# sys.argv[0] is the script name
bounds = sys.argv[1]
infilename = sys.argv[2]
outfilename = sys.argv[3]

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

# scale to basis points and convert to array
CSDs = dict()
CIPs = dict()
for curr_index in range(0,9):
    curr = currencies_except_USD[curr_index]
    CSDs[curr] = np.array([ 10000*d for d in data[curr].tolist()])
    CIPs[curr] = np.array([ 10000*d for d in data["CIP_basis_XCBS_" + curr].tolist()])

#years = chess_data.groupby("Year").PlyCount.mean().keys()  
#mean_PlyCount = sliding_mean(chess_data.groupby("Year").PlyCount.mean().values,  
#sem_PlyCount = sliding_mean(chess_data.groupby("Year").PlyCount.apply(sem).mul(1.96).values,  

CSDall_list = []
CIPall_list = []
for curr_index in range(0,9):
    curr = currencies_except_USD[curr_index]
    CSD_curr_list = [ 10000*d for d in data[curr].tolist()]
    CIP_curr_list = [ 10000*d for d in data["CIP_basis_XCBS_" + curr].tolist()]
    for i in range(0, len(CSD_curr_list)):
        if not math.isnan(CSD_curr_list[i]) and not math.isnan(CIP_curr_list[i]):
            CSDall_list.append(CSD_curr_list[i])
            CIPall_list.append(CIP_curr_list[i])
#line_fit = np.polyfit(CSDall_list, CIPall_list, 1)
line_fit = linregress(CSDall_list, CIPall_list)
  
# You typically want your plot to be ~1.33x wider than tall.  
# Common sizes: (10, 7.5) and (12, 9)  
if bounds.lower() == "true":
    plt.figure(figsize=(15,7.5))
else:
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
if bounds.lower() == "true":
    plt.ylim(-100, 50)  
    plt.xlim(-150, 125)  
  
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
    plt.scatter(CSDs[curr], CIPs[curr], color=color_map[curr], label=curr, s=marker_size)  
#    plt.plot(dates, cip_basis, color="#BB0000", lw=2)  


# Trendline
(min_x, max_x) = plt.xlim()
(min_y, max_y) = plt.ylim()
func = np.poly1d([line_fit[0], line_fit[1]])
plt.plot([min_x, max_x], [func(min_x), func(max_x)], "r--")

if bounds.lower() == "true":
    min_y += 10

# Trendline eqn
plt.text(max_x, min_y, "Basis = {:.4f}*RCSD + {:.4f}\nRsq: {:.4f}".format(line_fit[0], line_fit[1], line_fit[2]**2), fontsize=16, color="red", horizontalalignment='right', verticalalignment='bottom')

# Make the title big enough so it spans the entire plot, but don't make it  
# so big that it requires two lines to show.  
plt.title("CIP basis vs. RCSD", fontsize=22)  

plt.xlabel("Residualized Credit Spread Diff. (in basis points)", fontsize=16)  

# Legend
plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

# Finally, save the figure as a PNG.  
# You can also save it as a PDF, JPEG, etc.  
# Just change the file extension in this call.  
# bbox_inches="tight" removes all the extra whitespace on the edges of your plot.  
plt.savefig(outfilename, bbox_inches="tight")
