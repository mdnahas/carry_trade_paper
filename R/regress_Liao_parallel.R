
#library("lmtest")
library("sandwich")
#library("multiwayvcov")
library("parallel")

# process command-line arguments
argv = commandArgs(trailingOnly=TRUE)
if (length(argv) != 2) {
   stop(paste0("Needed 2 arguments and saw ", length(argv), ": infile_dir outputfilename"), call.=FALSE)
}
infile_directory = argv[1]
outfilename = argv[2]


currencies_except_USD = c( "AUD", "CAD",  "CHF", "EUR", "GBP", "JPY", "NOK", "NZD", "SEK")



process_one_file <- function(infile_directory, filename) {
    print(paste0("Processing ", filename)) 

    df = read.csv(paste0(infile_directory, "/", filename)) 

    fitted = tryCatch({
        lm(credit_spread ~ as.factor(currency) + as.factor(rating_bucket)  + as.factor(duration_bucket) + as.factor(firm), df)
    }, warning = function(w) {
         # warning handling code
	 write(paste0("Received warning during regression.  Skipping.  W=", w), stderr())
	 return(NULL)
    }, error = function(e) {
         # error handling code
	 write(paste0("Received error during regression.  Skipping.  E=", e), stderr())
	 return(NULL)
    })
    if ( is.null(fitted)) {
	 write(paste0("Error?  Fit was null for file ", filename), stderr())
	 return(NULL)
    }
    #robust = coeftest(fitted, vcov=vcovHC(fitted, "HC1"))[,2]
    robust = lmtest::coeftest(fitted, multiwayvcov::cluster.vcov(fitted, df$firm))[,2]
    
    # output one line for each file:
    # date
    line = filename

    coeffs = summary(fitted)$coefficients
    
    # Constant (USD) 
    line = paste0(line, ",", coeffs["(Intercept)", 1])

   # each currency (except USD)
   for (curr_index in 1:9) {
       str_index = paste0("as.factor(currency)", curr_index)
       value = tryCatch({
       	     toString( coeffs[str_index, 1] )
	}, warning = function(w) {
	     return("")
	}, error = function(e) {
	     return("")
	})
        line = paste0(line, ",", value)
    }

   # Robust error for constant (USD)
   line = paste0(line, ",", robust["(Intercept)"]) 

   # robust error for each currency (except USD)
   for (curr_index in 1:9) {
       str_index = paste0("as.factor(currency)", curr_index)
       value = tryCatch({
       	     if (is.na(robust[str_index] ))
	     	""
	     else 
	         toString( robust[str_index] )
	}, warning = function(w) {
	     return("")
	}, error = function(e) {
	     return("")
	})
        line = paste0(line, ",", value)
    }

   # rating bucket
   line = paste0(line, ",", coeffs["as.factor(rating_bucket)1", 1]) 
   line = paste0(line, ",", robust["as.factor(rating_bucket)1"]) 

   # factor for duration
   for (dur_index in 1:3) {
       str_index = paste0("as.factor(duration_bucket)", dur_index) 
       value = tryCatch({
       	     if (is.na(robust[str_index] ))
	     	""
	     else 
	         toString( robust[str_index] )
	}, warning = function(w) {
	     return("")
	}, error = function(e) {
	     return("")
	})
        line = paste0(line, ",", value)
    }
   
    # count
    line = paste0(line, ",", nrow(df))

    # max abs residual  (to see if anything is really wrong)
    copy = numeric(length(robust))
    copy_index = 0
    for (coeffs_index in 1:length(robust)) {
        if (startsWith( names(robust[coeffs_index]), "as.factor(firm)")) {
      	     copy[copy_index] = coeffs[ coeffs_index, 1]
	     copy_index = copy_index + 1
        }
    }
    max_res = max(abs(copy[0:copy_index]))
    line = paste0(line, ",", max_res)

    # write line to file
    # output = c(output, line)    
    return(line)
}

# empty vector of characters for output
output = character()

# loop over all files
filenames = list.files(infile_directory)


# loop through all files, generating lines of output.
# output = sapply(filenames, function(x) {process_one_file(infile_directory, x)} )    
num_cores = detectCores() - 1
cluster = makeCluster(num_cores, outfile="", type="FORK")
clusterEvalQ(cluster, library("lmtest"))  
clusterEvalQ(cluster, library("sandwich"))  
clusterEvalQ(cluster, library("multiwayvcov"))  
clusterExport(cluster, c("infile_directory", "process_one_file"))
par_output = parSapplyLB(cluster, filenames, function(x) {process_one_file(infile_directory, x)} )
output = character( length(par_output))
for (i in 1:length(par_output)) {
    output[i] = as.character(par_output[i])
}
stopCluster(cluster)



# generate header
header = "date"
header = paste0(header, ",USD")
for (curr_index in 1:9) {
    header = paste0(header, ",", currencies_except_USD[curr_index])
}
header = paste0(header, ",USD_err")
for (curr_index in 1:9) {
    header = paste0(header, ",", currencies_except_USD[curr_index], "_err")
}
header = paste0(header, ",rating_bucket")   
header = paste0(header, ",rating_bucket_err")   
for (dur_index in 1:3) {
    header = paste0(header, ",", "duration", dur_index)
}
header = paste0(header, ",count")  
header = paste0(header, ",max_abs_res") 


temp_filename = paste0(outfilename, "_unsorted")

# write to temp files
tmpfile = file(temp_filename, open="w+")
writeLines(output, tmpfile) 
close(tmpfile)

# output header  
outfile = file(outfilename, open="w+")
writeLines(header, outfile)
close(outfile)

# sort and copy data
system( paste0("sort -t \"-\" -n -k1 -k2 ", temp_filename, " >> ", outfilename))


