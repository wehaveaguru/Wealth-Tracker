import yfinance as yf

dat=yf.Ticker("AAPL")

print(dat.financials)
