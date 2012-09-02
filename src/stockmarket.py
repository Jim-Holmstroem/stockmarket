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
            print("Starting a new portfolio.")
            self.__setup_database()

    def __has_database(self):
        return os.path.isfile(datafile(self.name))

    def __setup_database(self):
        try:
            con = sql.connect(datafile(self.name))
            cur = con.cursor()
            cur.execute(
                    "CREATE TABLE cash (money DOUBLE PRECISION);"
                    )
            cur.execute(
                    "INSERT INTO cash VALUES(?);",
                    (self.start_amount,)
                    )
            cur.execute(
                    "CREATE TABLE stocks (token VARCHAR(8) NOT NULL UNIQUE,amount INT);"
                    )
            cur.execute(
                    "CREATE TABLE transactions (id INTEGER PRIMARY KEY AUTOINCREMENT,timestamp INT,token VARCHAR(8) NOT NULL,amount INT,aprice DOUBLE PRECISION,total DOUBLE PRECISION);"
                    )
            cur.execute(
                    "INSERT INTO transactions VALUES(null,strftime('%s','now'),?,?,?,?);",
                    ("-", 0, 0.0, self.start_amount) #make an empty transaction as startingpoint
                    )
        except sql.Error, e:
            raise e
        finally:
            if con:
                con.commit()
                con.close()

    def get_name(self):
        return self.name

    def get_cash(self):
        try:
            con = sql.connect(datafile(self.name))
            cur = con.cursor()
            cur.execute("SELECT money FROM cash;")
            return cur.fetchone()[0]
        except sql.Error, e:
            raise e
        finally:
            if con:
                con.close()

    def get_transactions(self):
        try:
            con = sql.connect(datafile(self.name))
            cur = con.cursor()
            cur.execute("SELECT * FROM transactions;")
            return list(cur.fetchall())
        except sql.Error, e:
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
        except sql.Error, e:
            raise e
        finally:
            if con:
                con.close()

    def update_stock(self, token, amount):
        """
        buy and sell(negative amount)
        """
        try:
            con = sql.connect(datafile(self.name))
            cur = con.cursor()

            cur.execute(
                    "SELECT count(*) FROM stocks WHERE token=?;",
                    (token,)
                    )
            
            if(cur.fetchone()[0]==0): #check if exists already, if not create it
                cur.execute(
                        "INSERT INTO stocks VALUES(?,?);",
                        (token, 0)
                        )
            cur.execute(
                    "SELECT amount from stocks WHERE token=?;",
                    (token,)
                    )
            stockcount=cur.fetchone()[0]
            if(amount<0 and stockcount<abs(amount)):
                print("You don't have that much stock to sell.")
                return

            total = self.get_value()
            aprice = Stockmarket.lookup([token,])[0] #check price
            price = aprice*amount
            totalprice = (
                    price,
                    max(
                        price+39,
                        price*1.0015
                        )
                    )[0<amount]
            
            if(amount>0 and totalprice>self.get_cash()):#bying and cash isn't enough
                print("Not enough money, sorry.")
                return

            cur.execute(
                    "UPDATE cash SET money = ( money - (?) );",
                    (totalprice,)
                    ) #draw cash
            cur.execute(
                    "UPDATE stocks SET amount = ( amount + (?) ) WHERE token = ?;",
                    (amount, token)
                    ) #get the stock
            con.commit()
            print("{what} {amount} {token} stocks.".format(what=("Bought","Sold")[amount<0],amount=abs(amount),token=token))
            cur.execute(
                    "INSERT INTO transactions VALUES(null,strftime('%s','now'),?,?,?,?);",
                    (token, amount, aprice, self.get_cash())
                    )

        except sql.Error, e:
            raise e
        finally:
            if con:
                con.commit()
                con.close()

    def get_value(self):
        value = self.get_cash()
        stocks = zip(*self.get_stocks()) #transpose the stocks

        if(stocks):
            value+=sum(
                    starmap(
                    operator.mul,
                    ( 
                        zip(
                            stocks[1],
                            Stockmarket.lookup(
                                stocks[0]
                                )
                            )
                        )
                    )
                )
        return value

class Stockmarket(object):
    @staticmethod
    def lookup(symbols):
        yql = "select LastTradePriceOnly from yahoo.finance.quotes where symbol in ('{params}')".format(params="','".join(symbols)) 
        url = "http://query.yahooapis.com/v1/public/yql?q={q}&format=json&env=http%3A%2F%2Fdatatables.org%2Falltables.env&callback=".format(q=urllib2.quote( yql ))

        try: 
            result = urllib2.urlopen(url)
            rawdata = result.read()
            data = json.loads(rawdata)
            json_quotes = data['query']['results']['quote']
            
            python_quotes = []
            if isinstance(json_quotes, dict):
                python_quotes.append(json_quotes)
            else:
                python_quotes = json_quotes
           
            python_quotes = map(lambda x: float(x['LastTradePriceOnly']), python_quotes)
            return python_quotes
        
        except urllib2.HTTPError, e:
            print("HTTP error:", e.code)
            raise e
        except urllib2.URLError, e:
            print("Network error:", e.reason)
            raise e
        except Exception, e:
            print("lookup failed", e)
            raise e

