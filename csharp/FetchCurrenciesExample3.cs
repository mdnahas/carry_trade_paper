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
	
	static int Main(string[] args) {
	    SimpleHistoryExample example = new SimpleHistoryExample();
	    example.init(args);
	    example.initBloomberg();
	    example.run();
	    return 0;
	}
	
	
	List<string> secs_preEuro;
	List<string> secs_postEuro;
	List<DateTime> dates;
	
	void init(string[] args) {
	    if (args.Length != 2) {
		System.Console.Error.WriteLine("Needs 2 arguments, got " + args.Length);
		Environment.Exit(1);
	    }

	    string year_str = args[0];
	    int year = 5;
	    if (!Int32.TryParse(year_str, out year)) {
		System.Console.Error.WriteLine("Unable to parse 1st arg as integer: " + year_str);
		Environment.Exit(1);
	    }
	    if (year <= 0 || year > 20) {
		System.Console.Error.WriteLine("Year was not in range 1 to 20: " + year_str);
		Environment.Exit(1);
	    }
	    
	    string dates_filename = args[1];
	    if (!File.Exists(dates_filename)) {
		System.Console.Error.WriteLine("Cannot find file with dates: " + dates_filename);
		Environment.Exit(1);
	    }
	    string[] dates_lines = System.IO.File.ReadAllLines(dates_filename);
	    
	    List<string> sec_ids = new List<string>();

	    // SPOT prices
	    sec_ids.Add("AUD curncy");
	    sec_ids.Add("CAD curncy");
	    sec_ids.Add("CHF curncy");
	    // DEM and EUR handled separately
	    sec_ids.Add("GBP curncy");
	    sec_ids.Add("JPY curncy");
	    sec_ids.Add("NOK curncy");
	    sec_ids.Add("NZD curncy");
	    sec_ids.Add("SEK curncy");
	    // sec_ids.Add("USD curncy");  // Always 1

	    // forwards
	    sec_ids.Add("AUD" + year_str + "Y curncy");
	    sec_ids.Add("CAD" + year_str + "Y curncy");
	    sec_ids.Add("CHF" + year_str + "Y curncy");
	    // DEM and EUR handled separately
	    sec_ids.Add("GBP" + year_str + "Y curncy");
	    sec_ids.Add("JPY" + year_str + "Y curncy");
	    sec_ids.Add("NOK" + year_str + "Y curncy");
	    sec_ids.Add("NZD" + year_str + "Y curncy");
	    sec_ids.Add("SEK" + year_str + "Y curncy");
	    // sec_ids.Add("USD" + year_str + "Y curncy");  // Always 1

	    // cross-currency basis swaps
	    sec_ids.Add("ADBS" + year_str + " curncy");
	    sec_ids.Add("CDBS" + year_str + " curncy");
	    sec_ids.Add("SFBS" + year_str + " curncy");
	    // DEM and EUR handled separately
	    sec_ids.Add("BPBS" + year_str + " curncy");
	    sec_ids.Add("JYBS" + year_str + " curncy");
	    sec_ids.Add("NKBS" + year_str + " curncy");
	    sec_ids.Add("NDBS" + year_str + " curncy");
	    sec_ids.Add("SKBS" + year_str + " curncy");
	    // sec_ids.Add("USBS" + year_str + " curncy"); // Always 1

            // interest-rate swaps
	    sec_ids.Add("ADSWAP" + year_str + " curncy");
	    sec_ids.Add("CDSW"   + year_str + " curncy");
	    sec_ids.Add("SFSW"   + year_str + " curncy");
	    // DEM and EUR handled separately
	    sec_ids.Add("BPSW"   + year_str + " curncy");
	    sec_ids.Add("JYSW"   + year_str + " curncy");
	    sec_ids.Add("NKSW"   + year_str + " curncy");
	    sec_ids.Add("NDSWAP" + year_str + " curncy");
	    sec_ids.Add("SKSW"   + year_str + " curncy");
	    sec_ids.Add("USSWAP" + year_str + " curncy"); 
	    
	    secs_preEuro  = new List<string>(sec_ids);
	    secs_postEuro = new List<string>(sec_ids);
	    // spot
	    secs_preEuro.Add("DEM curncy");
	    secs_postEuro.Add("EUR curncy");
	    // forwards
	    secs_preEuro.Add("DEM" + year_str + "Y curncy");
	    secs_postEuro.Add("EUR" + year_str + "Y curncy");
	    // cross-currency basis swaps
	    secs_preEuro.Add("DMBS" + year_str + "Y curncy");
	    secs_postEuro.Add("EUBS" + year_str + "Y curncy");
	    // interest-rate swaps
	    secs_preEuro.Add("DMSW" + year_str + " curncy");   // may alias to EUSA?
	    secs_postEuro.Add("EUSA" + year_str + " curncy"); 


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
	
	
	List<string> generateRequest(DateTime date) {
	    DateTime euro_start = new DateTime(1999, 1, 1, 0, 0, 0);
	    
	    if (DateTime.Compare(date, euro_start) < 0) {
		return secs_preEuro;
	    }
	    else {
		return secs_postEuro;
	    }
	}

	
	void run() {
	    foreach (DateTime date in dates) {
		PerformRequest(date, generateRequest(date));
	    }
	}
	
	/*
	static void PerformRequest(DateTime date, List<string> secs) {
	    Console.WriteLine( date.ToString("yyyy-M-d") );
	    foreach (string sec in secs) {
		Console.WriteLine("    " + sec);
	    }
	    Console.WriteLine();
	}
	*/

	void PerformRequest(DateTime date, List<string> secs) {
	    if (secs.Count == 0) {
		Console.Error.WriteLine("Request for date " + date + " had 0 securities");
		return;
	    }

            Request request = refDataService.CreateRequest("HistoricalDataRequest");
            Element securities = request.GetElement("securities");
	    foreach (string s in secs) {
		securities.AppendValue(s);
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

            //request.Set("pricingOption", "PRICING_OPTION_YIELD");

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

			    String secId = secData.GetElementAsString("security");  // AUD curncy...
			    //int seqNum = secData.GetElementAsInt32("sequenceNumber");  // index in secs
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
			else {
			    System.Console.Error.WriteLine("HistoricalDataResponse had no securityData element");
			    System.Console.Error.WriteLine("Full Msg: " + msg.AsElement);
			    Environment.Exit(2);
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

