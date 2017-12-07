#
# This is the makefile for my thesis.
#

# Everything depends on raw_data.  I'm not including those dependencies.
# Everything depends python file that produces it.

# Requires quantlib dynamic library:
#   export DYLD_LIBRARY_PATH=/opt/local/lib

.DEFAULT_GOAL := latex/thesis/thesis.pdf

#
# Python library dependencies
#
python_2.7/price_and_yield_on_culled_bonds.py: python_2.7/price_and_yield_lib.py
python_2.7/process_prices_Liao.py: python_2.7/rating_lib.py python_2.7/swap_rate_lib.py
python_2.7/add_CIP_XCBS.py: python_2.7/swap_rate_lib.py

python_2.7/process_prices_Govt.py: python_2.7/rating_lib.py python_2.7/swap_rate_lib.py
python_2.7/add_CIP_XCBS_Govt.py: python_2.7/swap_rate_lib.py

python_2.7/process_prices_Corp5Y.py: python_2.7/rating_lib.py python_2.7/swap_rate_lib.py

python_2.7/plot_manyCIP2.py: python_2.7/swap_rate_lib.py
python_2.7/plot_manyCIP_minus.py: python_2.7/swap_rate_lib.py
python_2.7/plot_maxCIPspread.py: python_2.7/swap_rate_lib.py
python_2.7/plot_rate_vs_CIP.py: python_2.7/swap_rate_lib.py
python_2.7/plot_single_corpCIP.py: python_2.7/swap_rate_lib.py
python_2.7/plot_swap_vs_govt.py: python_2.7/swap_rate_lib.py

#
# Dates to uses
#
data/dates.txt: python_2.7/generate_dates.py raw_data/NYSE_holidays_days.txt
	python_2.7/generate_dates.py raw_data/NYSE_holidays_days.txt > $@

#
# Government rates
#    (Converts data from government formats to a common format)
#
data/Govt/govt20.csv: python_2.7/translate_USD.py python_2.7/translate_EUR.py python_2.7/translate_JPY.py python_2.7/translate_GBP.py python_2.7/translate_CHF.py python_2.7/translate_AUD.py python_2.7/translate_NZD.py python_2.7/translate_CAD.py python_2.7/translate_SEK.py python_2.7/translate_NOK.py
	mkdir -p data/Govt
	if [ -a data/Govt/govt20.csv ] ; then mv data/Govt/govt*.csv /tmp ; fi ;
	python_2.7/translate_USD.py raw_data/Fred/ data/Govt/
	python_2.7/translate_EUR.py raw_data/Bundesbank/ data/Govt/
	python_2.7/translate_JPY.py raw_data data/Govt/
	python_2.7/translate_GBP.py raw_data/Bank_of_England/ data/Govt/
	python_2.7/translate_CHF.py raw_data/Swiss_National_Bank/ data/Govt/
	python_2.7/translate_AUD.py raw_data/Reserve_Bank_of_Australia/ data/Govt/
	python_2.7/translate_NZD.py raw_data/Reserve_Bank_of_New_Zealand/ data/Govt/
	python_2.7/translate_CAD.py raw_data/Bank_of_Canada/ data/Govt/
	python_2.7/translate_SEK.py raw_data/Swedish_Riksbank/ data/Govt/
	python_2.7/translate_NOK.py raw_data/Norges_Bank/ data/Govt/

#
# Liao data
#
data/Liao/bonds.csv: python_2.7/cull_bonds_Liao.py
	mkdir -p data/Liao
	python_2.7/cull_bonds_Liao.py raw_data/ $@

data/Liao/prices/2017-3-8: python_2.7/price_and_yield_on_culled_bonds.py data/Liao/bonds.csv
	mkdir -p data/Liao/prices
	python_2.7/price_and_yield_on_culled_bonds.py data/Liao/bonds.csv raw_data/ data/Liao/prices/

