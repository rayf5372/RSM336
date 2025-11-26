import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def calc_12_1m_return(ticker: str):
    """
    Calculate the 12-1 month momentum return for a given ticker.
    Definition: (Price_1M_Ago / Price_12M_Ago) - 1
    """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=550)  # ~18 months for buffer

    # Download daily data
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if data.empty:
        raise ValueError(f"No data found for {ticker}")

    # Resample to monthly frequency, take last close of each month
    monthly = data['Adj Close'].resample('M').last()

    # Ensure we have at least 13 months of data
    if len(monthly) < 13:
        raise ValueError(f"Not enough data for {ticker}")

    price_1m_ago = monthly.iloc[-2]     # price 1 month ago
    price_12m_ago = monthly.iloc[-13]   # price 12 months ago

    momentum = (price_1m_ago / price_12m_ago - 1) * 100  # percent return

    print(f"{ticker}: 12-1M return = {momentum:.2f}%")
    return momentum

# Example usage:
if __name__ == "__main__":
    for t in ["RNMBY"]:
        try:
            calc_12_1m_return(t)
        except Exception as e:
            print(f"Error for {t}: {e}")
