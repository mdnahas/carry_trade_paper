#!/usr/bin/python

# division returns float always; use // for integer division
from __future__ import division
from __future__ import print_function

import csv
import sys
import os
import math
import datetime
import calendar
import unittest

import price_and_yield_lib as pyl



class SwapRateLibrary:
    def __init__(self):
        # currency -> date -> duration -> rate
        self.swap_rate = dict()
        self.swap_rate_RAW = dict()
        self.forward = dict()
        self.spot = dict()
        self.govt_rate = dict()
        self.xcbs_rate = dict()
                    
    def insert_swap_rate(self, currency, date, duration, rate):
        if currency == "DEM":
            currency = "EUR"

        # Swap rate is calculated differently from our yields.
        if duration >= 1:
            common_rate = pyl.BondLibrary.commonYieldFromSwapYield(currency, int(duration), date, rate)
        else:
            print("NOT DOING PROPER CONVERSION FOR LIBOR YIELDS", file=sys.stderr)
            common_rate = rate
                    
        if currency not in self.swap_rate:
            self.swap_rate[ currency ] = dict()
        if date not in self.swap_rate[ currency ]:
            self.swap_rate[ currency ][ date ] = dict()
        if duration not in self.swap_rate[ currency ][ date ]:
            self.swap_rate[ currency ][ date ][ duration ] = common_rate
        else:
            raise Exception("Tried to insert swap rate twice: " + currency + "," + str(date) + "," + str(duration) + "=" + str(rate))


    def insert_swap_rate_RAW(self, currency, date, duration, rate):
        if currency == "DEM":
            currency = "EUR"

        if currency not in self.swap_rate_RAW:
            self.swap_rate_RAW[ currency ] = dict()
        if date not in self.swap_rate_RAW[ currency ]:
            self.swap_rate_RAW[ currency ][ date ] = dict()
        if duration not in self.swap_rate_RAW[ currency ][ date ]:
            self.swap_rate_RAW[ currency ][ date ][ duration ] = rate
        else:
            raise Exception("Tried to insert swap rate RAW twice: " + currency + "," + str(date) + "," + str(duration) + "=" + str(rate))


    
    def insert_forward_points(self, currency, date, duration, points):
        # Can't do this here.  One is DEM/USD, the other is USD/EUR
        #if currency == "DEM":
        #    currency = "EUR"

        if currency not in self.forward:
            self.forward[ currency ] = dict()
        if date not in self.forward[ currency ]:
            self.forward[ currency ][ date ] = dict()
        if duration not in self.forward[ currency ][ date ]:
            self.forward[ currency ][ date ][ duration ] = points
        else:
            raise Exception("Tried to insert forward twice: " + currency + "," + str(date) + "," + str(duration) + "=" + str(points))

                
    def insert_spot(self, currency, date, exchange_rate):
        # Can't do this here.  One is DEM/USD, the other is USD/EUR
        #if currency == "DEM":
        #    currency = "EUR"

        if currency not in self.spot:
            self.spot[ currency ] = dict()
        if date not in self.spot[ currency ]:
            self.spot[ currency ][ date ] = exchange_rate
        else:
            old_value = self.spot[ currency ][ date ]
            if old_value != exchange_rate:
                print("Tried to insert spot twice: " + currency + "," + str(date) + "=" + str(exchange_rate) + " with old value " + str(old_value), file=sys.stderr)
                #raise Exception("Tried to insert spot twice: " + currency + "," + str(date) + "=" + str(exchange_rate) + " with old value " + str(old_value))


    def insert_govt_rate(self, currency, date, duration, rate):
        if currency == "DEM":
            currency = "EUR"

        if currency not in self.govt_rate:
            self.govt_rate[ currency ] = dict()
        if date not in self.govt_rate[ currency ]:
            self.govt_rate[ currency ][ date ] = dict()
        if duration not in self.govt_rate[ currency ][ date ]:
            self.govt_rate[ currency ][ date ][ duration ] = rate
        else:
            raise Exception("Tried to insert govt rate twice: " + currency + "," + str(date) + "," + str(duration) + "=" + str(rate))


    def insert_xcbs_rate(self, currency, date, duration, rate):
        if currency == "DEM":
            currency = "EUR"

        if currency not in self.xcbs_rate:
            self.xcbs_rate[ currency ] = dict()
        if date not in self.xcbs_rate[ currency ]:
            self.xcbs_rate[ currency ][ date ] = dict()
        if duration not in self.xcbs_rate[ currency ][ date ]:
            self.xcbs_rate[ currency ][ date ][ duration ] = rate
        else:
            raise Exception("Tried to insert xcbs rate twice: " + currency + "," + str(date) + "," + str(duration) + "=" + str(rate))


    # Creates a dictionary for a given duration
    # that maps bloomberg tickers to
    # currency and a constant
    SPOT = 0
    FORWARD = 1
    SWAP_RATE = 2
    XCBS_RATE = 3
    
    def create_ticker_dict(self, duration):
        result = dict()
        major_currencies = ["AUD", "CAD", "CHF", "DEM", "EUR", "GBP", "JPY", "NOK", "NZD", "SEK", "USD"]
        for curr in major_currencies:
            result[ curr + " curncy"] = (curr, self.SPOT)
            result[ curr + str(int(duration)) + "Y curncy"] = (curr, self.FORWARD)

        swaps_roots = ["ADSWAP", "CDSW", "SFSW", "DMSW", "EUSA", "BPSW", "JYSW", "NKSW", "NDSWAP", "SKSW", "USSWAP"]
        for i in range(0, len(major_currencies)):
            result[ swaps_roots[ i ] + str(int(duration)) + " curncy"] = ( major_currencies[ i ], self.SWAP_RATE)

        xcbs_roots = ["ADBS", "CDBS", "SFBS", "DMBS", "EUBS", "BPBS", "JYBS", "NKBS", "NDBS", "SKBS"]  # No USBS
        for i in range(0, len(xcbs_roots)):
            result[ xcbs_roots[ i ] + str(int(duration)) + " curncy"] = ( major_currencies[ i ], self.XCBS_RATE)
                        
        return result


    def create_ticker_dict_monthly(self, duration_in_months):
        if duration_in_months >= 10:
            raise Exception("create_ticker_dict_monthly doesn't support multi-digit duration_in_months")
        
        result = dict()
        major_currencies = ["AUD", "CAD", "CHF", "DEM", "EUR", "GBP", "JPY", "NOK", "NZD", "SEK", "USD"]
        for curr in major_currencies:
            result[ curr + " curncy"] = (curr, self.SPOT)
            result[ curr + str(duration_in_months) + "M curncy"] = (curr, self.FORWARD)

        libor_roots = ["BBSW", "CDOR0", "SF000", "DM000", "EUR00", "BP000", "JY000", "NIBOR", "NDBB", "STBB", "US000"]
        for i in range(0, len(major_currencies)):
            if major_currencies[i] == "CAD":
                lr = libor_roots[i] + str(duration_in_months)
            else:
                lr = libor_roots[i] + str(duration_in_months) + "M"
            result[ lr + " curncy"] = ( major_currencies[ i ], self.SWAP_RATE)
            
        return result
            

    # This is the exchange rate from Deutche Marks to Euros on the day it was fixed.
    EUR_PER_DEM_EXCHANGE_RATE = 1.0/1.95583

    # returns as currency/USD
    # Will return EUR/USD for requests with "DEM"
    def get_spot(self, currency, date):
        if currency == "USD":
            return 1.0

        if currency == "EUR" and (currency not in self.spot or date not in self.spot[currency]):
            currency = "DEM"

        try:
            fx_rate = self.spot[currency][date]

            # These currencies are USD/EUR instead of EUR/USD.  Must invert result        
            invert = (currency == "EUR" or currency == "GBP" or currency == "AUD" or currency == "NZD")
            if invert:
                fx_rate = 1.0/fx_rate

            # need to return EUR
            if currency == "DEM":
                fx_rate *= self.EUR_PER_DEM_EXCHANGE_RATE
            
            return fx_rate
        except KeyError:
            raise Exception("get_spot could not find " + currency + " on " + str(date))
        


    # returns as currency/USD
    # Will return EUR/USD for requests with "DEM"
    def get_forward_price(self, currency, date, duration):
        if currency == "USD":
            return 1.0
                
        if currency=="EUR" and (currency not in self.forward or date not in self.forward[currency]):
            currency = "DEM"

        try:
            fwd_points = self.forward[currency][date][duration]
            spot_rate  = self.spot[currency][date]

            factor = 10000.0
            if currency == "JPY":
                factor = 100.0

            fwd_price = spot_rate + fwd_points / factor
            
            invert = (currency == "EUR" or currency == "GBP" or currency == "AUD" or currency == "NZD")
            if invert:
                fwd_price = 1.0/fwd_price

            # need to return EUR
            if currency == "DEM":
                fwd_price *= self.EUR_PER_DEM_EXCHANGE_RATE
                
            return fwd_price
        except KeyError:
            raise Exception("get_forward_price could not find " + currency + " on " + str(date) + " for " + str(duration) + " years")
        
        
            
    # Duration here can be a float, so 4.5 years
    def get_swap_rate(self, currency, date, duration):
        if currency == "DEM":
            currency = "EUR"
        
        # quick exact lookup
        try:
            if duration in self.swap_rate[ currency ][ date ]:
                return self.swap_rate[ currency ][ date ][ duration ]
        except KeyError:
            # do nothing ... report errors below.
            pass

        # look up rate at year boundaries.
        # then do a linear interpolation.
        if duration < 1.0:
            return float("NaN")
        elif duration <= 10.0:
            duration_fl = int(duration)
            duration_cl = int(math.ceil(duration))
        elif duration <= 12.0:
            duration_fl = 10
            duration_cl = 12
        elif duration <= 15.0:
            duration_fl = 12
            duration_cl = 15
        elif duration <= 20.0:
            duration_fl = 15
            duration_cl = 20
        else:
            return float("NaN")
            

        try:
            rate_fl = self.swap_rate[ currency ][ date ][ duration_fl ]
            rate_cl = self.swap_rate[ currency ][ date ][ duration_cl ]

            if duration_fl == duration_cl:
                return rate_fl
            else:
                return ((duration_cl - duration)*rate_fl + (duration - duration_fl)*rate_cl) / (duration_cl - duration_fl)
        except KeyError:
            print("Unable to find swap rate with: " + currency + "," + str(date) + "," + str(duration_fl) + " or " + str(duration_cl), file=sys.stderr)
            return float("NaN")
        

    # Duration must be an int 
    def get_swap_rate_RAW(self, currency, date, duration):
        if currency == "DEM":
            currency = "EUR"

        try:
            rate = self.swap_rate[ currency ][ date ][ duration ]
            return rate
        except KeyError:
            print("Unable to find swap rate with: " + currency + "," + str(date) + "," + str(duration), file=sys.stderr)
            return float('NaN')


    # Duration here can be a float, so 4.5 years
    def get_govt_rate(self, currency, date, duration):
        if currency == "DEM":
            currency = "EUR"

        # quick integer lookup
        try:
            if duration in self.govt_rate[ currency ][ date ]:
                return self.govt_rate[ currency ][ date ][ duration ]
        except KeyError:
            # do nothing ... report errors below.
            pass
        
        # look up rate at year boundaries.
        # then do a linear interpolation.
        if duration < 1.0:
            return float("NaN")
        elif duration <= 2.0:
            duration_fl = 1
            duration_cl = 2
        elif duration <= 3.0:
            duration_fl = 2
            duration_cl = 3
        elif duration <= 5.0:
            duration_fl = 3
            duration_cl = 5
        elif duration <= 7.0:
            duration_fl = 5
            duration_cl = 7
        elif duration <= 10.0:
            duration_fl = 7
            duration_cl = 10
        elif duration <= 20.0:
            duration_fl = 10
            duration_cl = 20
        else:
            return float("NaN")

        # AUD, NOK, and NZD have no 7 year 
        if duration_fl == 7 and (currency == "AUD" or currency == "NOK" or currency == "NZD"):
            duration_fl = 5
        if duration_cl == 7 and (currency == "AUD" or currency == "NOK" or currency == "NZD"):
            duration_cl = 10
        # NZD and SEK have no 3 year 
        if duration_fl == 3 and (currency == "NZD" or currency == "SEK"):
            duration_fl = 2
        if duration_cl == 3 and (currency == "NZD" or currency == "SEK"):
            duration_cl = 5
        # NOK has no 2 year
        if duration_fl == 2 and (currency == "NOK"):
            duration_fl = 1
        if duration_cl == 2 and (currency == "NOK"):
            duration_cl = 3
            
            
        try:
            rate_fl = self.govt_rate[ currency ][ date ][ duration_fl ]
            rate_cl = self.govt_rate[ currency ][ date ][ duration_cl ]

            if duration_fl == duration_cl:
                return rate_fl
            else:
                return ((duration_cl - duration)*rate_fl + (duration - duration_fl)*rate_cl) / (duration_cl - duration_fl)
        except KeyError:
            print("Unable to find govt rate with: " + currency + "," + str(date) + "," + str(duration_fl) + " or " + str(duration_cl), file=sys.stderr)
            return float("NaN")
        
        

    # Duration here can be a float, so 4.5 years
    def get_xcbs_rate(self, currency, date, duration):
        if currency == "USD":
            return 0.0
        
        if currency == "DEM":
            currency = "EUR"
        
        # quick exact lookup
        try:
            if duration in self.xcbs_rate[ currency ][ date ]:
                return self.xcbs_rate[ currency ][ date ][ duration ]
        except KeyError:
            # do nothing ... report errors below.
            pass

        # look up rate at year boundaries.
        # then do a linear interpolation.
        if duration < 1.0:
            return float("NaN")
        elif duration <= 10.0:
            duration_fl = int(duration)
            duration_cl = int(math.ceil(duration))
        elif duration <= 12.0:
            duration_fl = 10
            duration_cl = 12
        elif duration <= 15.0:
            duration_fl = 12
            duration_cl = 15
        elif duration <= 20.0:
            duration_fl = 15
            duration_cl = 20
        else:
            return float("NaN")
            

        try:
            rate_fl = self.xcbs_rate[ currency ][ date ][ duration_fl ]
            rate_cl = self.xcbs_rate[ currency ][ date ][ duration_cl ]

            if duration_fl == duration_cl:
                return rate_fl
            else:
                return ((duration_cl - duration)*rate_fl + (duration - duration_fl)*rate_cl) / (duration_cl - duration_fl)
        except KeyError:
            print("Unable to find xcbs rate with: " + currency + "," + str(date) + "," + str(duration_fl) + " or " + str(duration_cl), file=sys.stderr)
            return float("NaN")
        


                        
    # Duration is a integer years
    # Uses continuous compounding.
    def get_implied_USD_rate(self, currency, date, duration):
        # foc is foreign currency
        foc_now_per_usd_now = self.get_spot(currency, date)
        foc_then_per_usd_then = self.get_forward_price(currency, date, duration)
        foc_interest_rate = self.get_swap_rate(currency, date, duration)
        #foc_then_per_foc_now = (1.0 + foc_interest_rate)**duration
        foc_then_per_foc_now = math.exp(foc_interest_rate * duration)
        usd_then_per_usd_now = foc_now_per_usd_now * foc_then_per_foc_now / foc_then_per_usd_then
        #usd_interest_rate = usd_then_per_usd_now**(1.0/duration) - 1.0
        usd_interest_rate = math.log(usd_then_per_usd_now)/duration
        return usd_interest_rate


    # Duration is a integer years
    # Uses continuous compounding.
    def get_implied_rate_from_USD(self, currency, date, duration):
        # foc is foreign currency
        foc_now_per_usd_now = self.get_spot(currency, date)
        foc_then_per_usd_then = self.get_forward_price(currency, date, duration)
        usd_interest_rate = self.get_swap_rate("USD", date, duration)
        #usd_then_per_usd_now = (1.0 + usd_interest_rate)**duration
        usd_then_per_usd_now = math.exp(usd_interest_rate * duration)
        foc_then_per_foc_now = (1.0/foc_now_per_usd_now) * usd_then_per_usd_now * foc_then_per_usd_then
        #foc_interest_rate = foc_then_per_foc_now**(1.0/duration) - 1.0
        foc_interest_rate = math.log(foc_then_per_foc_now)/duration
        return foc_interest_rate

    def get_implied_forward_price_from_XCBS(self, currency, date, duration):
        # foc is foreign currency
        foc_now_per_usd_now = self.get_spot(currency, date)

        # BNS Paribas and Seeking Alpha says that this kind of relationship exists:
        #    F = S * (1 + swap_USD) / (1 + swap_EUR + xcbs)
        # !!! But that's for EUR rate, which is inverted.
        # It is: short 1 UDS, long SPOT rate in EUR.
        #        sell USD swap, buy EUR swap, buy XCBS
        #        LIBOR parts cancel.
        #        Fixed parts in USD are (1 + swap_USD)^duration
        #        Fixed parts in EUR are (1 + swap_EUR + XCBS)^duration
        #        ratio at time "duration" gets us the forward exchange rate.
        usd_swap_rate = self.get_swap_rate("USD", date, duration)
        foc_swap_rate = self.get_swap_rate(currency, date, duration)
        xcbs_rate = self.get_xcbs_rate(currency, date, duration)
        return foc_now_per_usd_now * math.exp((foc_swap_rate + xcbs_rate) * duration) / math.exp(usd_swap_rate * duration)
        

    
