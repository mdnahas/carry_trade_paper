#!/usr/bin/python

# division returns float always; use // for integer division
from __future__ import division

import calendar
import random
import datetime
import sys

if len(sys.argv) != 2:
    raise Exception("bad number of arguments.  Saw " + str(len(sys.argv)) + " expected 2.  Program NYSE_holiday_filename")
NYSE_holiday_filename = sys.argv[1]


# Generate dates to be used in study
#
# Dates are from Jan 1998 to Mar 2017
#
# I choose 1 random day each month.
#   - must be a weekday
#   - must not be a "fixed" holiday (had bad list of these)
#   - must not be on easter calendar (common moving holidays in Europe and USA)
#   - must not be a NYSE trading holiday (had good list of these)

# From https://code.activestate.com/recipes/576517-calculate-easter-western-given-a-year/
def calc_easter(year):
    "Returns Easter as a date object."
    a = year % 19
    b = year // 100
    c = year % 100
    d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
    e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
    f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
    month = f // 31
    day = f % 31 + 1    
    return datetime.date(year, month, day)

def is_easter_holiday(year, month, day):
    date_obj = datetime.date(year, month, day)
    easter = calc_easter(year)
    if date_obj == easter - datetime.timedelta(days=3):  # Thursday before
        return True
    if date_obj == easter - datetime.timedelta(days=2):  # Friday before
        return True
    if date_obj == easter + datetime.timedelta(days=39): # Ascension, 40th day
        return True
    if date_obj == easter + datetime.timedelta(days=50): # Whit Monday, day after Pentecost, 50th day
        return True
    return False


# NYSE holidays from http://www.tradingtheodds.com/nyse-full-day-closings/
NYSE_trading_holidays = set()
with open(NYSE_holiday_filename) as f:
    for line in f:
        NYSE_trading_holidays.add( datetime.datetime.strptime(line.strip(), "%Y-%m-%d").date() )

def is_nyse_holiday(year, month, day):
    date_obj = datetime.date(year, month, day)
    return date_obj in NYSE_trading_holidays

# Some hard-coded holidays:
# These dates had the same holiday name and day in 2015 and 2017
# according to Fidelity's list of holidays
# https://eresearch.fidelity.com/eresearch/markets_sectors/global/holidayCalendar.jhtml
# (I avoided duplicates, so boxing day is only listed in Canada, etc.)
#
# Multiple countries had extra easter-related holidays: holy Thursday, whit monday, but those
# seem difficult to code
#
# AUS
# Jan 26
#
# CAD
# Dec 26
#
# GER
# May 1
#
# JPY
# Jan 2
# May 4
# May 5
# Nov 3
# Nov 23
#
# NZD
# Feb 6
#
# NOK
#
# GBP
#
# CHF
#
# 

def is_fixed_holiday(year_ignored, month, day):
    if month==1 and day==26 :
        return True
    if month==12 and day==26 :
        return True
    if month==5 and day==1 :
        return True
    if month==1 and day==2 :
        return True
    if month==5 and day==4 :
        return True
    if month==5 and day==5 :
        return True
    if month==11 and day==3 :
        return True
    if month==11 and day==23 :
        return True
    if month==2 and day==6 :
        return True
    return False


def is_holiday(year, month, day):
    return is_fixed_holiday(year, month, day) or is_nyse_holiday(year, month, day) or is_easter_holiday(year, month, day)
    

random.seed(31415926)

def pick_day(year, month):
    while True:
        # tuple assignment - first element is the day of the week of the first day
        (ignored, days_in_month) = calendar.monthrange(year, month)
        day = random.randint(1, days_in_month)
        date_obj = datetime.date(year, month, day)
        # Monday is 0, ..., Saturday is 5, Sunday is 6
        if date_obj.weekday() >= 5:
            continue
        if is_holiday(year, month, day):
            continue
        return day

i = 0
while True:
    year = 1998 + (i // 12)
    month = 1 + (i % 12)   # offset of 1
    if year >= 2017 and month >= 4:
        break

    day = pick_day(year, month)
    print "%d-%d-%d" % (year, month, day)
    i += 1
    

