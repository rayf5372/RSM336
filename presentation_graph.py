import yfinance as yf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt

# --- Settings ---
TICKER = "EFR.TO"
START_DATE = "2025-01-01"
END_DATE = "2025-11-14"
SPLIT_DATE = dt.datetime(2025, 10, 7)   # split date

# --- Fetch data ---
def fetch_stock_data(ticker, start_date, end_date):
    return yf.download(ticker, start=start_date, end=end_date)

# --- Plot ---
def plot_stock_data(stock_data, ticker):
    plt.figure(figsize=(14, 7))

    # Apply font style
    plt.rcParams['font.family'] = 'Palatino'
    plt.rcParams['font.size'] = 14

    # Split data
    before = stock_data.loc[stock_data.index <= SPLIT_DATE]
    after = stock_data.loc[stock_data.index >= SPLIT_DATE]

    # Plot before period (blue-ish)
    plt.plot(
        before.index, 
        before['Close'],
        color=(30/255, 60/255, 96/255),
        linewidth=2.4
    )
    
    # Plot holding period (red)
    plt.plot(
        after.index, 
        after['Close'],
        color='red',
        linewidth=2.4,
        label="Holding Period"
    )

    # Annotation line at the split date
    plt.axvline(SPLIT_DATE, color='grey', linestyle='--', linewidth=1)
    plt.text(
        SPLIT_DATE, 
        stock_data['Close'].max()*0.97, 
        "Entry Date", 
        fontsize=13,
        rotation=90,
        va='top',
        ha='right',
        color='grey'
    )

    # Labels
    plt.xlabel("Date")
    plt.ylabel("Price (CAD)")
    plt.legend(frameon=False)

    # Remove grid + clean borders
    plt.grid(False)
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    plt.show()

# --- Run ---
if __name__ == "__main__":
    stock_data = fetch_stock_data(TICKER, START_DATE, END_DATE)
    plot_stock_data(stock_data, TICKER)
