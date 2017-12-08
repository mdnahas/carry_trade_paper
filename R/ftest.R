# needed for wt.var
library("SDMTools")


# process command-line arguments
argv = commandArgs(trailingOnly=TRUE)
if (length(argv) != 3) {
   stop(paste0("Needed 3 arguments and saw ", length(argv), ": infilename prefix bounded"), call.=FALSE)
}
infilename = argv[1]
prefix = argv[2]
bounded = argv[3]


currencies_except_USD = c( "AUD", "CAD",  "CHF", "EUR", "GBP", "JPY", "NOK", "NZD", "SEK")


# read file
df = read.csv(infilename, as.is=TRUE)

date_strs = vector("character")
credit_spread = vector("double") 
cip_basis = vector("double") 
weights = vector("double") 

for (curr_index in 1:9) {
    curr = currencies_except_USD[curr_index]

    # If comparing to Liao, ignore new currencies
    if (bounded == "true" && (curr == "NOK" || curr == "SEK" || curr == "NZD"))
        next
    
    date_strs = c(date_strs, df[["date"]]) 
    credit_spread = c(credit_spread, df[[curr]]) 
    cip_basis = c(cip_basis, df[[paste0(prefix, curr)]])
    errors = df[[paste0(currencies_except_USD[curr_index], "_err")]]
#
# WARNING - ERROR VALUES WERE EFFECTIVELY 0 for SEK and CAD
#                  - I limited the value to being at least 1 basis point.
#                  --- need to diagnose if something is wrong here.    
#
    errors = replace(errors, errors < 0.0001, 0.0001)
#
# Multiple examples had 1/(stdev^2).  Not sure they're right.  Either works ok.
#    weights = c(weights, 1 / (errors)^2)
    weights = c(weights, 1 / errors)
}

# remove NA
filter = !(is.na(cip_basis) | is.na(credit_spread) | is.na(weights))
date_strs = date_strs[filter] 
credit_spread = credit_spread[filter] 
cip_basis = cip_basis[filter]
weights = weights[filter]

# If comparing to Liao, ignore new dates
if (bounded == "true") {
      dates = as.Date( date_strs, "%Y-%m-%d" )
      filter = dates - as.Date("2004-1-1", "%Y-%m-%d") >= 0 & dates - as.Date("2016-7-31", "%Y-%m-%d") <= 0
      credit_spread = credit_spread[filter] 
      cip_basis = cip_basis[filter]
      weights = weights[filter]
}



mydata = data.frame(credit_spread, cip_basis, weights)

fitted = lm(cip_basis ~ credit_spread, mydata, weights=weights)

#summary(fitted)
coef(fitted)

# constrained - assume cip_basis = 1*credit_spread + 0
diff = cip_basis - credit_spread

diff_df = data.frame(diff, weights)

constrained = lm(diff ~ 0, diff_df, weights=weights)

v_result = var.test( fitted, constrained)
v_result

DF.x = v_result$parameter[1] 
DF.y = v_result$parameter[2] 

sample_every = 18
correction = round(DF.y*(sample_every-1)/sample_every)
PVAL = pf( v_result$statistic, DF.x - correction, DF.y - correction)
PVAL <- 2 * min(PVAL, 1 - PVAL)

print(paste0("When sampling every ", sample_every, " the p-value is ", PVAL))

