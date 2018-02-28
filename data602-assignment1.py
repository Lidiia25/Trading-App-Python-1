#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 27 19:42:29 2018

@author: lidiiatronina
"""



import datetime
import pandas as pd
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as soup



def get_yahoo_price(name):
    if (name not in stocks):
        return -1
    url = 'https://finance.yahoo.com/quote/' + name + '?p=' + name
    Client = uReq(url)
    page_html = Client.read()
    Client.close()
    page_soup = soup(page_html, "html.parser")
    price_container = page_soup.findAll("div", {"data-test":"quote-header"})
    price_scraped= price_container[0].text
    sub_a = price_scraped.find("USD")
    yahoo_pr= price_scraped[sub_a+3:]
    sub_b = yahoo_pr.find('.')
    yahoo_price= yahoo_pr[:sub_b+3]
    yahoo_price = float(yahoo_price.replace(',',''))
    return yahoo_price 


cash = 100000000
stocks = [
    "AAPL", "AMZN", "INTC", "MSFT", "SNAP"
]
transactions = []
stock_balance = [0, 0, 0, 0, 0]

while(True):
    print ("Welcome,")
    print("Please choose from following options:")
    print("1. Trade")
    print("2. Show Blotter")
    print("3. Show P/L")
    print("4. Quit")
    choice = input()
    if choice == "1":
        print("What would you like to do?")
        print("1. Buy")
        print("2. Sell")
        choice_buy_sale = input()
        if (choice_buy_sale == "1"):        
            print("Which of the following stock would you like to buy?")
            i = 1
            for stock in stocks:
                print(str(i) + ". " + stock)
                i += 1

            stock_index = int(input()) - 1
            if stock_index > len(stocks):
                print("error")
            else:
                qty = int(input("Please choose quantity:"))
                price = get_yahoo_price(stocks[stock_index])
                sum = qty * price
                if (sum > cash):
                    print("There isn’t enough money")
                else:
                    print("Would you like to confirm, that you are going to buy %d stocks for the price of %.2f (Total = %.2f)" % (qty, price, sum))
                    if (input("Please select:\n1. Yes, I confirm\n2. No") == "1"):
                        price = get_yahoo_price(stocks[stock_index])
                        sum = qty * price
                        if (sum > cash):
                            print("There isn’t enough money")
                        else:
                            cash -= sum
                            print("Thank you! Your transaction went through. Ramaining balance is ", cash)
                            stock_balance[stock_index] += qty
                            transactions.append({
                                "date": datetime.datetime.now(),
                                "price": price,
                                "qty": qty,
                                "ticker": stocks[stock_index],
                                "side": "buy"
                            })
        elif (choice_buy_sale == "2"):
            print("Which of the following stock would you like to sell?")
            i = 1
            for stock in stocks:
                print(str(i) + ". " + stock)
                i += 1

            stock_index = int(input()) - 1
            if stock_index > len(stocks):
                print("Error")
            else:
                qty = int(input("Please choose quantity:"))
                price = get_yahoo_price(stocks[stock_index])
                sum = qty * price
                if (qty > stock_balance[stock_index]):
                    print("You don’t have enough stocks to complete this transaction")
                else:
                    print("Would you like to confirm, that you are going to sell %d stocks for the price of %.2f (Total = %.2f)" % (qty, price, sum))
                    if (input("Please select:\n1. Yes, I confirm\n2. No") == "1"):
                        price = get_yahoo_price(stocks[stock_index])
                        sum = qty * price
                        if (qty > stock_balance[stock_index]):
                            print("You don’t have enough stocks to complete this transaction")
                        else:
                            cash += sum
                            print("Thank you! Your transaction went through. Ramaining balance is ", cash)
                            stock_balance[stock_index] -= qty
                            transactions.append({
                                "date": datetime.datetime.now(),
                                "price": price,
                                "qty": qty,
                                "ticker": stocks[stock_index],
                                "side": "sell"
                            })
    elif choice == "2":
        blotter =  pd.DataFrame.from_dict(transactions,orient='columns', dtype=None)
        blotter_df = blotter.assign(money_in_out = blotter.qty* blotter.price)
        blotter_df = blotter_df[['side', 'ticker', 'qty', 'price', 'date', 'money_in_out']]
        print(blotter_df)
    elif choice == "3":
        sum = [0, 0, 0, 0, 0]
        bought = [0, 0, 0, 0, 0]
        rpl = [0, 0, 0, 0, 0]
        last_price = [0, 0, 0, 0, 0]
        wap = [0, 0, 0, 0, 0]
        for ts in transactions:
            ticker_index = stocks.index(ts['ticker'])
            if (ts['side'] == 'buy'):
                sum[ticker_index] += ts['price'] * ts['qty']
                bought[ticker_index] += ts['qty']
            last_price[ticker_index] = ts['price']
        for i in range(len(stocks)):
            wap[i] = sum[i] / bought[i] if bought[i] > 0 else 0
        for ts in transactions:
            if (ts['side'] == 'sell'):
                ticker_index = stocks.index(ts['ticker'])
                rpl[ticker_index] = ts['qty'] * (ts['price'] - wap[ticker_index])
        pl_table = []
        for i in range(len(stocks)):
            pl_table.append({
                'Ticker': stocks[i],
                'Position': stock_balance[i],
                'Market': '%.2f' % (last_price[i]),
                'WAP': '%.2f' % (wap[i]),
                'UPL': '%.2f' % (stock_balance[i] * (last_price[i] - wap[i])),
                'RPL': '%.2f' % (rpl[i])
            })
        pl_table.append({
            'Ticker': 'Cash',
            'Position': '%.2f' % (cash),
            'Market': '%.2f' % (cash),
            'WAP': '',
            'UPL': '',
            'RPL': ''
        })
        pl =  pd.DataFrame.from_dict(pl_table,orient='columns', dtype=None)
        pl_df = pl[['Ticker', 'Position', 'Market', 'WAP', 'UPL', 'RPL']]
        print(pl_df)
    elif choice == "4":
        exit()