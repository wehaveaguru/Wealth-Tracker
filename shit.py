import yfinance as yf

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