# My definition
    def get_CIP_basis_DEF1(self, currency, date, duration):
        return( self.get_swap_rate("USD", date, duration) - self.get_implied_USD_rate(currency, date, duration))
            
# Ends up being same as my definition!
    def get_CIP_basis_DEF2(self, currency, date, duration):
        return( self.get_implied_rate_from_USD(currency, date, duration) - self.get_swap_rate(currency, date, duration))

# Liao's definition
    def get_CIP_basis_LIAO1(self, currency, date, duration):
        S = self.get_spot(currency, date)
        F = self.get_forward_price(currency, date, duration)
        r_foreign = self.get_swap_rate_RAW(currency, date, duration)
        r_USD = self.get_swap_rate_RAW("USD", date, duration)
        return ((F/S)*(1 + r_USD) - (1 + r_foreign))

# Liao with annualization
    def get_CIP_basis_LIAO2(self, currency, date, duration):
        S = self.get_spot(currency, date)
        F = self.get_forward_price(currency, date, duration)
        r_foreign = self.get_swap_rate_RAW(currency, date, duration)
        r_USD = self.get_swap_rate_RAW("USD", date, duration)
        return ((F/S)*((1 + r_USD)**duration))**(1.0/duration) - (1 + r_foreign)

# Liao with discounting approximation
    def get_CIP_basis_LIAO3(self, currency, date, duration):
        S = self.get_spot(currency, date)
        F = self.get_forward_price(currency, date, duration)
        r_foreign = self.get_swap_rate_RAW(currency, date, duration)
        r_USD = self.get_swap_rate_RAW("USD", date, duration)
        return ((F/S)*(1 + duration * r_USD) - 1)/duration - r_foreign



    # Duration is a integer years
    # Uses continuous compounding.
    def get_implied_rate_from_USD_GOVT(self, currency, date, duration):
        # foc is foreign currency
        foc_now_per_usd_now = self.get_spot(currency, date)
        foc_then_per_usd_then = self.get_forward_price(currency, date, duration)
        usd_interest_rate = self.get_govt_rate("USD", date, duration)
        #usd_then_per_usd_now = (1.0 + usd_interest_rate)**duration
        usd_then_per_usd_now = math.exp(usd_interest_rate * duration)
        foc_then_per_foc_now = (1.0/foc_now_per_usd_now) * usd_then_per_usd_now * foc_then_per_usd_then
        #foc_interest_rate = foc_then_per_foc_now**(1.0/duration) - 1.0
        foc_interest_rate = math.log(foc_then_per_foc_now)/duration
        return foc_interest_rate
    
