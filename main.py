import yfinance as yf
import math


def round_to_decimals(value, decimals):
    if not isinstance(value, (int, float)):
        raise TypeError("Value must be an int or float.")
    if not isinstance(decimals, int) or decimals < 0:
        raise ValueError("Decimals must be a non-negative integer.")

    factor = 10 ** decimals
    return math.floor(value * factor + 0.5) / factor
def get_stock_history(symbol: str, period: str ):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=period)
    
    print( {
        "dates": hist.index.strftime("%Y-%m-%d").tolist(),
        "close": hist["Close"].round(2).tolist(),
        "high": hist["High"].round(2).tolist(),
        "low": hist["Low"].round(2).tolist(),
        "volume": hist["Volume"].tolist()
    })

def summary(symbol : str, period: str= '1d'):
    ticker=yf.Ticker(symbol)
    hist=ticker.history(period=period)

    o=hist["Open"].iloc[0].round(2)
    f=hist["Close"].iloc[0].round(2)
    
    if (o>f):
        change=((o-f)/o)*100
        res=round_to_decimals(change,2)
        return res
    
    if (f>o):
        change=((f-o)/f)*100
        return change
    


dat=yf.Tickers('^GSPC')
for i in dat.tickers:
    print(i)
