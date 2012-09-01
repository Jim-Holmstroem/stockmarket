from __future__ import print_function

import urllib2
import json
import sqlite3 as sql

from itertools import *
import operator

import os.path

def datafile(name):
    return "../data/{name}.db".format(name=name)

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
            cur.execute("CREATE TABLE cash (money DOUBLE PRECISION);")
            cur.execute("INSERT INTO cash VALUES({start_amount});".format(start_amount=self.start_amount))
            cur.execute("CREATE TABLE stocks (token VARCHAR(8) NOT NULL UNIQUE,amount INT);")
            cur.execute("CREATE TABLE transactions (token VARCHAR(8) NOT NULL UNIQUE,amount INT,aprice DOUBLE PRECISION);")
        except sql.Error as e:
            raise e
        finally:
            if con:
                con.commit()
                con.close()

    def get_cash(self):
        try:
            con = sql.connect(datafile(self.name))
            cur = con.cursor()
            cur.execute("SELECT money FROM cash;")
            return cur.fetchone()[0]
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
            cur.execute("SELECT * FROM stocks;")
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
            
            int(amount) #making sure

            cur.execute("SELECT count(*) FROM stocks WHERE token=?;",(token,))
            if(cur.fetchone()[0]==0): #check if exists already, if not create it
                cur.execute("INSERT INTO stocks VALUES ( ? , ? );",(token,0))
            
            aprice = Stockmarket.lookup([token,])[0] #check price
            cur.execute("UPDATE cash SET money = ( money - ({withdraw}) );".format(withdraw=aprice*amount)) #draw cash
            cur.execute("UPDATE stocks SET amount = ( amount + ({damount}) ) WHERE token = ?;".format(damount=amount),(token,)) #get the stock
            
        except sql.Error as e:
            raise e
        finally:
            if con:
                con.commit()
                con.close()

    def current_value(self):
        value = self.get_cash()
        stocks = zip(*self.get_stocks()) #transpose the stocks
        if(stocks):
            value += sum(starmap(operator.mul, izip( stocks[1], map(Stockmarket.lookup, stocks[0]))))
        return value

class Stockmarket(object):
    @staticmethod
    def lookup(symbols):
        yql = "select LastTradePriceOnly from yahoo.finance.quotes where symbol in ('{params}')".format(params="','".join(symbols)) 
                        
        url = "http://query.yahooapis.com/v1/public/yql?q={q}&format=json&env=http%3A%2F%2Fdatatables.org%2Falltables.env&callback=".format(q=urllib2.quote( yql ))

        try: 
            result = urllib2.urlopen(url)
            rawdata = result.read()
            data = json.loads( rawdata )
            jsonQuotes = data['query']['results']['quote']
            
            pythonQuotes = []
            if type( jsonQuotes ) == type ( dict() ):
                pythonQuotes.append( jsonQuotes )
            else:
                pythonQuotes = jsonQuotes
           
            pythonQuotes = map(lambda x: float(x['LastTradePriceOnly']), pythonQuotes)
            return pythonQuotes
        
        except urllib2.HTTPError, e:
            print("HTTP error: ", e.code)
            raise e
        except urllib2.URLError, e:
            print("Network error: ", e.reason)
            raise e
        except Exception, e:
            print("lookup failed", e)
            raise e

        
p = Portfolio("sofia")
print("stocks =",p.get_stocks())
print(p.current_value())
p.update_stock("GOOG",2)
print("stocks =",p.get_stocks())
print(p.current_value())