# Same as DEF2, uses govt rates
    def get_CIP_basis_GOVT2(self, currency, date, duration):
        return( self.get_implied_rate_from_USD_GOVT(currency, date, duration) - self.get_govt_rate(currency, date, duration))


    # Duration is a integer years
    # Uses continuous compounding.
    def get_implied_rate_from_USD_XCBS_GOVT(self, currency, date, duration):
        # foc is foreign currency
        foc_now_per_usd_now = self.get_spot(currency, date)

        # THIS IS THE DIFFERENCE:
        foc_then_per_usd_then = self.get_implied_forward_price_from_XCBS(currency, date, duration)
        
        usd_interest_rate = self.get_govt_rate("USD", date, duration)
        #usd_then_per_usd_now = (1.0 + usd_interest_rate)**duration
        usd_then_per_usd_now = math.exp(usd_interest_rate * duration)
        foc_then_per_foc_now = (1.0/foc_now_per_usd_now) * usd_then_per_usd_now * foc_then_per_usd_then
        #foc_interest_rate = foc_then_per_foc_now**(1.0/duration) - 1.0
        foc_interest_rate = math.log(foc_then_per_foc_now)/duration
        return foc_interest_rate
    
# Same as DEF2, uses govt rates
    def get_CIP_basis_XCBS_GOVT2(self, currency, date, duration):
        return( self.get_implied_rate_from_USD_XCBS_GOVT(currency, date, duration) - self.get_govt_rate(currency, date, duration))



    # Duration is a integer years
    # Uses continuous compounding.
    def get_implied_rate_from_ANY(self, ref_curr, ref_rate, currency, date, duration):
        # foc is foreign currency
        if ref_curr == "USD":
            foc_now_per_ref_now = self.get_spot(currency, date)
        else:
            foc_now_per_usd_now = self.get_spot(currency, date)
            ref_now_per_usd_now = self.get_spot(ref_curr, date)
            foc_now_per_ref_now = foc_now_per_usd_now / ref_now_per_usd_now
        if ref_curr == "USD":
            foc_then_per_ref_then = self.get_forward_price(currency, date, duration)
        else:
            foc_then_per_usd_then = self.get_forward_price(currency, date, duration)
            ref_then_per_usd_then = self.get_forward_price(ref_curr, date, duration)
            foc_then_per_ref_then = foc_then_per_usd_then / ref_then_per_usd_then
        #ref_then_per_ref_now = (1.0 + ref_rate)**duration
        ref_then_per_ref_now = math.exp(ref_rate * duration)
        foc_then_per_foc_now = (1.0/foc_now_per_ref_now) * ref_then_per_ref_now * foc_then_per_ref_then
        #foc_interest_rate = foc_then_per_foc_now**(1.0/duration) - 1.0
        foc_interest_rate = math.log(foc_then_per_foc_now)/duration
        return foc_interest_rate
    