data/Liao/prices_processed/2017-3-8: python_2.7/process_prices_Liao.py data/Liao/prices/2017-3-8
	mkdir -p data/Liao/prices_processed
	python_2.7/process_prices_Liao.py raw_data/currency_prices/ data/Liao/prices/ data/Liao/prices_processed/

data/Liao/regression_results.csv: R/regress_Liao_parallel.R data/Liao/prices_processed/2017-3-8
	Rscript R/regress_Liao_parallel.R data/Liao/prices_processed/ $@

data/Liao/regression_results_withCIP.csv: python_2.7/add_CIP_XCBS.py data/Liao/regression_results.csv
	python_2.7/add_CIP_XCBS.py raw_data/currency_prices/ data/Liao/regression_results.csv $@

#
# Govt data
#

data/Govt/bonds.csv: data/Liao/bonds.csv
	#head -1 data/Liao/bonds.csv > data/Govt/bonds.csv
	#egrep ",USD,|,EUR,|,JPY,|,GBP,|,CHF,|,AUD,|,NZD," data/Liao/bonds.csv >> data/Govt/bonds.csv
	mkdir -p data/Govt
	cp data/Liao/bonds.csv $@

data/Govt/prices/2017-3-8: python_2.7/price_and_yield_on_culled_bonds.py data/Govt/bonds.csv
	mkdir -p data/Govt/prices
	python_2.7/price_and_yield_on_culled_bonds.py data/Govt/bonds.csv raw_data/ data/Govt/prices

data/Govt/prices_processed/2017-3-8: python_2.7/process_prices_Govt.py data/Govt/prices/2017-3-8 data/Govt/govt20.csv
	mkdir -p data/Govt/prices_processed
	python_2.7/process_prices_Govt.py raw_data/currency_prices/ data/Govt/ data/Govt/prices/ data/Govt/prices_processed/

data/Govt/regression_results.csv: R/regress_Liao_parallel.R data/Govt/prices_processed/2017-3-8
	Rscript R/regress_Liao_parallel.R data/Govt/prices_processed/ $@

data/Govt/regression_results_withCIP.csv: python_2.7/add_CIP_XCBS_Govt.py data/Govt/govt20.csv data/Govt/regression_results.csv
	python_2.7/add_CIP_XCBS_Govt.py raw_data/currency_prices/ data/Govt/ 5 data/Govt/regression_results.csv $@


#
# Corporate 5Y CIP basis rate, using govt to convert bonds to 5 years equivalents
#

data/Corp5Y/prices_processed/2017-3-8: python_2.7/process_prices_Corp5Y.py data/Govt/prices/2017-3-8 data/Govt/govt20.csv
	mkdir -p data/Corp5Y
	mkdir -p data/Corp5Y/prices_processed
	python_2.7/process_prices_Corp5Y.py raw_data/currency_prices/ data/Govt/ data/Govt/prices/ data/Corp5Y/prices_processed/

data/Corp5Y/regression_results.csv: R/regress_Corp_parallel.R data/Corp5Y/prices_processed/2017-3-8
	Rscript R/regress_Corp_parallel.R data/Corp5Y/prices_processed/ $@

data/Corp5Y/regression_results_withCIP.csv: python_2.7/add_CIP_XCBS_Govt.py data/Corp5Y/regression_results.csv
	python_2.7/add_CIP_XCBS_Govt.py raw_data/currency_prices/ data/Govt/ 5 data/Corp5Y/regression_results.csv $@




#
# Images of CIP basis for all currencies
#

latex/thesis/images/Basis_all_govt_1Y.eps: python_2.7/plot_manyCIP2.py data/dates.txt data/Govt/govt20.csv raw_data/currency_prices/currencies*.csv
	python_2.7/plot_manyCIP2.py raw_data/currency_prices/ data/Govt/ data/dates.txt USD 1 govt_xcbs $@

