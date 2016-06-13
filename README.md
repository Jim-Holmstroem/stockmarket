stockmarket
===========

Python game where you can buy and sell stocks.

Installation
============
* Download the package
* Unzip the package
* Open a terminal
* Type ``cd <unpacked-package-directory>/stockmarket``
* Then type ``python stockmarket.py``
* It will save the portfolios in your home directory so that they persist between runs

Demonstration
=============

```
[me@laptop stockmarket]$ python stockmarket.py 
>> help            
OPEN [name] - Open a portfolio.
CLOSE - Close the current portfolio.
VIEW - View the current portfolio.
LOOKUP [token] - Lookup the current price of a stock ``token''.
BUY [token] [amount] - Buy a given amount of a stock ``token'' to current portfolio.
SELL [token] [amount] - Sell a given amount of a stock ``token'' to current portfolio.
HISTORY - Shows the latest transaction history in current portfolio.
EXIT - Exits the program
>> open myportfolio
Starting a new portfolio.
`MYPORTFOLIO` open.
MYPORTFOLIO>> lookup goog
Current price:   5991.53SEK.
MYPORTFOLIO>> buy goog 1
Bought 1 GOOG-stocks for   5960.10SEK +     39.00SEK
MYPORTFOLIO>> lookup aapl
Current price:    818.15SEK.
MYPORTFOLIO>> view
Name:`MYPORTFOLIO`
================
   1*GOOG     
================
 Cash=  4000.90SEK
Value=  9956.47SEK
MYPORTFOLIO>> buy aapl 3
Bought 3 AAPL-stocks for   2454.46SEK +     39.00SEK
MYPORTFOLIO>> view
Name:`MYPORTFOLIO`
================
   1*GOOG     
   3*AAPL     
================
 Cash=  1507.44SEK
Value=  9919.04SEK
MYPORTFOLIO>> sell aapl 1
Sold 1 AAPL-stocks for    818.15SEK -     39.00SEK
MYPORTFOLIO>> view
Name:`MYPORTFOLIO`
================
   1*GOOG     
   2*AAPL     
================
 Cash=  2286.60SEK
Value=  9887.82SEK
MYPORTFOLIO>> history
  1. Mon Jun 13 17:23:01 2016:    0*START     a      0.00SEK. Cash= 10000.00SEK.
  2. Mon Jun 13 17:23:28 2016:    1*GOOG      a   5960.10SEK. Cash=  4000.90SEK.
  3. Mon Jun 13 17:24:00 2016:    3*AAPL      a    818.15SEK. Cash=  1507.44SEK.
  4. Mon Jun 13 17:24:53 2016:   -1*AAPL      a    818.15SEK. Cash=  2286.60SEK.
MYPORTFOLIO>> close
Closing `MYPORTFOLIO`.
```