# Same as DEF2, uses govt rates
    def get_CIP_basis_GOVT_ANY2(self, ref_curr, currency, date, duration):
        ref_rate = self.get_govt_rate(ref_curr, date, duration)
        curr_rate = self.get_govt_rate(currency, date, duration)
        return( self.get_implied_rate_from_ANY(ref_curr, ref_rate, currency, date, duration) - curr_rate)

    def get_CIP_basis_SWAP_ANY2(self, ref_curr, currency, date, duration):
        ref_rate = self.get_swap_rate(ref_curr, date, duration)
        curr_rate = self.get_swap_rate(currency, date, duration)
        return( self.get_implied_rate_from_ANY(ref_curr, ref_rate, currency, date, duration) - curr_rate)

    def get_CIP_basis_XCBS_ANY2(self, ref_curr, currency, date, duration):
        if ref_curr != "USD":
            raise Exception("XCBS only supports ref_curr=USD, not: " + ref_curr)
        return( self.get_xcbs_rate(currency, date, duration) )
                

    def get_Method2_factor(self, ref_curr, currency, date, duration):
        # foc is foreign currency
        if ref_curr == "USD":
            foc_now_per_ref_now = self.get_spot(currency, date)
        else:
            foc_now_per_usd_now = self.get_spot(currency, date)
            ref_now_per_usd_now = self.get_spot(ref_curr, date)
            foc_now_per_ref_now = foc_now_per_usd_now / ref_now_per_usd_now
        if ref_curr == "USD":
            foc_then_per_ref_then = self.get_implied_forward_price_from_XCBS(currency, date, duration)
        else:
            foc_then_per_usd_then = self.get_implied_forward_price_from_XCBS(currency, date, duration)
            ref_then_per_usd_then = self.get_implied_forward_price_from_XCBS(ref_curr, date, duration)
            foc_then_per_ref_then = foc_then_per_usd_then / ref_then_per_usd_then

        # This is log(fwd / spot) / duration, which is the correction factor
        # when using continuously compounding interest
        return math.log( foc_then_per_ref_then / foc_now_per_ref_now ) / duration
        
    

    # Duration is a integer years
    # Uses continuous compounding.
    def get_implied_rate_from_USD_XCBS(self, usd_interest_rate, currency, date, duration):
        # foc is foreign currency
        foc_now_per_usd_now = self.get_spot(currency, date)

        # THIS IS THE DIFFERENCE:
        foc_then_per_usd_then = self.get_implied_forward_price_from_XCBS(currency, date, duration)
        
        #usd_then_per_usd_now = (1.0 + usd_interest_rate)**duration
        usd_then_per_usd_now = math.exp(usd_interest_rate * duration)
        foc_then_per_foc_now = (1.0/foc_now_per_usd_now) * usd_then_per_usd_now * foc_then_per_usd_then
        #foc_interest_rate = foc_then_per_foc_now**(1.0/duration) - 1.0
        foc_interest_rate = math.log(foc_then_per_foc_now)/duration
        return foc_interest_rate
    