latex/thesis/images/Basis_all_govt_2Y.eps: python_2.7/plot_manyCIP2.py data/dates.txt data/Govt/govt20.csv raw_data/currency_prices/currencies*.csv
	python_2.7/plot_manyCIP2.py raw_data/currency_prices/ data/Govt/ data/dates.txt USD 2 govt_xcbs $@

latex/thesis/images/Basis_all_govt_5Y.eps: python_2.7/plot_manyCIP2.py data/dates.txt data/Govt/govt20.csv raw_data/currency_prices/currencies*.csv
	python_2.7/plot_manyCIP2.py raw_data/currency_prices/ data/Govt/ data/dates.txt USD 5 govt_xcbs $@

latex/thesis/images/Basis_all_govt_10Y.eps: python_2.7/plot_manyCIP2.py data/dates.txt data/Govt/govt20.csv raw_data/currency_prices/currencies*.csv
	python_2.7/plot_manyCIP2.py raw_data/currency_prices/ data/Govt/ data/dates.txt USD 10 govt_xcbs $@


latex/thesis/images/Basis_all_xcbs_1Y.eps: python_2.7/plot_manyCIP2.py data/dates.txt data/Govt/govt20.csv raw_data/currency_prices/currencies*.csv
	python_2.7/plot_manyCIP2.py raw_data/currency_prices/ data/Govt/ data/dates.txt USD 1 xcbs $@

latex/thesis/images/Basis_all_xcbs_2Y.eps: python_2.7/plot_manyCIP2.py data/dates.txt data/Govt/govt20.csv raw_data/currency_prices/currencies*.csv
	python_2.7/plot_manyCIP2.py raw_data/currency_prices/ data/Govt/ data/dates.txt USD 2 xcbs $@

latex/thesis/images/Basis_all_xcbs_5Y.eps: python_2.7/plot_manyCIP2.py data/dates.txt data/Govt/govt20.csv raw_data/currency_prices/currencies*.csv
	python_2.7/plot_manyCIP2.py raw_data/currency_prices/ data/Govt/ data/dates.txt USD 5 xcbs $@

latex/thesis/images/Basis_all_xcbs_10Y.eps: python_2.7/plot_manyCIP2.py data/dates.txt data/Govt/govt20.csv raw_data/currency_prices/currencies*.csv
	python_2.7/plot_manyCIP2.py raw_data/currency_prices/ data/Govt/ data/dates.txt USD 10 xcbs $@


latex/thesis/images/Basis_all_bank_3M.eps: python_2.7/plot_manyCIP2.py data/dates.txt data/Govt/govt20.csv raw_data/currency_prices/currencies*.csv
	python_2.7/plot_manyCIP2.py raw_data/currency_prices/ data/Govt/ data/dates.txt USD .25 swap $@


#
# Images plotting swap rate minus the govt rate
#
latex/thesis/images/SwapVsGovt_all_2Y.eps: python_2.7/plot_swap_vs_govt.py data/dates.txt 
	python_2.7/plot_swap_vs_govt.py 2 raw_data/currency_prices/ data/ $@

latex/thesis/images/SwapVsGovt_all_20Y.eps: python_2.7/plot_swap_vs_govt.py data/dates.txt 
	python_2.7/plot_swap_vs_govt.py 20 raw_data/currency_prices/ data/ $@

#
# Swap-rate reproductions of Liao's Figure 4
#
latex/thesis/images/Liao2016Figure4_AUD_xcbs.eps: python_2.7/plot_graph.py data/Liao/regression_results_withCIP.csv
	python_2.7/plot_graph.py AUD AUD_err CIP_basis_XCBS_AUD data/Liao/regression_results_withCIP.csv $@ CIP_basis_AUD

latex/thesis/images/Liao2016Figure4_CAD_xcbs.eps: python_2.7/plot_graph.py data/Liao/regression_results_withCIP.csv
	python_2.7/plot_graph.py CAD CAD_err CIP_basis_XCBS_CAD data/Liao/regression_results_withCIP.csv $@ CIP_basis_CAD

