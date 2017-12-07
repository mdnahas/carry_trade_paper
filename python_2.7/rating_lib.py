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

moody_dict = {
                  "Aaa":0,
                  "Aa1":1, "Aa2":2, "Aa3":3,
                  "A1":4, "A2":5, "A3":6,
                  "Baa1":7, "Baa2":8, "Baa3":9,
                  "Ba1":10, "Ba2":11, "Ba3":12,
                  "B1":13, "B2":14, "B3":15,
                  "Caa1":16, "Caa2":17, "Caa3":18,
                  "Ca": 20,
                  "C": 21,
                  "NR": 50,
                  "WR": 51
}

sandp_dict = {
                  "AAA":0,
                  "AA+":1, "AA":2, "AA-":3,
                  "A+":4, "A":5, "A-":6,
                  "BBB+":7, "BBB":8, "BBB-":9,
                  "BB+":10, "BB":11, "BB-":12,
                  "B+":13, "B":14, "B-":15,
                  "CCC+":16, "CCC":17, "CCC-":18,
                  "CC": 20,
                  "C": 21,
                  "D": 22,
                  "NR": 50
}
                  

# returns integer 0 or 1 for ratings bucket
#
# 0 is "high quality":
#        Aaa, Aa1, Aa2, Aa3, or A1 from Moody's
#        No rating from Moody's and rating AAA, AA+, AA, AA-, or A+ from S&P
# 1 is "low quality"
#
# takes ISIN for error reporting
def rating_bucket(moody_rating, sandp_rating, isin):
    moody_orig = moody_rating
    sandp_orig = sandp_rating
    
    # Some ratings are preliminary. Treat them as actual.
    if len(moody_rating) > 3 and moody_rating[:3] == "(P)":
        moody_rating = moody_rating[3:]

    # Some have extensions " *" " *+" and " *-"
    if len(moody_rating) > 3 and (moody_rating[-3:] == " *+" or moody_rating[-3:] == " *-"):
        moody_rating = moody_rating[:-3]
    if len(moody_rating) > 2 and moody_rating[-2:] == " *":
        moody_rating = moody_rating[:-2]

    # unsolicited rating.  still a real rating
    if moody_rating[-1:] == "u":
        moody_rating = moody_rating[:-1]
        
    # rating is "expected".  Not actually a rating.
    # It is a predicted rating by Bloomberg, so we'll treat it as
    # if the market expects that rating and use it.
    if moody_rating[-1:] == "e":
        moody_rating = moody_rating[:-1]

    # NOTE: The "e" was removed from the end of "#N/A Field Not Applicable"
    if moody_rating != "#N/A N/A" and moody_rating != "#N/A Field Not Applicabl" and moody_rating != "NR" and moody_rating != "WR":
        if moody_rating not in moody_dict:
            raise Exception("Bond " + isin + " Could not parse moody rating.  Orig=" + moody_orig + " Final=" + moody_rating)

        if moody_dict[ moody_rating ] <= moody_dict["A1"]:
            return 1
        else:
            return 0

    # moody did not rate it - use S&P rating

    # Some have extensions " *" " *+" and " *-"
    if len(sandp_rating) > 3 and (sandp_rating[-3:] == " *+" or sandp_rating[-3:] == " *-"):
        sandp_rating = sandp_rating[:-3]
    if len(sandp_rating) > 2 and sandp_rating[-2:] == " *":
        sandp_rating = sandp_rating[:-2]

    # unsolicited rating.  still a real rating
    if sandp_rating[-1:] == "u":
        sandp_rating = sandp_rating[:-1]
    
    if sandp_rating != "#N/A N/A" and sandp_rating != "#N/A Field Not Applicable" and sandp_rating != "NR":
        if sandp_rating not in sandp_dict:
            raise Exception("Bond " + isin + " Could not parse sandp rating.  Orig=" + sandp_orig + " Final=" + sandp_rating)
            
        if sandp_dict[ sandp_rating ] <= sandp_dict["A+"]:
            return 1
        else:
            return 0

    # sandp did not rate it
    raise Exception("Bond " + isin + " did not have rating.  Moody=" + moody_orig + " S&P=" + sandp_orig)



