import urllib2
import json
import sqlite3 as sql

from itertools import *
import operator

import os.path

def datafile(name):
    return "../{name}.db".format(name=name)

class Portfolio(object):
    start_amount = 10000

    def __init__(self, name):
        self.name = name
        if(not self.__has_database()):
            self.__setup_database()

    def __has_database(self):
        return os.path.isfile(datafile(self.name))

    def __setup_database(self):
        try:
            con = sql.connect(datafile(self.name))
            cur = con.cursor()
            cur.execute("CREATE TABLE cash (double precision money);")
            cur.execute("INSERT INTO cash VALUES({start_amount});".format(start_amount=self.start_amount))
            cur.execute("CREATE TABLE stocks (unique string token,int amount);")
            cur.execute("CREATE TABLE transactions (primary key autoincrement int,string token,int amount,double precision aprice);")
        except sql.Error as e:
            raise e
        finally:
            if con:
                con.close()

    def get_stocks(self):
        """
        {"tokens":['AAPL','GOOG'],"amount":[3,4]}
        """
        try:
            con = sql.connect(datafile(self.name))
            cur = con.cursor()
            cur.execute("SELECT * FROM stocks")
            return list(cur.fetchall())
        except sql.Error as e:
            raise e
        finally:
            if con:
                con.close()

    def update_stock(self,token,amount):
        """
        buy and sell (negative amount)
        """
        try:
            con = sql.connect(datafile(self.name))
            cur = con.cursor()
            cur.execute("UPDATE stocks SET amount=(amount ?) WHERE token='?'",("%+d"%amount,abs(amount),token))
        except sql.Error as e:
            raise e
        finally:
            if con:
                con.close()
        

    def current_value(self):
        stocks = zip(*self.get_stocks())
        return self.cash + sum(starmap(operator.mul, izip( stocks[1], map(Stockmarket.lookup, stocks[0]))

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