latex/thesis/images/Liao2016Figure4_CHF_xcbs.eps: python_2.7/plot_graph.py data/Liao/regression_results_withCIP.csv
	python_2.7/plot_graph.py CHF CHF_err CIP_basis_XCBS_CHF data/Liao/regression_results_withCIP.csv $@ CIP_basis_CHF

latex/thesis/images/Liao2016Figure4_EUR_xcbs.eps: python_2.7/plot_graph.py data/Liao/regression_results_withCIP.csv
	python_2.7/plot_graph.py EUR EUR_err CIP_basis_XCBS_EUR data/Liao/regression_results_withCIP.csv $@ CIP_basis_EUR

latex/thesis/images/Liao2016Figure4_GBP_xcbs.eps: python_2.7/plot_graph.py data/Liao/regression_results_withCIP.csv
	python_2.7/plot_graph.py GBP GBP_err CIP_basis_XCBS_GBP data/Liao/regression_results_withCIP.csv $@ CIP_basis_GBP

latex/thesis/images/Liao2016Figure4_JPY_xcbs.eps: python_2.7/plot_graph.py data/Liao/regression_results_withCIP.csv
	python_2.7/plot_graph.py JPY JPY_err CIP_basis_XCBS_JPY data/Liao/regression_results_withCIP.csv $@ CIP_basis_JPY

latex/thesis/images/Liao2016Figure4_NOK_xcbs.eps: python_2.7/plot_graph.py data/Liao/regression_results_withCIP.csv
	python_2.7/plot_graph.py NOK NOK_err CIP_basis_XCBS_NOK data/Liao/regression_results_withCIP.csv $@ CIP_basis_NOK

latex/thesis/images/Liao2016Figure4_NZD_xcbs.eps: python_2.7/plot_graph.py data/Liao/regression_results_withCIP.csv
	python_2.7/plot_graph.py NZD NZD_err CIP_basis_XCBS_NZD data/Liao/regression_results_withCIP.csv $@ CIP_basis_NZD

latex/thesis/images/Liao2016Figure4_SEK_xcbs.eps: python_2.7/plot_graph.py data/Liao/regression_results_withCIP.csv
	python_2.7/plot_graph.py SEK SEK_err CIP_basis_XCBS_SEK data/Liao/regression_results_withCIP.csv $@ CIP_basis_SEK

#
# Govt-rate reproductions of Liao's Figure 4
#
latex/thesis/images/Liao2016Figure4_AUD_govt.eps: python_2.7/plot_graph.py data/Govt/regression_results_withCIP.csv
	python_2.7/plot_graph.py AUD AUD_err CIP_basis_XCBS_AUD data/Govt/regression_results_withCIP.csv $@ CIP_basis_AUD

latex/thesis/images/Liao2016Figure4_CAD_govt.eps: python_2.7/plot_graph.py data/Govt/regression_results_withCIP.csv
	python_2.7/plot_graph.py CAD CAD_err CIP_basis_XCBS_CAD data/Govt/regression_results_withCIP.csv $@ CIP_basis_CAD

latex/thesis/images/Liao2016Figure4_CHF_govt.eps: python_2.7/plot_graph.py data/Govt/regression_results_withCIP.csv
	python_2.7/plot_graph.py CHF CHF_err CIP_basis_XCBS_CHF data/Govt/regression_results_withCIP.csv $@ CIP_basis_CHF

latex/thesis/images/Liao2016Figure4_EUR_govt.eps: python_2.7/plot_graph.py data/Govt/regression_results_withCIP.csv
	python_2.7/plot_graph.py EUR EUR_err CIP_basis_XCBS_EUR data/Govt/regression_results_withCIP.csv $@ CIP_basis_EUR