# Same as DEF2, uses govt rates
    def get_CIP_basis_given_rates(self, usd_interest_rate, foc_interest_rate, currency, date, duration):
        return(self.get_implied_rate_from_USD_XCBS(usd_interest_rate, currency, date, duration) - foc_interest_rate)



    def read_swap_file(self, duration, filename):
        with open(filename, 'rb') as csv_infile:
            csv_reader = csv.reader(csv_infile)
        
            # no header

            # create the mapping from Bloomberg's tickers to internal naming
            if duration >= 1:
                ticker_dict = self.create_ticker_dict(duration)
            else:
                ticker_dict = self.create_ticker_dict_monthly(int(round(duration*12)))
                
            for row in csv_reader:
                # ticker, date, yield
                bloomberg_ticker = row[0]
                if row[1][4] == "-":
                    date = datetime.datetime.strptime( row[1], "%Y-%m-%d").date()
                else:
                    date = datetime.datetime.strptime( row[1], "%m/%d/%Y").date()
                if row[2] == "" or row[2] == "#N/A N/A":
                    continue
                yield_or_price = float(row[2])

                if bloomberg_ticker not in ticker_dict:
                    raise Exception("Unable to find ticker in dictionary: " + bloomberg_ticker)
                (curr, kind) = ticker_dict[ bloomberg_ticker ]

                if kind == self.XCBS_RATE:
                    # notice, need to scale basis points by 10000.0
                    self.insert_xcbs_rate(curr, date, duration, yield_or_price / 10000.0)
                elif kind == self.SWAP_RATE:
                    # notice, need to scale percent by 100.0
                    self.insert_swap_rate(curr, date, duration, yield_or_price / 100.0)
                    self.insert_swap_rate_RAW(curr, date, duration, yield_or_price / 100.0)
                elif kind == self.FORWARD:
                    self.insert_forward_points(curr, date, duration, yield_or_price)
                elif kind == self.SPOT:
                    self.insert_spot(curr, date, yield_or_price)
                else:
                    raise Exception("Kind had illegal value " + str(kind))


    def read_govt_file(self, duration, filename):
        with open(filename, 'rb') as csv_infile:
            csv_reader = csv.reader(csv_infile)
        
            # no header

            for row in csv_reader:
                # ticker, date, yield
                ticker = row[0]
                date = datetime.datetime.strptime( row[1], "%Y-%m-%d").date()
                if row[2] == "":
                    continue
                yield_or_price = float(row[2])

                # ticker example: "USD1 govt"
                currency = ticker[0:3]
                duration = int(ticker[3:-5])
                
                self.insert_govt_rate(currency, date, duration, yield_or_price / 100.0)

                
    def load_files(self, swap_dir_name, govt_dir_name):
        if swap_dir_name != "":
            for i in range(2, 11):
                self.read_swap_file(i, os.path.join(swap_dir_name, "currencies" + str(i) + "Y.csv"))
            self.read_swap_file(12, os.path.join(swap_dir_name, "currencies" + str(12) + "Y.csv"))
            self.read_swap_file(15, os.path.join(swap_dir_name, "currencies" + str(15) + "Y.csv"))
            self.read_swap_file(20, os.path.join(swap_dir_name, "currencies" + str(20) + "Y.csv"))
            # Notice - first file is faked data, from 12M files
            # Loaded after, so that spot price comes from other files that I trust more.
            #self.read_swap_file(1, os.path.join(swap_dir_name, "currencies1Y_faked.csv"))
            self.read_swap_file(1, os.path.join(swap_dir_name, "currencies1Y.csv"))
        if govt_dir_name != "":
            for i in [1, 2, 3, 5, 7, 10, 20]:
                self.read_govt_file(i, os.path.join(govt_dir_name, "govt" + str(i) + ".csv"))
        
    