# returns integer 0 or 1 for ratings bucket
#
# 0 is "high quality":
#        Aaa, Aa1, Aa2, Aa3, or A1 from Moody's
#        No rating from Moody's and rating AAA, AA+, AA, AA-, or A+ from S&P
# 1 is "low quality"
#
# takes ISIN for error reporting
def moody_as_int(moody_rating, isin):
    moody_orig = moody_rating
    
    # Some ratings are preliminary. Treat them as actual.
    if len(moody_rating) > 3 and moody_rating[:3] == "(P)":
        moody_rating = moody_rating[3:]

    # Some have extensions " *" " *+" and " *-"
    if len(moody_rating) > 3 and (moody_rating[-3:] == " *+" or moody_rating[-3:] == " *-"):
        moody_rating = moody_rating[:-3]
    if len(moody_rating) > 2 and moody_rating[-2:] == " *":
        moody_rating = moody_rating[:-2]

    # unsolicited rating.  still a real rating
    if moody_rating[-1:] == "u":
        moody_rating = moody_rating[:-1]
        
    # rating is "expected".  Not actually a rating.
    # It is a predicted rating by Bloomberg, so we'll treat it as
    # if the market expects that rating and use it.
    if moody_rating[-1:] == "e":
        moody_rating = moody_rating[:-1]

    # NOTE: The "e" was removed from the end of "#N/A Field Not Applicable"
    if moody_rating != "#N/A N/A" and moody_rating != "#N/A Field Not Applicabl" and moody_rating != "NR" and moody_rating != "WR":
        if moody_rating not in moody_dict:
            raise Exception("Bond " + isin + " Could not parse moody rating.  Orig=" + moody_orig + " Final=" + moody_rating)

        return moody_dict[ moody_rating ] 

    # moody did not rate it.
    return 50

# returns integer 0 or 1 for ratings bucket
#
# 0 is "high quality":
#        Aaa, Aa1, Aa2, Aa3, or A1 from Moody's
#        No rating from Moody's and rating AAA, AA+, AA, AA-, or A+ from S&P
# 1 is "low quality"
#
# takes ISIN for error reporting
def sandp_as_int(sandp_rating, isin):
    sandp_orig = sandp_rating
    
    # Some have extensions " *" " *+" and " *-"
    if len(sandp_rating) > 3 and (sandp_rating[-3:] == " *+" or sandp_rating[-3:] == " *-"):
        sandp_rating = sandp_rating[:-3]
    if len(sandp_rating) > 2 and sandp_rating[-2:] == " *":
        sandp_rating = sandp_rating[:-2]

    # unsolicited rating.  still a real rating
    if sandp_rating[-1:] == "u":
        sandp_rating = sandp_rating[:-1]
    
    if sandp_rating != "#N/A N/A" and sandp_rating != "#N/A Field Not Applicable" and sandp_rating != "NR":
        if sandp_rating not in sandp_dict:
            raise Exception("Bond " + isin + " Could not parse sandp rating.  Orig=" + sandp_orig + " Final=" + sandp_rating)

        return sandp_dict[ sandp_rating ]

    # sandp did not rate it
    return 50

def combine_rating(moody_rating_int, sandp_rating_int):
    if moody_rating_int == 50:
        return 2*sandp_rating_int
    elif sandp_rating_int == 50:
        return 2*moody_rating_int
    else:
        return moody_rating_int + sandp_rating_int

def rating_bucket2(combined_rating):
    if combined_rating <= 6:
        return 0
    else:
        return 1

            