latex/thesis/images/Liao2016Figure4_GBP_govt.eps: python_2.7/plot_graph.py data/Govt/regression_results_withCIP.csv
	python_2.7/plot_graph.py GBP GBP_err CIP_basis_XCBS_GBP data/Govt/regression_results_withCIP.csv $@ CIP_basis_GBP

latex/thesis/images/Liao2016Figure4_JPY_govt.eps: python_2.7/plot_graph.py data/Govt/regression_results_withCIP.csv
	python_2.7/plot_graph.py JPY JPY_err CIP_basis_XCBS_JPY data/Govt/regression_results_withCIP.csv $@ CIP_basis_JPY

latex/thesis/images/Liao2016Figure4_NOK_govt.eps: python_2.7/plot_graph.py data/Govt/regression_results_withCIP.csv
	python_2.7/plot_graph.py NOK NOK_err CIP_basis_XCBS_NOK data/Govt/regression_results_withCIP.csv $@ CIP_basis_NOK

latex/thesis/images/Liao2016Figure4_NZD_govt.eps: python_2.7/plot_graph.py data/Govt/regression_results_withCIP.csv
	python_2.7/plot_graph.py NZD NZD_err CIP_basis_XCBS_NZD data/Govt/regression_results_withCIP.csv $@ CIP_basis_NZD

latex/thesis/images/Liao2016Figure4_SEK_govt.eps: python_2.7/plot_graph.py data/Govt/regression_results_withCIP.csv
	python_2.7/plot_graph.py SEK SEK_err CIP_basis_XCBS_SEK data/Govt/regression_results_withCIP.csv $@ CIP_basis_SEK

#
# X-Y plots for swap data
#
latex/thesis/images/Liao2016Figure5_xcbs_alldata.eps: python_2.7/plot_XY.py data/Liao/regression_results_withCIP.csv
	python_2.7/plot_XY.py false data/Liao/regression_results_withCIP.csv $@
latex/thesis/images/Liao2016Figure5_xcbs_bounded.eps: python_2.7/plot_XY.py data/Liao/regression_results_withCIP.csv
	python_2.7/plot_XY.py true data/Liao/regression_results_withCIP.csv $@

#
# X-Y plots for govt data
#
latex/thesis/images/Liao2016Figure5_govt_alldata.eps: python_2.7/plot_XY.py data/Govt/regression_results_withCIP.csv
	python_2.7/plot_XY.py false data/Govt/regression_results_withCIP.csv $@

#
# Plot of CIP Corp all in one plot
#

latex/thesis/images/Basis_all_corp_5Y.eps: python_2.7/plot_manyCIP.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_manyCIP.py data/Corp5Y/regression_results_withCIP.csv "" "5 year, Corporate" $@

#
# Plot Corp CIP next to Govt CIP
#
latex/thesis/images/Basis_AUD_corp_5Y.eps: python_2.7/plot_single_corpCIP.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_single_corpCIP.py AUD raw_data/currency_prices/ data/Corp5Y/regression_results_withCIP.csv $@ 

latex/thesis/images/Basis_CAD_corp_5Y.eps: python_2.7/plot_single_corpCIP.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_single_corpCIP.py CAD raw_data/currency_prices/ data/Corp5Y/regression_results_withCIP.csv $@ 

latex/thesis/images/Basis_CHF_corp_5Y.eps: python_2.7/plot_single_corpCIP.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_single_corpCIP.py CHF raw_data/currency_prices/ data/Corp5Y/regression_results_withCIP.csv $@ 

latex/thesis/images/Basis_EUR_corp_5Y.eps: python_2.7/plot_single_corpCIP.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_single_corpCIP.py EUR raw_data/currency_prices/ data/Corp5Y/regression_results_withCIP.csv $@ 

latex/thesis/images/Basis_GBP_corp_5Y.eps: python_2.7/plot_single_corpCIP.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_single_corpCIP.py GBP raw_data/currency_prices/ data/Corp5Y/regression_results_withCIP.csv $@ 