class Commander(object):
    def __init__(self):
        self.current_portfolio = None
    def exit(self):
        print("BYE!!1")
        exit()
    def buy(self, stock, amount):
        if(amount>0):
            try:
                self.current_portfolio.update_stock(stock, int(amount))
            except Exception, e:
                print(e)
                print("Error..")
        else:
            print("Amount needs to be positive.")

    def sell(self, stock, amount): #TODO change stock to token instead.
       if(amount>0):
           try:
               self.current_portfolio.update_stock(stock,-int(amount))
           except Exception, e:
               print(e)
               print("Error..")
       else:
           print("Amount needs to be positive.")

    def view(self):
        stocks = self.current_portfolio.get_stocks()
        cash   = self.current_portfolio.get_cash()
        name   = self.current_portfolio.get_name()
        print("Name:`{name}`".format(name=name)) 
        print("="*16)
        map(print, self.current_portfolio.get_stocks())
        print("="*16)
        print("Cash={cash}".format(cash=self.current_portfolio.get_cash()))
        print("Total value={value}".format(value=self.current_portfolio.get_value()))

    def open(self, name):
        if(self.current_portfolio is None):
            self.current_portfolio = Portfolio(name) 
            print("`{name}` open.".format(name=name))
        else:
            self.close()
            self.open(name)

    def close(self):
        if(self.current_portfolio is not None):
            print("Closing `{name}`.".format(name=self.current_portfolio.get_name()))
            self.current_portfolio = None
        else:
            print("Nothing to close.")

    def lookup(self, stock):
        print("Current price:{price}.".format(price=Stockmarket.lookup([stock,])[0]))
    
    def help(self):
        print("OPEN [name] - Open a portfolio.")
        print("CLOSE - Close the current portfolio.")
        print("VIEW - View the current portfolio.")
        print("LOOKUP [stock] - Lookup the current price of a stock.")
        print("BUY [stock] [amount] - Buy a given amount of a stock to current portfolio.")
        print("SELL [stock] [amount] - Sell a given amount of a stock to current portfolio.")
        print("HISTORY - Shows the latest transaction history in current portfolio.") 
        print("HELP - Displays this help message.")
        print("EXIT - Exits the program")

    def history(self):
        history = self.current_portfolio.get_transactions()
        map(print,history)

    def start(self):
        while(True):
            command=raw_input(">>").upper().split()
            if(len(command)==0):
                continue
            
            if(command[0]=="EXIT"):
                if(len(command)==1):
                    self.exit()
                else: 
                    print("Wrong number of arguments.")

            elif(command[0]=="OPEN"):
                if(len(command)==2):
                    self.open(command[1])
                else:
                    print("Wrong number of arguments.")

            elif(command[0]=="CLOSE"):
                if(len(command)==1):
                    self.close()
                else: 
                    print("Wrong number of arguments.")

            elif(command[0]=="VIEW"):
                if(len(command)==1):
                    self.view()
                else: 
                    print("Wrong number of arguments.")

            elif(command[0]=="BUY"):
                if(len(command)==3):
                    self.buy(command[1], command[2])
                else:
                    print("Wrong number of arguments.")

            elif(command[0]=="SELL"):
                if(len(command)==3):
                    self.sell(command[1], command[2])
                else: 
                    print("Wrong number of arguments.")

            elif(command[0]=="LOOKUP"):
                if(len(command)==2):
                    self.lookup(command[1])
                else: 
                    print("Wrong number of arguments.")

            elif(command[0]=="HISTORY"):
                if(len(command)==1):
                    self.history()
                else: 
                    print("Wrong number of arguments.")

            elif(command[0]=="HELP"):
                if(len(command)==1):
                    self.help()
                else: 
                    print("Wrong number of arguments.")

            else:
                print("{command} is an unknown command.".format(command=command[0]))

def test():        
    p = Portfolio("test")
    
    print("stocks =",p.get_stocks(),"/",p.get_cash())
    print(p.get_value())

    p.update_stock("GOOG",2)
    print("stocks =",p.get_stocks(),"/",p.get_cash())
    print(p.get_value())

    p.update_stock("AAPL",2)
    print("stocks =",p.get_stocks(),"/",p.get_cash())
    print(p.get_value())

    p.update_stock("AAPL",-2)
    print("stocks =",p.get_stocks(),"/",p.get_cash())
    print(p.get_value())

    p.update_stock("GOOG",-2)
    print("stocks =",p.get_stocks(),"/",p.get_cash())
    print(p.get_value())

#test()

Commander().start()

