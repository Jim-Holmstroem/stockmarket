#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import urllib2
import json
import sqlite3 as sql

from itertools import *
import operator

import os
import time

def get_data_directory():
    """gets the current directory, and creates it upon non-existance."""
    directory = "{home}/.stockmarket/data".format(home=os.path.expanduser('~'))
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory

def printer(thing):
    """printer for debugging"""
    print(thing)
    return thing

def datafile(name):
    return "{directory}/{name}.db".format(
        directory=get_data_directory(), 
        name=name
    )
def price_renderer(price):
    return ("%0.2f"%price).rjust(8,' ')+"SEK"

def weird_price(price):
    """Something is fishy with this stock."""
    if(price<0.0001):
        print("Something is fishy with this token, misspelling?")
        return True
    else:
        return False


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
                "CREATE TABLE cash \
                (money DOUBLE PRECISION);"
                )
            cur.execute(
                "INSERT INTO cash \
                VALUES(?);",
                (self.start_amount,)
            )
            cur.execute(
                "CREATE TABLE stocks\
                (token VARCHAR(8) NOT NULL UNIQUE, amount INT);"
            )
            cur.execute(
                "CREATE TABLE transactions \
                (id INTEGER PRIMARY KEY AUTOINCREMENT,\
                timestamp INT,\
                token VARCHAR(8) NOT NULL,\
                amount INT,\
                aprice DOUBLE PRECISION,\
                total DOUBLE PRECISION);"
            )
            #Empty transaction as startingpoint
            cur.execute(
                "INSERT INTO transactions \
                VALUES(null, strftime('%s', 'now'), ?, ?, ?, ?);",
                ("-", 0, 0.0, self.start_amount) 
            )
        except sql.Error as e:
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
        except sql.Error as e:
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

    def update_stock(self, token, amount):
        """Buy and sell(negative amount)
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
            if(weird_price(aprice)):
                return
            price = aprice*amount
            courtage = max(
                39, 
                0.0015*abs(price)
            )
            totalprice = price + courtage 
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
            cur.execute(
                    "INSERT INTO transactions VALUES(null,strftime('%s','now'),?,?,?,?);",
                    (token, amount, aprice, self.get_cash())
                    )
            con.commit()
            print(
                "{what} {amount} {token}-stocks for {price} {courtage_sign} {courtage}".format(
                    what=("Bought", "Sold")[ amount<0 ], 
                    amount=abs(amount),
                    token=token,
                    price=price_renderer(
                        abs(price)
                    ),
                    courtage_sign=("+", "-")[ amount<0 ],
                    courtage=price_renderer(
                        courtage
                    )
                )
            )
        except sql.Error as e:
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
        assert(not isinstance(symbols, basestring))
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
        
        except urllib2.HTTPError as e:
            print("HTTP error:", e.code)
        except urllib2.URLError as e:
            print("Network error:", e.reason)
        except Exception as e:
            print("lookup failed", e)
    
class Commander(object):
    def __init__(self):
        self.current_portfolio = None
        self.avaliable_options = [
            self.open,
            self.close,
            self.view,
            self.lookup,
            self.buy,
            self.sell,
            self.history,
            self.exit
        ]

    def exit(self):
        """EXIT - Exits the program"""
        print(
            "BYE!!1"
        )
        exit()

    def buy(self, token, amount):
        """BUY [token] [amount] - Buy a given amount of a stock ``token'' to current portfolio."""
        if(amount>0):
            try:
                self.current_portfolio.update_stock(
                    token, 
                    int(amount)
                )
            except Exception as e:
                print("Error:", e)
        else:
            print("Amount needs to be positive.")

    def sell(self, token, amount):
        """SELL [token] [amount] - Sell a given amount of a stock ``token'' to current portfolio."""
        if(amount>0):
            try:
                self.current_portfolio.update_stock(
                    token,
                    -int(amount)
                )
            except Exception as e:
                print("Error:",e)
        else:
            print("Amount needs to be positive.")

    def view(self):
        """VIEW - View the current portfolio."""
        stocks = self.current_portfolio.get_stocks()
        cash   = self.current_portfolio.get_cash()
        name   = self.current_portfolio.get_name()
        print(
            "Name:`{name}`".format(
                name=name
            )
        ) 
        print(
            "="*16
        )
        map(
            print, 
            self.current_portfolio.get_stocks()
        )
        print(
            "="*16
        )
        print(
            "Cash={cash}".format(
                cash=self.current_portfolio.get_cash()
            )
        )
        print(
            "Total value={value}".format(
                value=self.current_portfolio.get_value()
            )
        )

    def open(self, name):
        """OPEN [name] - Open a portfolio."""
        if(self.current_portfolio is None):
            self.current_portfolio = Portfolio(name) 
            print(
                "`{name}` open.".format(
                    name=name
                )
            )
        else:
            self.close()
            self.open(name)

    def close(self):
        """CLOSE - Close the current portfolio."""
        if(self.current_portfolio is not None):
            print(
                "Closing `{name}`.".format(
                    name=self.current_portfolio.get_name()
                )
            )
            self.current_portfolio = None
        else:
            print(
                "Nothing to close."
            )

    def lookup(self, token):
        """LOOKUP [token] - Lookup the current price of a stock ``token''."""
        aprice = Stockmarket.lookup(
            [token,]
        )[0]
        if(weird_price(aprice)):
            return
        print(
            "Current price: {aprice}.".format(
                aprice=price_renderer(
                    aprice
                )
            )
        )
    
    def history(self):
        """HISTORY - Shows the latest transaction history in current portfolio."""
        def renderer(row):
            return "{i}. {time}: {amount}*{token} a {aprice}. Cash={cash}.".format(
                i=str(
                    row[0]
                ).rjust(3,' '),
                time=time.ctime(
                    row[1]
                ),#localtime
                token=(
                    str(row[2]), 
                    "START"
                )[ row[2]=='-' ].ljust(9,' '),
                amount=str(
                    row[3]
                ).rjust(4,' '),
                aprice=price_renderer(
                    row[4]
                ),
                cash=price_renderer(
                    row[5]
                ),
            )

        map(
            print,
            map(
                renderer,
                self.current_portfolio.get_transactions()
            )
        )

    def help(self):
        """HELP - Displays this help message."""
        map(
            print, 
            map(
                operator.attrgetter('__doc__'), 
                self.avaliable_options
            )
        )

    def start(self):
        while(True):
            if(self.current_portfolio):
                header = "{name}>> ".format(
                    name=self.current_portfolio.get_name()
                )
            else:
                header = ">> "
            command=raw_input(
                header
            ).upper().split()

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