latex/thesis/images/Basis_JPY_corp_5Y.eps: python_2.7/plot_single_corpCIP.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_single_corpCIP.py JPY raw_data/currency_prices/ data/Corp5Y/regression_results_withCIP.csv $@ 

latex/thesis/images/Basis_NOK_corp_5Y.eps: python_2.7/plot_single_corpCIP.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_single_corpCIP.py NOK raw_data/currency_prices/ data/Corp5Y/regression_results_withCIP.csv $@ 

latex/thesis/images/Basis_NZD_corp_5Y.eps: python_2.7/plot_single_corpCIP.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_single_corpCIP.py NZD raw_data/currency_prices/ data/Corp5Y/regression_results_withCIP.csv $@ 

latex/thesis/images/Basis_SEK_corp_5Y.eps: python_2.7/plot_single_corpCIP.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_single_corpCIP.py SEK raw_data/currency_prices/ data/Corp5Y/regression_results_withCIP.csv $@ 

#
# plot max CIP basis spread
#

latex/thesis/images/BasisSpread_all_swap_5Y.eps: python_2.7/plot_maxCIPspread.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_maxCIPspread.py data/Corp5Y/regression_results_withCIP.csv raw_data/currency_prices/ data/Govt/ $@ swapsonly

latex/thesis/images/BasisSpread_all_swapgovt_5Y.eps: python_2.7/plot_maxCIPspread.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_maxCIPspread.py data/Corp5Y/regression_results_withCIP.csv raw_data/currency_prices/ data/Govt/ $@

latex/thesis/images/BasisSpread_all_all_5Y.eps: python_2.7/plot_maxCIPspread.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_maxCIPspread.py data/Corp5Y/regression_results_withCIP.csv raw_data/currency_prices/ data/Govt/ $@ data/Corp5Y/regression_results_withCIP.csv

#
# Plot of Govt and Swap minus CIP Corp
#

latex/thesis/images/Basis_all_swapMinusCorp_5Y.eps: python_2.7/plot_manyCIP_minus.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_manyCIP_minus.py swap data/Corp5Y/regression_results_withCIP.csv raw_data/currency_prices/ data/Govt/ "5 year, Swap minus Corp" $@

latex/thesis/images/Basis_all_govtMinusCorp_5Y.eps: python_2.7/plot_manyCIP_minus.py data/Corp5Y/regression_results_withCIP.csv
	python_2.7/plot_manyCIP_minus.py govt data/Corp5Y/regression_results_withCIP.csv raw_data/currency_prices/ data/Govt/ "5 year, Govt. minus Corp" $@

#
# Plot Liao plot with CIP basis corp subtracted
#
latex/thesis/images/LiaoSendup_AUD_5Y.pdf: python_2.7/plot_graph2.py data/Liao/regression_results_withCIP.csv data/Corp5Y/regression_results.csv
	python_2.7/plot_graph2.py AUD AUD_err CIP_basis_XCBS_AUD data/Liao/regression_results_withCIP.csv $@ data/Corp5Y/regression_results.csv AUD AUD_err

latex/thesis/images/LiaoSendup_CAD_5Y.pdf: python_2.7/plot_graph2.py data/Liao/regression_results_withCIP.csv data/Corp5Y/regression_results.csv
	python_2.7/plot_graph2.py CAD CAD_err CIP_basis_XCBS_CAD data/Liao/regression_results_withCIP.csv $@ data/Corp5Y/regression_results.csv CAD CAD_err

latex/thesis/images/LiaoSendup_CHF_5Y.pdf: python_2.7/plot_graph2.py data/Liao/regression_results_withCIP.csv data/Corp5Y/regression_results.csv
	python_2.7/plot_graph2.py CHF CHF_err CIP_basis_XCBS_CHF data/Liao/regression_results_withCIP.csv $@ data/Corp5Y/regression_results.csv CHF CHF_err

