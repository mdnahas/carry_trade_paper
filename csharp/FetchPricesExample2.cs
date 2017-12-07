/*
This is example C# code to download prices from Bloomberg.

I want it to read two files:
   1) a CSV of bonds, with issue and maturity dates
   2) a list of dates

Then for each security,
   fetch the prices for all the dates that lie between the issue date and the maturity date.

Bloomberg's API makes it easier to pick the dates and then the securities that share that day.

*/

// This code is derived from Bloomberg code.  Here is their copyright notice.
/* Copyright 2012. Bloomberg Finance L.P.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to
 * deal in the Software without restriction, including without limitation the
 * rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
 * sell copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:  The above
 * copyright notice and this permission notice shall be included in all copies
 * or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 * FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
 * IN THE SOFTWARE.
 */

// Bloomberg imports
using Event = Bloomberglp.Blpapi.Event;
using Message = Bloomberglp.Blpapi.Message;
using Name = Bloomberglp.Blpapi.Name;
using Request = Bloomberglp.Blpapi.Request;
using Service = Bloomberglp.Blpapi.Service;
using Session = Bloomberglp.Blpapi.Session;


using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;


namespace Bloomberglp.Blpapi.Examples
{
    public class SimpleHistoryExample {
	
	class Bond {
	    public const int num_of_fields = 16;  // goes to column P in Gnumeric
	    // public const int issued_date_field_index = 9;
	    public const int matures_date_field_index = 5;
	    public const int duration_field_index = 12;
	    public const int identifier_field_index = 3;
	    
	    public DateTime issued_date;
	    public DateTime matures_date;
	    public string identifier;
	    
	    public Bond(string s) {
		char[] delimiters = { ',' };
		string[] fields = s.Split(delimiters);
		if (fields.Length != num_of_fields) {
		    System.Console.Error.WriteLine("Expected " + num_of_fields + " fields, got " + fields.Length + " in: " + s);
		    Environment.Exit(2);
		}
		
		//issued_date  = string_to_date(fields[issued_date_field_index]);
		matures_date = string_to_date(fields[matures_date_field_index]);
		identifier = fields[identifier_field_index];

		double duration_in_years = Double.Parse(fields[duration_field_index]);
		double days_per_year = 365.25;
		int duration_in_days = Convert.ToInt32( Math.Round(duration_in_years * days_per_year) );
		issued_date = matures_date.AddDays(-1 * duration_in_days);

		// System.Console.Error.WriteLine("!!! " + identifier + " from " + issued_date.ToString("yyyy-M-d") + " to " + matures_date.ToString("yyyy-M-d"));
	    }
	    
	    DateTime string_to_date(string s) {
		return DateTime.ParseExact(s, "M/d/yyyy", CultureInfo.InvariantCulture);
	    }
	    
	    public bool in_range(DateTime date) {
		return (DateTime.Compare(issued_date, date) <= 0
			&& DateTime.Compare(date, matures_date) <= 0);
	    }
	}
	
	
	static int Main(string[] args) {
	    SimpleHistoryExample example = new SimpleHistoryExample();
	    example.init(args);
	    example.initBloomberg();
	    example.run();
	    return 0;
	}
	
	
	List<Bond> bonds;
	List<DateTime> dates;
	
	void init(string[] args) {
	    if (args.Length != 2) {
		System.Console.Error.WriteLine("Needs 2 arguments, got " + args.Length);
		Environment.Exit(1);
	    }
	    
	    string bonds_filename = args[0];
	    if (!File.Exists(bonds_filename)) {
		System.Console.Error.WriteLine("Cannot find file with bonds: " + bonds_filename);
		Environment.Exit(1);
	    }
	    string[] bonds_lines = System.IO.File.ReadAllLines(bonds_filename);
	    
	    string dates_filename = args[1];
	    if (!File.Exists(dates_filename)) {
		System.Console.Error.WriteLine("Cannot find file with dates: " + dates_filename);
		Environment.Exit(1);
	    }
	    string[] dates_lines = System.IO.File.ReadAllLines(dates_filename);
	    
	    
	    bonds = new List<Bond>();
	    // Skipping first line in bond file - it is the header
	    for (int i = 1; i < bonds_lines.Length; i++) {
		bonds.Add( new Bond(bonds_lines[i]) );
	    }
	    
	    dates = new List<DateTime>();
	    foreach (string date_str in dates_lines) {
		dates.Add( DateTime.ParseExact(date_str, "yyyy-M-d", CultureInfo.InvariantCulture));
	    }
	}