class TestRatingsMethods(unittest.TestCase):

    def test_moody_matters(self):
        self.assertEqual(1, rating_bucket("Aaa", "AAA", "US123456789"))
        self.assertEqual(1, rating_bucket("Aaa", "D", "US123456789"))
        self.assertEqual(1, rating_bucket("Aaa", "NR", "US123456789"))
        self.assertEqual(1, rating_bucket("Aaa", "#N/A N/A", "US123456789"))

    def test_high1(self):
        self.assertEqual(1, rating_bucket("Aaa", "D", "US123456789"))
        self.assertEqual(1, rating_bucket("Aa1", "D", "US123456789"))
        self.assertEqual(1, rating_bucket("Aa2", "D", "US123456789"))
        self.assertEqual(1, rating_bucket("Aa3", "D", "US123456789"))
        self.assertEqual(1, rating_bucket("A1", "D", "US123456789"))

    def test_low1(self):
        self.assertEqual(0, rating_bucket("A2", "AAA", "US123456789"))
        self.assertEqual(0, rating_bucket("A3", "AAA", "US123456789"))
        self.assertEqual(0, rating_bucket("Baa1", "AAA", "US123456789"))
        self.assertEqual(0, rating_bucket("Ba2", "AAA", "US123456789"))
        self.assertEqual(0, rating_bucket("B3", "AAA", "US123456789"))
        self.assertEqual(0, rating_bucket("Caa1", "AAA", "US123456789"))
        self.assertEqual(0, rating_bucket("Ca", "AAA", "US123456789"))
        self.assertEqual(0, rating_bucket("C", "AAA", "US123456789"))

    def test_high_prefix_suffix(self):
        self.assertEqual(1, rating_bucket("(P)A1e", "D", "US123456789"))
        self.assertEqual(1, rating_bucket("(P)A1u", "D", "US123456789"))
        self.assertEqual(1, rating_bucket("(P)A1e *+", "D", "US123456789"))
        self.assertEqual(1, rating_bucket("(P)A1u *-", "D", "US123456789"))
        self.assertEqual(1, rating_bucket("A1 *", "D", "US123456789"))

    def test_low_prefix_suffix(self):
        self.assertEqual(0, rating_bucket("(P)A2e", "AAA", "US123456789"))
        self.assertEqual(0, rating_bucket("(P)A2u", "AAA", "US123456789"))
        self.assertEqual(0, rating_bucket("(P)A2e *+", "AAA", "US123456789"))
        self.assertEqual(0, rating_bucket("(P)A2u *-", "AAA", "US123456789"))
        self.assertEqual(0, rating_bucket("A2 *", "AAA", "US123456789"))

    def test_high_sandp(self):
        self.assertEqual(1, rating_bucket("#N/A N/A", "AAA", "US123456789"))
        self.assertEqual(1, rating_bucket("#N/A N/A", "AA+", "US123456789"))
        self.assertEqual(1, rating_bucket("#N/A N/A", "AA", "US123456789"))
        self.assertEqual(1, rating_bucket("#N/A N/A", "AA-", "US123456789"))
        self.assertEqual(1, rating_bucket("#N/A N/A", "A+", "US123456789"))
        self.assertEqual(1, rating_bucket("NR", "A+", "US123456789"))
        self.assertEqual(1, rating_bucket("WR", "A+", "US123456789"))
        # From bond CH0009967156
        rating_bucket("#N/A Field Not Applicable", "AA-", "US123456789")

    def test_low_sandp(self):
        self.assertEqual(0, rating_bucket("#N/A N/A", "A", "US123456789"))
        self.assertEqual(0, rating_bucket("#N/A N/A", "A-", "US123456789"))
        self.assertEqual(0, rating_bucket("#N/A N/A", "BBB+", "US123456789"))
        self.assertEqual(0, rating_bucket("#N/A N/A", "BB", "US123456789"))
        self.assertEqual(0, rating_bucket("#N/A N/A", "B-", "US123456789"))
        self.assertEqual(0, rating_bucket("#N/A N/A", "CCC+", "US123456789"))
        self.assertEqual(0, rating_bucket("#N/A N/A", "CC", "US123456789"))
        self.assertEqual(0, rating_bucket("#N/A N/A", "C", "US123456789"))
        self.assertEqual(0, rating_bucket("#N/A N/A", "D", "US123456789"))
        self.assertEqual(0, rating_bucket("NR", "D", "US123456789"))
        self.assertEqual(0, rating_bucket("WR", "D", "US123456789"))

    def test_high_sandp_prefix(self):
        self.assertEqual(1, rating_bucket("#N/A N/A", "A+u *-", "US123456789"))
        self.assertEqual(1, rating_bucket("#N/A N/A", "A+ *+", "US123456789"))
        self.assertEqual(1, rating_bucket("#N/A N/A", "A+ *", "US123456789"))

    def test_low_sandp_prefix(self):
        self.assertEqual(0, rating_bucket("#N/A N/A", "A *-", "US123456789"))
        self.assertEqual(0, rating_bucket("#N/A N/A", "A *+", "US123456789"))
        self.assertEqual(0, rating_bucket("#N/A N/A", "A *", "US123456789"))

    def test_no_rating(self):
        with self.assertRaises(Exception):
            rating_bucket("#N/A N/A", "#N/A N/A", "US123456789")
        with self.assertRaises(Exception):
            rating_bucket("NR", "NR", "US123456789")
        with self.assertRaises(Exception):
            rating_bucket("WR", "NR", "US123456789")

    def test_numeric(self):
        self.assertEqual(0, moody_as_int("Aaa", "US123456789"))
        self.assertEqual(7, moody_as_int("Baa1", "US123456789"))
        self.assertEqual(21, moody_as_int("C", "US123456789"))
        self.assertEqual(50, moody_as_int("NR", "US123456789"))
        self.assertEqual(50, moody_as_int("WR", "US123456789"))
        self.assertEqual(50, moody_as_int("#N/A N/A", "US123456789"))

        self.assertEqual(0, sandp_as_int("AAA", "US123456789"))
        self.assertEqual(7, sandp_as_int("BBB+", "US123456789"))
        self.assertEqual(21, sandp_as_int("C", "US123456789"))
        self.assertEqual(50, sandp_as_int("NR", "US123456789"))
        self.assertEqual(50, sandp_as_int("#N/A N/A", "US123456789"))

    def test_numeric_prefix_suffix(self):
        self.assertEqual(4, moody_as_int("(P)A1e", "US123456789"))
        self.assertEqual(4, moody_as_int("(P)A1u", "US123456789"))
        self.assertEqual(4, moody_as_int("(P)A1e *+", "US123456789"))
        self.assertEqual(4, moody_as_int("(P)A1u *-", "US123456789"))
        self.assertEqual(4, moody_as_int("A1 *", "US123456789"))
        
        self.assertEqual(6, sandp_as_int("A-u", "US123456789"))
        self.assertEqual(4, sandp_as_int("A+u *+", "US123456789"))
        self.assertEqual(6, sandp_as_int("A-u *-", "US123456789"))
        self.assertEqual(4, sandp_as_int("A+ *", "US123456789"))
        
    def test_combined(self):
        self.assertEquals(100, combine_rating(50, 50))
        self.assertEquals(0, combine_rating(0, 0))
        self.assertEquals(1, combine_rating(1, 0))
        self.assertEquals(4, combine_rating(2, 2))
        self.assertEquals(6, combine_rating(3, 50))
        self.assertEquals(8, combine_rating(50, 4))

    def test_rating_bucket2(self):
        self.assertEquals(0, rating_bucket2(combine_rating(0, 0)))
        self.assertEquals(0, rating_bucket2(combine_rating(1, 1)))
        self.assertEquals(0, rating_bucket2(combine_rating(2, 3)))
        self.assertEquals(0, rating_bucket2(combine_rating(3, 3)))
        self.assertEquals(0, rating_bucket2(combine_rating(2, 4)))
        self.assertEquals(0, rating_bucket2(combine_rating(4, 2)))
        self.assertEquals(1, rating_bucket2(combine_rating(4, 3)))
        self.assertEquals(1, rating_bucket2(combine_rating(3, 4)))
        self.assertEquals(1, rating_bucket2(combine_rating(4, 4)))
        self.assertEquals(1, rating_bucket2(combine_rating(20, 20)))
        
        self.assertEquals(0, rating_bucket2(combine_rating(0, 50)))
        self.assertEquals(0, rating_bucket2(combine_rating(50, 0)))
        self.assertEquals(0, rating_bucket2(combine_rating(3, 50)))
        self.assertEquals(0, rating_bucket2(combine_rating(50, 3)))
        self.assertEquals(1, rating_bucket2(combine_rating(4, 50)))
        self.assertEquals(1, rating_bucket2(combine_rating(50, 4)))
        self.assertEquals(1, rating_bucket2(combine_rating(20, 50)))
        self.assertEquals(1, rating_bucket2(combine_rating(50, 20)))


                                     
if __name__ == '__main__':
    unittest.main()