latex/thesis/images/LiaoSendup_EUR_5Y.pdf: python_2.7/plot_graph2.py data/Liao/regression_results_withCIP.csv data/Corp5Y/regression_results.csv
	python_2.7/plot_graph2.py EUR EUR_err CIP_basis_XCBS_EUR data/Liao/regression_results_withCIP.csv $@ data/Corp5Y/regression_results.csv EUR EUR_err

latex/thesis/images/LiaoSendup_GBP_5Y.pdf: python_2.7/plot_graph2.py data/Liao/regression_results_withCIP.csv data/Corp5Y/regression_results.csv
	python_2.7/plot_graph2.py GBP GBP_err CIP_basis_XCBS_GBP data/Liao/regression_results_withCIP.csv $@ data/Corp5Y/regression_results.csv GBP GBP_err

latex/thesis/images/LiaoSendup_JPY_5Y.pdf: python_2.7/plot_graph2.py data/Liao/regression_results_withCIP.csv data/Corp5Y/regression_results.csv
	python_2.7/plot_graph2.py JPY JPY_err CIP_basis_XCBS_JPY data/Liao/regression_results_withCIP.csv $@ data/Corp5Y/regression_results.csv JPY JPY_err

latex/thesis/images/LiaoSendup_NOK_5Y.pdf: python_2.7/plot_graph2.py data/Liao/regression_results_withCIP.csv data/Corp5Y/regression_results.csv
	python_2.7/plot_graph2.py NOK NOK_err CIP_basis_XCBS_NOK data/Liao/regression_results_withCIP.csv $@ data/Corp5Y/regression_results.csv NOK NOK_err

latex/thesis/images/LiaoSendup_NZD_5Y.pdf: python_2.7/plot_graph2.py data/Liao/regression_results_withCIP.csv data/Corp5Y/regression_results.csv
	python_2.7/plot_graph2.py NZD NZD_err CIP_basis_XCBS_NZD data/Liao/regression_results_withCIP.csv $@ data/Corp5Y/regression_results.csv NZD NZD_err

latex/thesis/images/LiaoSendup_SEK_5Y.pdf: python_2.7/plot_graph2.py data/Liao/regression_results_withCIP.csv data/Corp5Y/regression_results.csv
	python_2.7/plot_graph2.py SEK SEK_err CIP_basis_XCBS_SEK data/Liao/regression_results_withCIP.csv $@ data/Corp5Y/regression_results.csv SEK SEK_err



