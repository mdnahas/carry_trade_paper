#!/usr/bin/python

# division returns float always; use // for integer division
from __future__ import division
from __future__ import print_function

import csv
import sys
import math
import datetime
import calendar
from sets import Set
import unittest

# Remember to run something like:
# export DYLD_LIBRARY_PATH=/opt/local/lib
import QuantLib as ql

major_currencies = Set(["AUD", "CAD", "CHF", "DEM", "EUR", "GBP", "JPY", "NOK", "NZD", "SEK", "USD"])

def isMajorCurrency(currency):
    return currency in major_currencies

def convertToQLDate(d):
    if type(d) is ql.Date:
        return d
    elif type(d) is datetime.date:
        return ql.Date(d.day, d.month, d.year)
    else:
        raise Exception("type of object was not date, it was: " + str(type(d)))



class BondLibrary:
    # Dictionary mapping ISIN to bond attributes
    bond_dict = dict()
    reverse_bond_dict = dict()
    
    #def __init__(self):
    #
    
    # Inserts a bond's description into the class's dictionary
    # isin is the string with the bond's identifier
    # coupon is fractional, e.g. 0.05 for a 5% bond
    # mat_date and issue_date are both ql.Date objects
    # currency a string with the 3 letter code, e.g. "USD"
    def insertBond(self, isin, coupon, mat_date, issue_date, currency, issuer, moody_rating, sandp_rating):
        if coupon < 0.0 or coupon > 1.0:
            raise Exception("coupon was outside expectation 0.0 to 1.0")
        # Check for duplicates
        reverse_key = (coupon, mat_date, currency, issuer)
        # if reverse_key in self.reverse_bond_dict:
        #     print("FOUND DUPLICATE BOND.  Original:" + str(self.reverse_bond_dict[reverse_key]) + " New:" + isin, file=sys.stderr)
            # Do not insert
            # return DO INSERT (FOR NOW) 
        # insert
        bond_desc = dict()
        bond_desc['coupon'] = coupon
        bond_desc['mat_date'] = mat_date
        bond_desc['issue_date'] = issue_date
        bond_desc['currency'] = currency
        bond_desc['issuer'] = issuer
        bond_desc['moody'] = moody_rating
        bond_desc['sandp'] = sandp_rating
        # insert it
        self.bond_dict[isin] = bond_desc
        self.reverse_bond_dict[reverse_key] = isin

    # Some European bonds only pay interest yearly.
    # http://www.nasdaqomx.com/digitalAssets/59/59908_Principal_Characteristics_and_Calculation_Conventions_of_Listed_Bonds_and_Bills.pdf
    # PROBABLY GOVERNMENTS! (from 2006)
    # says AUS, USD, GBP, CAD, and NZD pay twice yearly
    #      rest pay annually
    #
    # I know US298785DW34 is AUD and used Annual compounding
    # (but switching AUD caused more errors than it fixed!)
    @staticmethod
    def frequencyFromCurrency(currency):
        if currency == "EUR" or currency == "NOK" or currency == "SEK":
            return ql.Annual
        else:
            return ql.Semiannual

    # from Bloomberg's info pages for FIXED leg of swap
    # I'm not sure I can do anything about variable leg
    # (which is semi-annual, except quarterly for
    # USD, CAD, NZD, and SEK)
    @staticmethod
    def swapFrequencyFromCurrency(currency):
        if currency == "EUR" or currency == "NOK" or currency == "SEK":
            return ql.Annual
        else:  #
            return ql.Semiannual


    # "Isolating the Effect of Day-Count Conventions on the Market Value of Interest Rate Swaps"
    # by Deng, et al.
    # IMPORTANT PART: three groups: ACT/ACT ~= ACT/365, 30/ACT ~= 30/365, ACT/360. 
    # IMPORTANT PART: If you have to guess, choose ACT/ACT --- it's the middle one
    # Says US Corporates use 30/360
    # says European (incl. British) use ACT/ACT
    # but it is variable.
    # !!! SWAPS are different, see ISDA
    #
    # http://treasurytoday.com/2001/11/day-count-conventions
    # says ACT/ACT for EUR, AUD, CAD.  (and UST)
    # says E30/360 for CHF, and DEM (Euro area pre-1999)
    # says 30/360 for USD (corporates)
    #
    # Investopedia   http://www.investopedia.com/terms/d/daycount.asp
    # Floating rates (LIBOR) use ACT/360, except for GBP which is ACT/365
    # Floating rates AUD and NZD also use ACT/365
    # FIXED rate legs of USD, EUR, and CHF use 30/360
    # FIXED rate legs of GBP, JPY, AUD, NZD use 30/365
    #
    # wiki.treasurers.org
    # 30E/360 was used for some pre-Euro Eurobonds, Swiss, and Swedish
    # ACT/ACT used for GBP and EUR.  Used for UST and some USD swaps
    #
    # http://iiac.ca/wp-content/uploads/Canadian-Conventions-in-FI-Markets.pdf
    # says either ACT/ACT or ACT/365 (for Canadian Bond).  Usually ACT/365
    #
    #https://developers.opengamma.com/quantitative-research/Interest-Rate-Instruments-and-Market-Conventions.pdf
    # says New Zealand's reference interest rate is "NZD-NZIONA" and is ACT/365
    #
    # https://quant.stackexchange.com/questions/8813/japan-day-count-conventions
    # says JPY uses ACT/365 domestically and ACT/360 for "euroyen" market
    #      SWAPs use fixed leg ACT/365, float is ACT/360 (libor) or ACT/365 (tibor)
    #
    # https://www.riksgalden.se/en/For-investors/Newsroom/News-and-press-releases/Press-releases/2000/New-day-count-convention-for-issuance-of-Swedish-Treasury-bills/
    # says Sweden on Apr 1, 2000 converted to ACT/360 for governments
    #
    # https://www.six-swiss-exchange.com/services/yield_calculator_en.html
    # bond calculator defaults to "German 30/360"
    #
    # http://www.finansanalytiker.no/innhold/publikasjoner/Konv_eng%20may01.pdf
    # Recommends 30E/360 for norwegian fixed bonds
    #
    # http://www.nasdaqomx.com/digitalAssets/59/59908_Principal_Characteristics_and_Calculation_Conventions_of_Listed_Bonds_and_Bills.pdf
    # PROBABLY GOVERMENTS!!! From 2006, says:
    # says NOK uses ACT/365
    #      SEK and CHF use 30E/360
    #      rest use ACT/ACT
    
    @staticmethod
    def dayCountForBondFromCurrency(currency):
        if currency=="AUD":
            return ql.ActualActual(ql.ActualActual.Bond)
        elif currency=="CAD":
            return ql.ActualActual(ql.ActualActual.Bond)   # ?? Actual365Fixed?
        elif currency=="CHF":
            return ql.Thirty360(ql.Thirty360.European)
        elif currency=="DEM":
            return ql.Thirty360(ql.Thirty360.European)
        elif currency=="EUR":
            return ql.ActualActual(ql.ActualActual.Euro)
        elif currency=="GBP":
            return ql.ActualActual(ql.ActualActual.Bond)
        elif currency=="JPY":
            return ql.ActualActual(ql.ActualActual.Actual365)
        elif currency=="NOK":
            return ql.Thirty360(ql.Thirty360.European)           # Not clear 
            # return ql.ActualActual(ql.ActualActual.Actual365)  
        elif currency=="NZD":
            return ql.ActualActual(ql.ActualActual.Actual365)   # Not clear
        elif currency=="SEK":
            return ql.Thirty360(ql.Thirty360.European)           # Not clear 
            # return ql.ActualActual(ql.ActualActual.Bond)
        elif currency=="USD":
            return ql.Thirty360(ql.Thirty360.BondBasis)
        else:
            raise Exception("no daycount for currency:" + currency)

    @staticmethod
    def calendarFromCurrency(currency):
        if currency=="AUD":
            return ql.Australia()
        elif currency=="CAD":
            return ql.Canada()
        elif currency=="CHF":
            return ql.Switzerland()
        elif currency=="DEM":
            return ql.Germany()
        elif currency=="EUR":
            return ql.Germany()
        elif currency=="GBP":
            return ql.UnitedKingdom()
        elif currency=="JPY":
            return ql.Japan()
        elif currency=="NOK":
            return ql.Norway()
        elif currency=="NZD":
            return ql.NewZealand()
        elif currency=="SEK":
            return ql.Sweden()
        elif currency=="USD":
            return ql.UnitedStates()
        else:
            raise Exception("no calendar for currency:" + currency)

    @staticmethod
    def yieldAndAccIntStatic(coupon, mat_date, issue_date, currency, settle_date, clean_price):
        frequency = BondLibrary.frequencyFromCurrency(currency)
        tenor = ql.Period(frequency)
        # assume no weekends, no holidays in calculating accrued interest
        calendar_local = ql.NullCalendar()
        # businessConvention is when is actual coupon date, when coupon lands on a holiday/weekend?
        businessConvention = ql.Unadjusted
        # from maturity date, going backwards
        dateGeneration = ql.DateGeneration.Backward
        # Shift to land on 28/29/30/31st
        monthEnd = False

        schedule = ql.Schedule( issue_date, mat_date, tenor, calendar_local,
                                businessConvention, businessConvention, dateGeneration, monthEnd)

        settlementDays = 1
        faceValue = 100.0
        couponList = [ coupon ]
        dayCount = BondLibrary.dayCountForBondFromCurrency( currency )
        fixedRateBond = ql.FixedRateBond(settlementDays, faceValue, schedule, couponList, dayCount)

        if ql.BondFunctions.nextCashFlowDate(fixedRateBond, settle_date) == ql.BondFunctions.maturityDate(fixedRateBond):
            compounding = ql.Simple
        else:
            compounding = ql.Compounded
        yyield = fixedRateBond.bondYield(clean_price, dayCount, compounding, frequency, settle_date)
        accint = fixedRateBond.accruedAmount(settle_date)

        # tuple 
        return (yyield, accint)

        
    def yieldAndAccInt(self, isin, settle_date, clean_price):
        if isin not in self.bond_dict:
            raise Exception("could not find bond:" + isin)
        bond_desc = self.bond_dict[isin]

        return BondLibrary.yieldAndAccIntStatic(bond_desc["coupon"], bond_desc["mat_date"],
                                        bond_desc["issue_date"], bond_desc['currency'],
                                        settle_date, clean_price)

    
    @staticmethod
    def dirtyPriceFromCleanStatic(coupon, mat_date, issue_date, currency, settle_date, clean_price):
        (yyield_ignored, accint) = BondLibrary.yieldAndAccIntStatic(coupon, mat_date, issue_date, currency,
                                                    settle_date, clean_price)
        dirty_price = clean_price - accint
        return dirty_price

    def dirtyPriceFromClean(self, isin, settle_date, clean_price):
        if isin not in self.bond_dict:
            raise Exception("could not find bond:" + isin)
        bond_desc = self.bond_dict[isin]

        return BondLibrary.dirtyPriceFromCleanStatic( bond_desc["coupon"], bond_desc["mat_date"],
                                            bond_desc["issue_date"], bond_desc['currency'],
                                            settle_date, clean_price)


    @staticmethod
    def commonYieldFromCleanPriceStatic(coupon, mat_date, issue_date, currency, settle_date, clean_price):
        
        dirty_price = BondLibrary.dirtyPriceFromCleanStatic(coupon, mat_date, issue_date, currency,
                                                        settle_date, clean_price)
                    
        tenor = ql.Period( BondLibrary.frequencyFromCurrency(currency) )
        # Now, with the dirty price, we calculate an "exact" common yield
        # Payments are now affected by national calendars
        calendar_local = BondLibrary.calendarFromCurrency( currency )
        businessConvention = ql.Following
        # from maturity date, going backwards
        dateGeneration = ql.DateGeneration.Backward
        # Shift to land on 28/29/30/31st
        monthEnd = False
        
        schedule = ql.Schedule( issue_date, mat_date, tenor, calendar_local,
                                businessConvention, businessConvention, dateGeneration, monthEnd)

        settlementDays = 1
        faceValue = 100.0
        couponList = [ coupon ]
        dayCount = ql.ActualActual(ql.ActualActual.ISMA)
        fixedRateBond = ql.FixedRateBond(settlementDays, faceValue, schedule, couponList, dayCount)

        accint = fixedRateBond.accruedAmount(settle_date)
        
        clean_price = dirty_price + accint

        yyield = fixedRateBond.bondYield(clean_price, dayCount,
                                         ql.Continuous, ql.NoFrequency, settle_date)
        return yyield
        

    def commonYieldFromCleanPrice(self, isin, settle_date, clean_price):
        if isin not in self.bond_dict:
            raise Exception("could not find bond:" + isin)
        bond_desc = self.bond_dict[isin]

        return BondLibrary.commonYieldFromCleanPriceStatic(bond_desc["coupon"], bond_desc["mat_date"],
                                                bond_desc["issue_date"], bond_desc['currency'],
                                                settle_date, clean_price)

    @staticmethod
    def commonYieldFromSwapYield(currency, duration, issue_pydate, swap_yield):
        # NOTE: Use frequence of swap's fixed leg
        tenor = ql.Period( BondLibrary.swapFrequencyFromCurrency(currency) )
        # Now, with the dirty price, we calculate an "exact" common yield
        # Payments are now affected by national calendars
        calendar_local = BondLibrary.calendarFromCurrency( currency )
        businessConvention = ql.Following
        # from maturity date, going backwards
        dateGeneration = ql.DateGeneration.Backward
        # Shift to land on 28/29/30/31st
        monthEnd = False

        issue_date = convertToQLDate(issue_pydate)
        # WEIRD bug, just avoiding it.  Happens even on leap years!
        if issue_pydate.month == 2 and issue_pydate.day == 29:
            mat_date = ql.Date(28, 2, issue_pydate.year + duration)
        else:
            mat_date = ql.Date(issue_pydate.day, issue_pydate.month, issue_pydate.year + duration)
        schedule = ql.Schedule( issue_date, mat_date, tenor, calendar_local,
                                businessConvention, businessConvention, dateGeneration, monthEnd)

        settlementDays = 1
        faceValue = 100.0
        couponList = [ swap_yield ]
        dayCount = ql.ActualActual(ql.ActualActual.ISMA)
        fixedRateBond = ql.FixedRateBond(settlementDays, faceValue, schedule, couponList, dayCount)

        # accrued interest should be zero.
        clean_price = 100.0
        yyield = fixedRateBond.bondYield(clean_price, dayCount,
                                         ql.Continuous, ql.NoFrequency, issue_date)
        return yyield
        

        
    def currencyFromIsin(self, isin):
        if isin not in self.bond_dict:
            raise Exception("could not find bond:" + isin)
        bond_desc = self.bond_dict[isin]

        return bond_desc["currency"]

    def pythonMaturityFromIsin(self, isin):
        if isin not in self.bond_dict:
            raise Exception("could not find bond:" + isin)
        bond_desc = self.bond_dict[isin]

        d = bond_desc["mat_date"]
        return datetime.date(d.year(), d.month(), d.dayOfMonth())

    def csvDescriptionOfBond(self, isin):
        if isin not in self.bond_dict:
            raise Exception("could not find bond:" + isin)
        bond_desc = self.bond_dict[isin]

        md = bond_desc["mat_date"]
        pydate_maturity = datetime.date(md.year(), md.month(), md.dayOfMonth())
        
        issue_date = bond_desc["issue_date"]
        pydate_issue = datetime.date(issue_date.year(), issue_date.month(), issue_date.dayOfMonth())
        
        return str( bond_desc['coupon']) + "," + pydate_maturity.strftime("%Y-%m-%d") + "," + pydate_issue.strftime("%Y-%m-%d") + "," + str( bond_desc['currency']) + "," + str( bond_desc['issuer'] + "," + bond_desc['moody'] + "," + bond_desc['sandp'])

    def csvDescriptionOfBondHeader(self):
        return "coupon,maturity,issue_date,currency,firm,moody_rating,sandp_rating"
    
    def containsIsin(self, isin):
        return isin in self.bond_dict
        
#  !!!!
# remove bonds from firms that only issue in a single currency
#   --- this is done elsewhere