class TestRatingsMethods(unittest.TestCase):

    def test_swap_insert_get(self):
        x = SwapRateLibrary()
        x.insert_swap_rate("AUD", datetime.date(2000,1,1), 5, 0.03125)
        expected = pyl.BondLibrary.commonYieldFromSwapYield("AUD", 5, datetime.date(2000,1,1), 0.03125)
        self.assertAlmostEqual(expected, x.get_swap_rate("AUD", datetime.date(2000,1,1), 5))

    def test_swap_get_fails(self):
        x = SwapRateLibrary()
        self.assertTrue( math.isnan(x.get_swap_rate("AUD", datetime.date(2000,1,1), 5)))

    def test_swap_insert_twice(self):
        with self.assertRaises(Exception):
            x = SwapRateLibrary()
            x.insert_swap_rate("AUD", datetime.date(2000,1,1), 5, 0.03125)
            x.insert_swap_rate("AUD", datetime.date(2000,1,1), 5, 0.03125)
    
    def test_swap_insert_get_linear(self):
        x = SwapRateLibrary()
        x.insert_swap_rate("AUD", datetime.date(2000,1,1), 4, 0.03125)
        x.insert_swap_rate("AUD", datetime.date(2000,1,1), 5, 0.0625)
        a = pyl.BondLibrary.commonYieldFromSwapYield("AUD", 4, datetime.date(2000,1,1), 0.03125)
        b = pyl.BondLibrary.commonYieldFromSwapYield("AUD", 5, datetime.date(2000,1,1), 0.0625)
        self.assertAlmostEqual(0.75*a + 0.25*b, x.get_swap_rate("AUD", datetime.date(2000,1,1), 4.25))
        self.assertAlmostEqual(0.25*a + 0.75*b, x.get_swap_rate("AUD", datetime.date(2000,1,1), 4.75))

    def test_swap_insert_get_linear2(self):
        x = SwapRateLibrary()
        x.insert_swap_rate("AUD", datetime.date(2000,1,1), 10, 0.05)
        x.insert_swap_rate("AUD", datetime.date(2000,1,1), 12, 0.10)
        x.insert_swap_rate("AUD", datetime.date(2000,1,1), 15, 0.05)
        x.insert_swap_rate("AUD", datetime.date(2000,1,1), 20, 0.10)
        a = pyl.BondLibrary.commonYieldFromSwapYield("AUD", 10, datetime.date(2000,1,1), 0.05)
        b = pyl.BondLibrary.commonYieldFromSwapYield("AUD", 12, datetime.date(2000,1,1), 0.10)
        c = pyl.BondLibrary.commonYieldFromSwapYield("AUD", 15, datetime.date(2000,1,1), 0.05)
        d = pyl.BondLibrary.commonYieldFromSwapYield("AUD", 20, datetime.date(2000,1,1), 0.10)
        self.assertAlmostEqual(a, x.get_swap_rate("AUD", datetime.date(2000,1,1), 10))
        self.assertAlmostEqual(b, x.get_swap_rate("AUD", datetime.date(2000,1,1), 12))
        self.assertAlmostEqual(c, x.get_swap_rate("AUD", datetime.date(2000,1,1), 15))
        self.assertAlmostEqual(d, x.get_swap_rate("AUD", datetime.date(2000,1,1), 20))
        self.assertTrue(math.isnan(x.get_swap_rate("AUD", datetime.date(2000,1,1), 20.5)))
        self.assertAlmostEqual(0.75*a + 0.25*b, x.get_swap_rate("AUD", datetime.date(2000,1,1), 10.5))
        self.assertAlmostEqual(0.25*a + 0.75*b, x.get_swap_rate("AUD", datetime.date(2000,1,1), 11.5))
        self.assertAlmostEqual(b*2.0/3.0 + c*1.0/3.0, x.get_swap_rate("AUD", datetime.date(2000,1,1), 13))
        self.assertAlmostEqual(b*1.0/3.0 + c*2.0/3.0, x.get_swap_rate("AUD", datetime.date(2000,1,1), 14))
        self.assertAlmostEqual(c*4.0/5.0 + d*1.0/5.0, x.get_swap_rate("AUD", datetime.date(2000,1,1), 16))
        self.assertAlmostEqual(c*3.0/5.0 + d*2.0/5.0, x.get_swap_rate("AUD", datetime.date(2000,1,1), 17))
        self.assertAlmostEqual(c*2.0/5.0 + d*3.0/5.0, x.get_swap_rate("AUD", datetime.date(2000,1,1), 18))
        self.assertAlmostEqual(c*1.0/5.0 + d*4.0/5.0, x.get_swap_rate("AUD", datetime.date(2000,1,1), 19))

        
    # SLOW TEST
    def test_load_file(self):
        x = SwapRateLibrary()
        year = 3
        x.read_swap_file(year, "raw_data/currency_prices/currencies" + str(year) + "Y.csv")
        expected = pyl.BondLibrary.commonYieldFromSwapYield("GBP", 3, datetime.date(1998,2,12), 0.06785)
        self.assertAlmostEqual(expected, x.get_swap_rate("GBP", datetime.date(1998,2,12), 3))

    def test_spot_insert_get(self):
        x = SwapRateLibrary()
        x.insert_spot("CHF", datetime.date(2000,1,1), 1.5)
        self.assertAlmostEqual(1.5, x.get_spot("CHF", datetime.date(2000,1,1)))
        # AUD inverts
        x.insert_spot("AUD", datetime.date(2000,1,1), 1.5)
        self.assertAlmostEqual(1/1.5, x.get_spot("AUD", datetime.date(2000,1,1)))
        # GBP inverts
        x.insert_spot("GBP", datetime.date(2000,1,1), 2.0)
        self.assertAlmostEqual(.5, x.get_spot("GBP", datetime.date(2000,1,1)))
        # EUR inverts
        x.insert_spot("EUR", datetime.date(2000,1,1), 2.0)
        self.assertAlmostEqual(.5, x.get_spot("EUR", datetime.date(2000,1,1)))
        # EUR will go to DEM 
        x.insert_spot("DEM", datetime.date(1999,1,1), 2.0)
        self.assertAlmostEqual(2.0 * SwapRateLibrary.EUR_PER_DEM_EXCHANGE_RATE, x.get_spot("EUR", datetime.date(1999,1,1)))
                
    def test_forward_insert_get(self):
        x = SwapRateLibrary()
        x.insert_spot("CHF", datetime.date(2000,1,1), 2.0)
        x.insert_forward_points("CHF", datetime.date(2000,1,1), 1, 7)
        x.insert_forward_points("CHF", datetime.date(2000,1,1), 2, 33)
        self.assertAlmostEqual(2.0007, x.get_forward_price("CHF", datetime.date(2000,1,1), 1))
        self.assertAlmostEqual(2.0033, x.get_forward_price("CHF", datetime.date(2000,1,1), 2))
        # AUD inverts
        x.insert_spot("AUD", datetime.date(2000,1,1), 2.0)
        x.insert_forward_points("AUD", datetime.date(2000,1,1), 1, 7)
        x.insert_forward_points("AUD", datetime.date(2000,1,1), 2, 33)
        self.assertAlmostEqual(1/2.0007, x.get_forward_price("AUD", datetime.date(2000,1,1), 1))
        self.assertAlmostEqual(1/2.0033, x.get_forward_price("AUD", datetime.date(2000,1,1), 2))
        # JPY scales differently
        x.insert_spot("JPY", datetime.date(2000,1,1), 200.0)
        x.insert_forward_points("JPY", datetime.date(2000,1,1), 1, 7)
        x.insert_forward_points("JPY", datetime.date(2000,1,1), 2, 33)
        self.assertAlmostEqual(200.07, x.get_forward_price("JPY", datetime.date(2000,1,1), 1))
        self.assertAlmostEqual(200.33, x.get_forward_price("JPY", datetime.date(2000,1,1), 2))
        # GBP inverts
        x.insert_spot("GBP", datetime.date(2000,1,1), 2.0)
        x.insert_forward_points("GBP", datetime.date(2000,1,1), 1, 7)
        x.insert_forward_points("GBP", datetime.date(2000,1,1), 2, 33)
        self.assertAlmostEqual(1.0 / 2.0007, x.get_forward_price("GBP", datetime.date(2000,1,1), 1))
        self.assertAlmostEqual(1.0 / 2.0033, x.get_forward_price("GBP", datetime.date(2000,1,1), 2))
        # EUR inverts
        x.insert_spot("EUR", datetime.date(2000,1,1), 2.0)
        x.insert_forward_points("EUR", datetime.date(2000,1,1), 1, 7)
        x.insert_forward_points("EUR", datetime.date(2000,1,1), 2, 33)
        self.assertAlmostEqual(1.0 / 2.0007, x.get_forward_price("EUR", datetime.date(2000,1,1), 1))
        self.assertAlmostEqual(1.0 / 2.0033, x.get_forward_price("EUR", datetime.date(2000,1,1), 2))
        # EUR will go to DEM
        x.insert_spot("DEM", datetime.date(1999,1,1), 2.0)
        x.insert_forward_points("DEM", datetime.date(1999,1,1), 1, 7)
        x.insert_forward_points("DEM", datetime.date(1999,1,1), 2, 33)
        self.assertAlmostEqual(2.0007 * SwapRateLibrary.EUR_PER_DEM_EXCHANGE_RATE, x.get_forward_price("EUR", datetime.date(1999,1,1), 1))
        self.assertAlmostEqual(2.0033 * SwapRateLibrary.EUR_PER_DEM_EXCHANGE_RATE, x.get_forward_price("EUR", datetime.date(1999,1,1), 2))
        

    def test_govt(self):
        x = SwapRateLibrary()
        # Need two different durations to do fetch.
        x.insert_govt_rate("AUD", datetime.date(2000,1,1), 1, 2.0)
        x.insert_govt_rate("AUD", datetime.date(2000,1,1), 2, 3.0)
        x.insert_govt_rate("AUD", datetime.date(2000,1,1), 3, 5.0)
        self.assertEqual(2.0, x.get_govt_rate("AUD", datetime.date(2000,1,1), 1))
        self.assertEqual(3.0, x.get_govt_rate("AUD", datetime.date(2000,1,1), 2))

    def test_govt_missing_rates(self):
        x = SwapRateLibrary()
        # Need two different durations to do fetch.
        x.insert_govt_rate("AUD", datetime.date(2000,1,1), 5, 2.0)
        x.insert_govt_rate("AUD", datetime.date(2000,1,1), 10, 3.0)
        x.insert_govt_rate("NZD", datetime.date(2000,1,1), 2, 4.0)
        x.insert_govt_rate("NZD", datetime.date(2000,1,1), 5, 7.0)
        self.assertEqual(2.4, x.get_govt_rate("AUD", datetime.date(2000,1,1), 7))
        self.assertEqual(5.0, x.get_govt_rate("NZD", datetime.date(2000,1,1), 3))

    def test_govt_file(self):
        x = SwapRateLibrary()
        # Need two different durations to do fetch.
        x.read_govt_file(1, "data/Govt/govt1.csv")
        x.read_govt_file(2, "data/Govt/govt2.csv")
        self.assertEqual(.0530, x.get_govt_rate("USD", datetime.date(1998,4,6), 1))
        self.assertEqual(.0380, x.get_govt_rate("EUR", datetime.date(1998,4,6), 1))
        self.assertEqual(.0669, x.get_govt_rate("GBP", datetime.date(1998,4,6), 1))
        self.assertEqual(.00559, x.get_govt_rate("JPY", datetime.date(1998,4,6), 1))
        
    def test_govt_missing_rates_real_example(self):
        x = SwapRateLibrary()
        # Need two different durations to do fetch.
        x.insert_govt_rate("NZD", datetime.date(2009,2,4), 1, 3.16)
        x.insert_govt_rate("NZD", datetime.date(2009,2,4), 2, 3.40)
        x.insert_govt_rate("NZD", datetime.date(2009,2,4), 5, 3.81)
        x.insert_govt_rate("NZD", datetime.date(2009,2,4), 10, 4.52)
        self.assertEqual(3.81, x.get_govt_rate("NZD", datetime.date(2009,2,4), 5))

    def test_govt_missing_rates_real_example_files(self):
        x = SwapRateLibrary()
        x.read_govt_file(1, "data/Govt/govt1.csv")
        x.read_govt_file(2, "data/Govt/govt2.csv")
        x.read_govt_file(3, "data/Govt/govt3.csv")
        x.read_govt_file(5, "data/Govt/govt5.csv")
        x.read_govt_file(7, "data/Govt/govt7.csv")
        x.read_govt_file(10, "data/Govt/govt10.csv")
        self.assertEqual(.0381, x.get_govt_rate("NZD", datetime.date(2009,2,4), 5))
                        
    def test_xcbs_insert_get(self):
        x = SwapRateLibrary()
        x.insert_xcbs_rate("AUD", datetime.date(2000,1,1), 5, 0.03125)
        self.assertAlmostEqual(0.03125, x.get_xcbs_rate("AUD", datetime.date(2000,1,1), 5))

    def test_xcbs_get_fails(self):
        x = SwapRateLibrary()
        self.assertTrue( math.isnan(x.get_xcbs_rate("AUD", datetime.date(2000,1,1), 5)))

    def test_xcbs_relationship(self):
        x = SwapRateLibrary()
        year = 3
        x.read_swap_file(year, "raw_data/currency_prices/currencies" + str(year) + "Y.csv")
        x.read_govt_file(year, "data/Govt/govt" + str(year) + ".csv")

        currency = "GBP"
        duration = year
        date = datetime.date(2002,1,8)
        
        foc_now_per_usd_now = x.get_spot(currency, date)
        foc_then_per_usd_then = x.get_forward_price(currency, date, duration)
        usd_interest_rate = x.get_govt_rate("USD", date, duration)
        #usd_then_per_usd_now = (1.0 + usd_interest_rate)**duration
        usd_then_per_usd_now = math.exp(usd_interest_rate * duration)
        foc_then_per_foc_now = (1.0/foc_now_per_usd_now) * usd_then_per_usd_now * foc_then_per_usd_then
        #foc_interest_rate = foc_then_per_foc_now**(1.0/duration) - 1.0
        foc_interest_rate = math.log(foc_then_per_foc_now)/duration

        # If xcbs is negative (like now with EUR), then it should be more expensive
        # to borrow USD.  So, xcbs_rate is negative here.
        xcbs_rate = x.get_xcbs_rate(currency, date, duration)
        foc_swap_rate = x.get_swap_rate(currency, date, duration)
        usd_swap_rate = x.get_swap_rate("USD", date, duration)
        foc_interest_rate_xcbs = usd_interest_rate - xcbs_rate - usd_swap_rate + foc_swap_rate

        #print(str(usd_interest_rate))
        #print(str(xcbs_rate))
        #print(str(usd_swap_rate))
        #print(str(foc_swap_rate))
        
        self.assertAlmostEqual( foc_interest_rate, foc_interest_rate_xcbs, places=2)

    def test_xcbs_relationship2(self):
        x = SwapRateLibrary()
        year = 3
        x.read_swap_file(year, "raw_data/currency_prices/currencies" + str(year) + "Y.csv")
        x.read_govt_file(year, "data/Govt/govt" + str(year) + ".csv")

        currency = "GBP"
        duration = year
        date = datetime.date(2002,1,8)

        self.assertAlmostEqual( x.get_forward_price(currency, date, duration), x.get_implied_forward_price_from_XCBS(currency, date, duration), places=2)
                
if __name__ == '__main__':
    unittest.main()

