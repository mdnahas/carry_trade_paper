/*
This is example C# code to download prices from Bloomberg.

I want it to read two files:
   1) a CSV of bonds, with issue and maturity dates
   2) a list of dates

Then for each security,
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

		System.Console.Error.WriteLine("!!! " + identifier + " from " + issued_date.ToString("yyyy-M-d") + " to " + matures_date.ToString("yyyy-M-d"));
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
	

	static void PerformRequest(DateTime date, List<Bond> bonds) {
	    Console.WriteLine( date.ToString("yyyy-M-d") );
	    foreach (Bond b in bonds) {
		Console.WriteLine("    " + b.identifier);
	    }
	    Console.WriteLine();
	}
    }
}