#
# List of all images
#
images = \
	latex/thesis/images/Basis_all_govt_5Y.eps \
	latex/thesis/images/Basis_all_xcbs_5Y.eps \
	latex/thesis/images/Basis_all_bank_3M.eps \
	latex/thesis/images/SwapVsGovt_all_2Y.eps \
	latex/thesis/images/SwapVsGovt_all_20Y.eps \
	latex/thesis/images/Liao2016Figure4_AUD_xcbs.eps \
	latex/thesis/images/Liao2016Figure4_CAD_xcbs.eps \
	latex/thesis/images/Liao2016Figure4_CHF_xcbs.eps \
	latex/thesis/images/Liao2016Figure4_EUR_xcbs.eps \
	latex/thesis/images/Liao2016Figure4_GBP_xcbs.eps \
	latex/thesis/images/Liao2016Figure4_JPY_xcbs.eps \
	latex/thesis/images/Liao2016Figure4_NOK_xcbs.eps \
	latex/thesis/images/Liao2016Figure4_NZD_xcbs.eps \
	latex/thesis/images/Liao2016Figure4_SEK_xcbs.eps \
	latex/thesis/images/Liao2016Figure4_AUD_govt.eps \
	latex/thesis/images/Liao2016Figure4_CAD_govt.eps \
	latex/thesis/images/Liao2016Figure4_CHF_govt.eps \
	latex/thesis/images/Liao2016Figure4_EUR_govt.eps \
	latex/thesis/images/Liao2016Figure4_GBP_govt.eps \
	latex/thesis/images/Liao2016Figure4_JPY_govt.eps \
	latex/thesis/images/Liao2016Figure4_NOK_govt.eps \
	latex/thesis/images/Liao2016Figure4_NZD_govt.eps \
	latex/thesis/images/Liao2016Figure4_SEK_govt.eps \
	latex/thesis/images/Liao2016Figure5_xcbs_alldata.eps \
	latex/thesis/images/Liao2016Figure5_xcbs_bounded.eps \
	latex/thesis/images/Liao2016Figure5_govt_alldata.eps \
	latex/thesis/images/Basis_all_corp_5Y.eps \
	latex/thesis/images/Basis_AUD_corp_5Y.eps \
	latex/thesis/images/Basis_CAD_corp_5Y.eps \
	latex/thesis/images/Basis_CHF_corp_5Y.eps \
	latex/thesis/images/Basis_EUR_corp_5Y.eps \
	latex/thesis/images/Basis_GBP_corp_5Y.eps \
	latex/thesis/images/Basis_JPY_corp_5Y.eps \
	latex/thesis/images/Basis_NOK_corp_5Y.eps \
	latex/thesis/images/Basis_NZD_corp_5Y.eps \
	latex/thesis/images/Basis_SEK_corp_5Y.eps \
	latex/thesis/images/BasisSpread_all_swap_5Y.eps \
	latex/thesis/images/BasisSpread_all_swapgovt_5Y.eps \
	latex/thesis/images/BasisSpread_all_all_5Y.eps \
	latex/thesis/images/Basis_all_swapMinusCorp_5Y.eps \
	latex/thesis/images/Basis_all_govtMinusCorp_5Y.eps \
	latex/thesis/images/LiaoSendup_AUD_5Y.pdf \
	latex/thesis/images/LiaoSendup_CAD_5Y.pdf \
	latex/thesis/images/LiaoSendup_CHF_5Y.pdf \
	latex/thesis/images/LiaoSendup_EUR_5Y.pdf \
	latex/thesis/images/LiaoSendup_GBP_5Y.pdf \
	latex/thesis/images/LiaoSendup_JPY_5Y.pdf \
	latex/thesis/images/LiaoSendup_NOK_5Y.pdf \
	latex/thesis/images/LiaoSendup_NZD_5Y.pdf \
	latex/thesis/images/LiaoSendup_SEK_5Y.pdf \


#^^^^ Need two blank lines here ^^^^

#
# Latex files
#

latex/thesis/thesis.bbl: latex/currency_bibliography.bib latex/dataset_bibliography.bib $(images)
	cd latex/thesis && pdflatex -halt-on-error thesis
	cd latex/thesis && bibtex thesis

latex/talk/talk.pdf: latex/talk/talk.tex latex/thesis/thesis.bbl $(images)
	cd latex/talk && pdflatex -halt-on-error talk
	cd latex/talk && pdflatex -halt-on-error talk

latex/thesis/thesis.pdf: latex/thesis/thesis.tex latex/thesis/content.tex latex/thesis/appendix1.tex latex/thesis/appendix2.tex latex/thesis/thesis.bbl $(images)
	cd latex/thesis && pdflatex -halt-on-error thesis
	cd latex/thesis && pdflatex -halt-on-error thesis

spell: latex/thesis/content.tex
	aspell -t -c latex/thesis/content.tex

ftest: R/ftest.R data/Liao/regression_results_withCIP.csv data/Govt/regression_results_withCIP.csv
	Rscript R/ftest.R data/Liao/regression_results_withCIP.csv CIP_basis_XCBS_
	Rscript R/ftest.R data/Govt/regression_results_withCIP.csv CIP_basis_

test:
	python_2.7/duration_weight_lib.py
	python_2.7/rating_lib.py
	python_2.7/swap_rate_lib.py
	python_2.7/weighted_median.py