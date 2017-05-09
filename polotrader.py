import requests
import json
import hmac
import random
import urllib, urllib2
import hashlib


tradingApiUrl = 'https://poloniex.com/tradingApi'
publicApiUrl  = 'https://poloniex.com/public?'
BTCRateApi    = 'https://blockchain.info/ticker'

# PUBLIC API
# https://poloniex.com/public?command=returnTicker
# https://poloniex.com/public?command=return24hVolume
# https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_NXT&depth=10
# https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_NXT&start=1410158341&end=1410499372
# https://poloniex.com/public?command=returnChartData&currencyPair=BTC_XMR&start=1405699200&end=9999999999&period=14400
# https://poloniex.com/public?command=returnCurrencies
# https://poloniex.com/public?command=returnLoanOrders&currency=BTC


class publicTrading:

    def __init__(self, apiUrl, exchangeUrl):
        self.base_url = apiUrl
        self.rate_url = exchangeUrl

    def getBTCRate(self):
        url=self.rate_url
        req = requests.post(url)
        print "Status: %d" % req.status_code
        tickers = req.json()
        return float(tickers['USD']['last'])
	
    def returnTicker(self, x):
        url = self.base_url+'command=returnTicker'
        res={}
        req = requests.post(url)
        print "Status: %d" % req.status_code
        tickers = req.json()    
        rate = self.getBTCRate()

        for pair in sorted(tickers):
            if "BTC_" in pair:
                ticker = pair.split("_")[1]
                if ticker in x:
                    price = float(tickers[pair]['last'])*rate
                    change = float(tickers[pair]['percentChange']) * 100
                    volume = float(tickers[pair]['baseVolume'])
                    res[ticker] = {'price': price, 'change': change, 'volume': volume}            
        return res
	                # create object from dict tickers[ticker]

    
    def return24hVol(self):
        url = self.base_url+'command=return24hVolume'
        req = requests.post(url)
        print "Status: %d" % req.status_code
        tickers = req.json()
        for ticker in sorted(tickers):
            if "BTC_" in ticker:
                first, second = ticker.split('_')
                secondVolume = float(tickers[ticker][second])
                print "%s Vol: %f" % (second, secondVolume)

    def returnOrderBook(self, pair, depth):
        payload = {'curencyPair': pair, 'depth': depth}
        url = self.base_url+'returnOrderBook'
        req = requests.post(url, data=payload)

    def returnTradeHist(self, pair, start, end):
        payload = {'curencyPair': pair, 'start': start, 'end': end}
        url = self.base_url+'command=returnTradeHistory'
        req = requests.post(url, data=payload)

    def returnChartData(self, pair, start, end, period):
        payload = {'curencyPair': pair, 'start': start, 'end': end, 'period': period}
        url = self.base_url+'command=returnChartData'
	print url
        requests.post(url, data=payload)

    def returnCurrencies(self):
        url = self.base_url+'command=returnCurrencies'
        req = requests.post(url, data=payload)

    def returnLoanOrders(self, currency):
	    payload = {'currency': currency}
	    url = self.base_url+'command=returnLoanOrders'
	    req = requests.post(url, data=payload)

class privateTrading(publicTrading):
    def __init__(self, apiUrl, exchangeUrl, tradingUrl):
	    publicTrading.__init__(self, apiUrl, exchangeUrl)
	    self.trade_url = tradingUrl
	    self.key = ''
	    self.secret=''
	    self.nonce = 0

    def setKey(self, key):
	    self.key = key

    def getKey(self):
	    return self.key

    def setSecret(self, secret):
	    self.secret = secret

    def getSecret(self):
        return self.secret

    def getNonce(self):
        f = open('nonce.txt', 'r+b')
        self.nonce = int(f.readline())
        self.nonce += 1
        f.seek(0)
        f.write(str(self.nonce))
        f.close()
        return self.nonce

    def returnBalances(self):
        url = self.trade_url
        key = self.getKey()
        secret = self.getSecret()
        nonce = self.getNonce()
        x = {}

        dict_data = {'command': 'returnBalances', 'nonce': nonce}
        post_data = urllib.urlencode(dict_data)
        print dict_data
        print post_data
        exit(1)
	    
        sign = hmac.new(secret, post_data, hashlib.sha512).hexdigest()

        headers = {'Sign': sign, 'Key': key}

        req = requests.post(url, data=dict_data, headers=headers)

        print "Status: %d" % req.status_code
        
        balances = req.json()

        for ticker in balances:
            balance = float(balances[ticker])

            if(balance > 0):
                x[ticker] = balance

        return x
 
	
	#for ticker in tickers:
	#     if (float(tickers[ticker]) > 0):
	#         print "%s %f"% (ticker, float(tickers[ticker]))
 

#p = publicTrading(publicApiUrl, BTCRateApi)
pv = privateTrading(publicApiUrl, BTCRateApi, tradingApiUrl)
pv.setKey('')
pv.setSecret('')

balances = pv.returnBalances()
tickers =  pv.returnTicker(balances.keys())

for ticker in tickers:
    change = tickers[ticker]['change']
    print "%s %0.2f" % (ticker, change), 
    if change < -5:
        print "Buy!"
        #pv.buy(ticker, amount)
    elif change > 5:
        print "Sell!"
        #pv.sell(ticker, amount)
    else:
        print "Hold!"
         
    

#p.returnTicker()
#p.return24hVol()
#p.returnOrderBook('BTC_NXT', 10)
#p.returnTradeHist('BTC_NXT', 100, 200)
#p.returnChartData('BTC_NXT', 100, 200, 300)
#p.returnCurrencies()
#p.returnLoanOrders('BTC')