	Session session;
	Service refDataService;
	void initBloomberg() {
            string serverHost = "localhost";
            int serverPort = 8194;

            SessionOptions sessionOptions = new SessionOptions();
            sessionOptions.ServerHost = serverHost;
            sessionOptions.ServerPort = serverPort;

            System.Console.Error.WriteLine("Connecting to " + serverHost +
                ":" + serverPort);
            session = new Session(sessionOptions);
            bool sessionStarted = session.Start();
            if (!sessionStarted)
            {
                System.Console.Error.WriteLine("Failed to start session.");
                return;
            }
            if (!session.OpenService("//blp/refdata"))
            {
                System.Console.Error.WriteLine("Failed to open //blp/refdata");
                return;
            }
	    refDataService = session.GetService("//blp/refdata");
	}
	
	
	List<Bond> generateRequest(DateTime date) {
	    List<Bond> bonds_in_this_request = new List<Bond>();
	    foreach (Bond b in bonds) {
		if (b.in_range(date)) {
		    bonds_in_this_request.Add(b);
		}
	    }
	    return bonds_in_this_request;
	}

	
	void run() {
	    foreach (DateTime date in dates) {
		PerformRequest(date, generateRequest(date));
	    }
	}
	
	/*
	static void PerformRequest(DateTime date, List<Bond> bonds) {
	    Console.WriteLine( date.ToString("yyyy-M-d") );
	    foreach (Bond b in bonds) {
		Console.WriteLine("    " + b.identifier);
	    }
	    Console.WriteLine();
	}
	*/

	void PerformRequest(DateTime date, List<Bond> bonds) {
	    if (bonds.Count == 0) {
		Console.Error.WriteLine("Request for date " + date + " had 0 bonds");
		return;
	    }

            Request request = refDataService.CreateRequest("HistoricalDataRequest");
            Element securities = request.GetElement("securities");
	    foreach (Bond b in bonds) {
		securities.AppendValue("/isin/" + b.identifier);
	    }
            Element fields = request.GetElement("fields");
            fields.AppendValue("PX_LAST"); // close?
            //fields.AppendValue("LAST_PRICE");   // last trade price
            request.Set("startDate", date.ToString("yyyyMMdd"));
            request.Set("endDate", date.ToString("yyyyMMdd"));
            request.Set("periodicityAdjustment", "ACTUAL");
            request.Set("periodicitySelection", "DAILY");
            request.Set("nonTradingDayFillOption", "ALL_CALENDAR_DAYS");  // report when not trading
            request.Set("nonTradingDayFillMethod", "PREVIOUS_VALUE");  // use last value when not trading

            request.Set("pricingOption", "PRICING_OPTION_YIELD");

            request.Set("maxDataPoints", 40000);
            //request.Set("returnEids", true);  // ?? Needed

            System.Console.Error.WriteLine("Sending Request: " + request);
            session.SendRequest(request, null);

	    // following code from:
            // http://stackoverflow.com/questions/12315754/bloomberg-net-api-response-data-for-multiple-securities
            while (true) {
                Event eventObj = session.NextEvent();
                foreach (Message msg in eventObj) {
                    if (msg.MessageType.Equals(Name.GetName("HistoricalDataResponse"))) {
			if (msg.HasElement("securityData")) {
			    Element secData = msg.GetElement("securityData");  

			    String secId = secData.GetElementAsString("security");  // /isin/xxxxx
			    int seqNum = secData.GetElementAsInt32("sequenceNumber");  // index in bonds
			    if (secData.HasElement("fieldData")) { //ARRAY!
				Element fieldDataArray = secData.GetElement("fieldData");
				//System.Console.Error.WriteLine("fieldDataArray has " +  fieldDataArray.NumValues + " elements");
				for (int i = 0; i < fieldDataArray.NumValues; i++) {
				    Element fieldData = fieldDataArray.GetValueAsElement(i);  // "fieldData not array
				    Datetime d = fieldData.GetElementAsDate("date");
				    if (fieldData.HasElement("PX_LAST")) {
					double yield = fieldData.GetElementAsFloat64("PX_LAST");

					// output price
					System.Console.WriteLine(secId +","+ d.Year +"-"+ d.Month +"-"+ d.DayOfMonth +","+ yield);
				    }
				    else {
					// output missing price
					System.Console.WriteLine( secId +","+ d.Year +"-"+ d.Month +"-"+ d.DayOfMonth +",");
				    }
				}
			    }
			    else {
				System.Console.Error.WriteLine("HistoricalDataResponse for " + secId + " had no fieldData[] element");
				System.Console.Error.WriteLine("Full Msg: " + msg.AsElement);
				Environment.Exit(2);
			    }
			}
		    }
		    else {
			System.Console.Error.WriteLine("Received Msg: " + msg.AsElement);
		    }
                }
                if (eventObj.Type == Event.EventType.RESPONSE) {
                    break;
                }
            }
        }
    }
}

