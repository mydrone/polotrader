import requests
import json
import hmac
import random
import urllib, urllib2
import hashlib


tradingApiUrl = 'http://poloniex.com/tradingApi'
publicApiUrl  = 'http://poloniex.com/public?'
rateApiUrl    = 'http://blockchain.info/ticker'

# PUBLIC API
# https://poloniex.com/public?command=returnTicker
# https://poloniex.com/public?command=return24hVolume
# https://poloniex.com/public?command=returnOrderBook&currencyPair=BTC_NXT&depth=10
# https://poloniex.com/public?command=returnTradeHistory&currencyPair=BTC_NXT&start=1410158341&end=1410499372
# https://poloniex.com/public?command=returnChartData&currencyPair=BTC_XMR&start=1405699200&end=9999999999&period=14400
# https://poloniex.com/public?command=returnCurrencies
# https://poloniex.com/public?command=returnLoanOrders&currency=BTC


class publicTrading:

    def __init__(self, apiUrl, rateUrl):
        self.base_url = apiUrl
        self.rate_url = rateUrl

    def getBTCRate(self):
        url=self.rate_url
        req = requests.post(url)
        print "Status: %d" % req.status_code
        tickers = req.json()
        return float(tickers['USD']['last'])
	
    def returnTickerData(self, tickers):
        res=[]
        url = self.base_url
        data = {'command': 'returnTicker'}

        req = requests.get(url, params=data)

        print "Status: %d" % req.status_code

        tickerData = req.json() 
  
        rate = self.getBTCRate()

        for tickerPair in sorted(tickerData):
            if "BTC_" in tickerPair: # Values against BTC only?
                ticker1, ticker2 = tickerPair.split("_")
                if ticker2 in tickers: # is it in the list passed? 
                    price = float(tickerData[tickerPair]['last'])*rate
                    change = float(tickerData[tickerPair]['percentChange']) * 100
                    volume = float(tickerData[tickerPair]['baseVolume'])
                    res.append( {ticker2: {'price': price, 'volume': volume, 'change': change}} )
        return res

    def return24hVol(self, tickers):
        res=[]
        url = self.base_url
        data = {'command': 'return24hVolume'}

        req = requests.get(url, params=data)

        print "Status: %d" % req.status_code

        tickerData = req.json()

        for tickerPair in sorted(tickerData):
            if "BTC_" in tickerPair:
				ticker1, ticker2 = tickerPair.split("_")
				if ticker2 in tickers:
					ticker2Volume = float(tickerData[tickerPair][ticker2])
					res.append({ticker2: {'volume': ticker2Volume}})
        return res

    def returnOrderBook(self, ticker, depth):
        res=[]
        url = self.base_url
        pair = "BTC_"+ticker

        #if ticker == 'all'
        #    data = {'command':'returnOrderBook', 'currencyPair': 'all', 'depth': depth}
        #else:
        #    data = {'command':'returnOrderBook', 'currencyPair': pair, 'depth': depth}

        data = {'command':'returnOrderBook', 'currencyPair': pair, 'depth': depth}

        req = requests.get(url, params=data)

        print "Status: %d" % req.status_code

        orders = req.json()

        bids = orders['bids']
        asks = orders['asks']
        frozen = orders['isFrozen']

        return orders
		

    def returnTradeHist(self, ticker, start=0, end=0):
        res=[]
        url = self.base_url
        pair = "BTC_"+ticker
        #data = {'command':'returnTradeHistory', 'currencyPair': pair, 'start': start, 'end': end}
        data = {'command':'returnTradeHistory', 'currencyPair': pair}

        req = requests.get(url, params=data)

        print "Status: %d" % req.status_code

        trades = req.json()
    
        for trade in trades:
            amount = trade['amount']
            ttype   = trade['type']
        
            res.append({'amount': amount, 'type': ttype})

        return res

    def returnChartData(self, ticker, start=0, end=0, period=0):
        res=[]
        url = self.base_url
        pair = "BTC_"+ticker
        data = {'command':'returnChartData', 'currencyPair': pair}
        #data = {'command':'returnChartData', 'curencyPair': pair, 'start': start, 'end': end, 'period': period}
        req = requests.get(url, params=data)

        print "Status: %d" % req.status_code

        chartData = req.json()

        print chartData
        return chartData
            

    def returnCurrencies(self):
        res=[]
        url = self.base_url
        data = {'command':'returnCurrencies'}

        req = requests.get(url, params=data)

        print "Status: %d" % req.status_code

        currencies = req.json()

        print currencies

        return currencies

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
 

p = publicTrading(publicApiUrl, rateApiUrl)
#pv = privateTrading(publicApiUrl, rateApiUrl, tradingApiUrl)
#pv.setKey('')
#pv.setSecret('')

#balances = pv.returnBalances()
tickers =  p.returnTickerData(['LTC', 'ETH', 'NXT'])
tickers =  p.return24hVol(['LTC', 'ETH', 'NXT'])
tickers = p.returnOrderBook('ETH', 1)
tickers = p.returnTradeHist('ETH',0 ,0)
tickers= p.returnChartData('ETH', 0 , 0)
tickers = p.returnCurrencies()

#for ticker in tickers:
#    change = tickers[ticker]['change']
#    print "%s %0.2f" % (ticker, change), 
#    if change < -5:
#        print "Buy!"
#        #pv.buy(ticker, amount)
#    elif change > 5:
#        print "Sell!"
#        #pv.sell(ticker, amount)
#    else:
#        print "Hold!"
         
    

#p.returnTicker()
#p.return24hVol()
#p.returnOrderBook('BTC_NXT', 10)
#p.returnTradeHist('BTC_NXT', 100, 200)
#p.returnChartData('BTC_NXT', 100, 200, 300)
#p.returnCurrencies()
#p.returnLoanOrders('BTC')


