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
if len(sys.argv) != 9:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 9")


# sys.argv[0] is the script name
col_mean  = sys.argv[1]
col_stdev = sys.argv[2]
col_cip_basis_xcbs = sys.argv[3]
infilename = sys.argv[4]
outfilename = sys.argv[5]
infilename_corp = sys.argv[6]
col_cip_basis_corp = sys.argv[7]
col_cip_basis_corp_stdev = sys.argv[8]
    

data = pd.read_csv(infilename)  # do not parse dates.


  
# read data
dates_raw = data["date"].tolist()
dates = [ datetime.datetime.strptime( d, "%Y-%m-%d").date() for d in dates_raw]

# scale to basis points and convert to array
means_list = []
for i in range(0, len(dates)):
    means_list.append(10000*(data[col_cip_basis_xcbs][i] - data[col_mean][i]))
means = np.array( means_list )
error_margin = np.array([ 1.96 * 10000*d for d in data[col_stdev].tolist()])

data_corp = pd.read_csv(infilename_corp)  # do not parse dates.

# Check that dates match
dates_corp_raw = data_corp["date"].tolist()
if dates_corp_raw != dates_raw:
    raise Exception("Dates did not match!")

# subtract CIP basis corp from CIP basis XCBS
cip_basis_corp = np.array([10000*d for d in data_corp[col_cip_basis_corp].tolist() ])
cip_basis_corp_error_margin = np.array([1.96 * 10000*d for d in data_corp[col_cip_basis_corp_stdev].tolist() ])

#years = chess_data.groupby("Year").PlyCount.mean().keys()  
#mean_PlyCount = sliding_mean(chess_data.groupby("Year").PlyCount.mean().values,  
#sem_PlyCount = sliding_mean(chess_data.groupby("Year").PlyCount.apply(sem).mul(1.96).values,  
  
# You typically want your plot to be ~1.33x wider than tall.  
# Common sizes: (10, 7.5) and (12, 9)  
plt.figure(figsize=(11, 5))  
  
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
#plt.yticks(range(-150, 50, 20), fontsize=14)  
#plt.ylim(-150,50)

# x-axis at zero
plt.axhline(0, color='black', linestyle="dotted")

# Along the same vein, make sure your axis labels are large  
# enough to be easily read as well. Make them slightly larger  
# than your axis tick labels so they stand out.  
plt.ylabel("basis points", fontsize=16)  
  
# Use matplotlib's fill_between() call to create error bars.  
# Use the dark blue "#3F5D7D" as a nice fill color.  
plt.fill_between(dates, means - error_margin, means + error_margin, facecolor="#000000", alpha=.25) 
plt.fill_between(dates, cip_basis_corp - cip_basis_corp_error_margin, cip_basis_corp + cip_basis_corp_error_margin, facecolor="#FF0000", alpha=.25) 

# plot CIP basis
plt.plot(dates, means, color="#000000", lw=2)  
plt.plot(dates, cip_basis_corp, color="#FF0000", lw=2)  
  
# Plot the means as a white line in between the error bars.   
# White stands out best against the dark blue.  
#plt.plot(dates, means, color="#000000", lw=2)  
  
# Make the title big enough so it spans the entire plot, but don't make it  
# so big that it requires two lines to show.  
plt.title("Net Deviation, " + col_mean, fontsize=22)  

plt.xlabel("Year", fontsize=16)  
  
# Finally, save the figure as a PNG.  
# You can also save it as a PDF, JPEG, etc.  
# Just change the file extension in this call.  
# bbox_inches="tight" removes all the extra whitespace on the edges of your plot.  
plt.savefig(outfilename, bbox_inches="tight")
