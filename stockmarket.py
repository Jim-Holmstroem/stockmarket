import urllib2
import json
import sqlite3

from itertools import *
import operator

class Portfolio(object):
    def __init__(self, name):
        self.name = name

    def get_stocks(self):
        """
        {"tokens":['AAPL','GOOG'],"amount":[3,4]}
        """
        return db.klsjdfjlksf 

    def sell_stock(self,token,amount):
        pass

    def buy_stock(self):
        pass

    def current_value(self):
        stocks = self.get_stocks() 
        return self.cash + sum(starmap(operator.mul, izip( stocks["amount"], map(Stockmarket.lookup, stocks["tokens"]))

class Stockmarket(object):

    @staticmethod
    def lookup(symbols):
        yql = "select LastTradePriceOnly from yahoo.finance.quotes where symbol in ('{params}')".format(params="','".join(symbols)) 
                        
        url = "http://query.yahooapis.com/v1/public/yql?q={q}&format=json&env=http%3A%2F%2Fdatatables.org%2Falltables.env&callback=".format(q=urllib2.quote( yql ))

        try: 
            result = urllib2.urlopen(url)
        except urllib2.HTTPError, e:        
            print ("HTTP error: ", e.code)        
        except urllib2.URLError, e:
            print ("Network error: ", e.reason)
           
        data = json.loads( result.read() )
        jsonQuotes = data['query']['results']['quote']
        
        pythonQuotes = []
        if type( jsonQuotes ) == type ( dict() ):
            pythonQuotes.append( jsonQuotes )
        else:
            pythonQuotes = jsonQuotes
       
        pythonQuotes = map(lambda x: float(x['LastTradePriceOnly']), pythonQuotes)
        return pythonQuotes

print Stockmarket.lookup(['AAPL','GOOG'])
