# carry_trade_paper

This repository holds the code and text to generate my thesis for my
Masters of Arts in Economic from the University of Texas at Austin.

**_The repository is missing proprietary Bloomberg data.  Please
  contact me at michael at nahas dot com to get the data._**

Requirements:
* Quantlib (finance library), version 1.9.2
  * Quantlib-SWIG (python interface to Quantlib), version 1.9
* R
  * lmtest library 
  * sandwich library 
  * multiwayvcov library 
  * parallel library 
* python version 2.7
  * matplotlib library
  * scipy library
  * numpy library
  * pandas library
* LaTeX (pdflatex)
  * graphicx package
  * hyperref package
  * epsfig package
  * _others, used by UT style file_
* make

NOTE: C# was used to download the data from Bloomberg, but is not
necessary to compile the document.

To compile, run: "make"

