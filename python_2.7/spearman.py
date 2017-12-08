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

from scipy.stats import spearmanr
from scipy.stats import pearsonr
import numpy as np

if len(sys.argv) != 3:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 3    programname regression_results true/false")

filename = sys.argv[1]
constrained = sys.argv[2]

if constrained.lower() == "true":
    print("Using Liao's time range.")


with open(filename, 'rb') as infile:
    csv_reader = csv.reader(infile)

    header = csv_reader.next()

    if header[2] != "AUD":
        raise Exception("wrong col for credit spread diff")
    if header[10] != "SEK":
        raise Exception("wrong col for credit spread diff SEK")
    if header[28] != "CIP_basis_XCBS_AUD":
        raise Exception("wrong col for CIP basis")
        
        
    credit_spread_list = []
    basis_list = []
    curr_credit_spread_lists = dict()
    curr_basis_lists = dict()
    for i in range(0,9):
        curr_credit_spread_lists[ i ] = []
        curr_basis_lists[ i ] = []
    
    for row in csv_reader:
        date_str = row[0]
        date = datetime.datetime.strptime( row[0], "%Y-%m-%d").date()

        if constrained.lower() == "true" and (date < datetime.date(2004,1,1) or date > datetime.date(2016, 7, 31)):
            continue

        for i in range(0,9):
            if constrained.lower() == "true" and (header[2+i] == "SEK" or header[2+i] == "NZD" or header[2+i] == "NOK"):
                continue
            
            # index of credit spread diff is 2+i
            # index of basis is 28+i
            if row[2+i] != "" and row[28+i] != "":
                
                if not math.isnan(float(row[2+i])) and not math.isnan(float(row[28+i])):
                    #if float(row[2+i]) < -0.025:
                    #    print("Dropping extreme point from currency " + str(i))
                    #    continue
                    credit_spread_list.append( float(row[2+i]) )
                    basis_list.append( float(row[28+i]) )

                    curr_credit_spread_lists[ i ].append( float(row[2+i]) )
                    curr_basis_lists[ i ].append( float(row[28+i]) )
                    

    s = spearmanr(np.array(credit_spread_list), np.array(basis_list))                
    print("Correlation on " + str(len(credit_spread_list)) + " data points was " + str(s))

    # from https://stats.stackexchange.com/questions/18887/how-to-calculate-a-confidence-interval-for-spearmans-rank-correlation
    r = s[0]
    num = len(credit_spread_list)
    stderr = 1.0 / math.sqrt(num - 3)
    delta = 1.96 * stderr
    lower = math.tanh(math.atanh(r) - delta)
    upper = math.tanh(math.atanh(r) + delta)
    print("95percent confidence interval lower %.6f upper %.6f" % (lower, upper))

    print("Pearson was " + str( pearsonr(np.array(credit_spread_list), np.array(basis_list))))

    for i in range(0,9):
        if constrained.lower() == "true" and (header[2+i] == "SEK" or header[2+i] == "NZD" or header[2+i] == "NOK"):
            continue
        p = pearsonr(np.array(curr_credit_spread_lists[i]), np.array(curr_basis_lists[i]))
        s = spearmanr(np.array(curr_credit_spread_lists[i]), np.array(curr_basis_lists[i]))                
        print( header[2+i] + " P=" + str(p[0]) + " S=" + str(s[0]))
        

    # Line fitting
    z = np.polyfit(basis_list, credit_spread_list, 1)
    #p = np.poly1d(basis_list)
    print("line fit is " + str(z) )
    
