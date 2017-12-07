#!/usr/bin/python

# division returns float always; use // for integer division
from __future__ import division
from __future__ import print_function

import sys
import datetime

import swap_rate_lib as srl


import pandas as pd  
import matplotlib
import matplotlib.pyplot as plt  
from scipy.stats import sem
import numpy as np

# Check num of args - note sys.argv[0] is the script name
if len(sys.argv) != 5:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 5:  progname currency infilename outfilename")


# sys.argv[0] is the script name
currency  = sys.argv[1]
raw_data_directory = sys.argv[2]
infilename = sys.argv[3]
outfilename = sys.argv[4]
    

data = pd.read_csv(infilename)  # do not parse dates.



duration = 5
swap_rates = srl.SwapRateLibrary()
swap_rates.read_swap_file(duration, raw_data_directory + "/currencies" + str(duration) + "Y.csv")


  
# read data
dates_raw = data["date"].tolist()
dates = [ datetime.datetime.strptime( d, "%Y-%m-%d").date() for d in dates_raw]

# scale to basis points and convert to array
means = np.array([ 10000*d for d in data[currency].tolist()])
error_margin = np.array([ 1.96 * 10000*d for d in data[currency + "_err"].tolist()])
cip_basis_govt = np.array([ 10000*d for d in data["CIP_basis_XCBS_" + currency].tolist()])
cip_basis_xcbs = np.array([ 10000*swap_rates.get_xcbs_rate(currency, d, duration) for d in dates ])

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
plt.ylim(-150, 150)  
  
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
  
# Use matplotlib's fill_between() call to create error bars.  
# Use the dark blue "#3F5D7D" as a nice fill color.  
plt.fill_between(dates, means - error_margin, means + error_margin, color="#D9D9D9") 

# plot CIP basis
plt.plot(dates, cip_basis_xcbs, color="#F45F5A", lw=2, linestyle="dashed")  
plt.plot(dates, cip_basis_govt, color="#BB0000", lw=2)
  
# Plot the means as a white line in between the error bars.   
# White stands out best against the dark blue.  
plt.plot(dates, means, color="#17B3B7", lw=2, linestyle="dotted")    
  
# Make the title big enough so it spans the entire plot, but don't make it  
# so big that it requires two lines to show.  
plt.title("CIP Basis, All, " + currency, fontsize=22)  

plt.xlabel("Year", fontsize=16)  
  
# Finally, save the figure as a PNG.  
# You can also save it as a PDF, JPEG, etc.  
# Just change the file extension in this call.  
# bbox_inches="tight" removes all the extra whitespace on the edges of your plot.  
plt.savefig(outfilename, bbox_inches="tight")
