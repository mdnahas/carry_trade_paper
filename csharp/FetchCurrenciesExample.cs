/*
This is example C# code to download prices from Bloomberg.

I want it to read one file:
   2) a list of dates

Then for every currency, forward, and swap:
   fetch the prices for all the dates that lie between the issue date and the maturity date.

Bloomberg's API makes it easier to pick the dates and then the securities that share that day.

*/

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
	    // interest-rate swaps
	    secs_preEuro.Add("DMSW" + year_str + " curncy");   // may alias to EUSA?
	    secs_postEuro.Add("EUSA" + year_str + " curncy"); 


	    dates = new List<DateTime>();
	    foreach (string date_str in dates_lines) {
		dates.Add( DateTime.ParseExact(date_str, "yyyy-M-d", CultureInfo.InvariantCulture));
	    }
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
	

	static void PerformRequest(DateTime date, List<string> secs) {
	    Console.WriteLine( date.ToString("yyyy-M-d") );
	    foreach (string sec in secs) {
		Console.WriteLine("    " + sec);
	    }
	    Console.WriteLine();
	}
    }
}

