import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------
# Value sleeve tickers
# ------------------------------
VALUE_TICKERS = [
    "DIS",        # Disney (US)
    "MAT",        # Mattel (US)
    "RCI-B.TO",   # Rogers Communications, Class B, TSX
    "T.TO",       # TELUS, TSX
    "BAM.TO",     # Brookfield Asset Management, TSX
    "SU.TO",      # Suncor, TSX
    "EXC",        # Exelon (US)
    "ALGN",       # Align Technology (US)
    "DLTR",       # Dollar Tree (US)
    "CAG",        # Conagra (US)
    "STLA",       # Stellantis (US listing)
    "HST",        # Host Hotels & Resorts (US)
    "IBM",        # IBM (US)
    "5930.T",     # Bunka Shutter (Tokyo)
    "VTV",        # Vanguard Value ETF (US)
    "6301.T",     # Komatsu (Tokyo)
    "6305.T",     # Hitachi Construction Machinery (Tokyo)
    "CI",         # Cigna Group (US)
    "C",          # Citigroup (US)
    "EIX",        # Edison International (US)
    "5802.T",     # Sumitomo Electric (Tokyo)
    "9532.T"      # Osaka Gas (Tokyo)
]

# ------------------------------
# Momentum sleeve tickers
# ------------------------------
MOM_TICKERS = [
    "HOOD",       # Robinhood (US)
    "PLTR",       # Palantir (US)
    "OKLO",       # Oklo Inc. (US)
    "TMC",        # TMC the metals company (US)
    "K",          # Kellanova (US)
    "AVGO",       # Broadcom (US)
    "FMCC",       # Freddie Mac (OTC)
    "RKLB",       # Rocket Lab (US)
    "HWKN",       # Hawkins (US)
    "GE",         # GE Aerospace (US)
    "TSLA",       # Tesla (US)
    "MP",         # MP Materials (US)
    "HIMS",       # Hims & Hers (US)
    "CDE",        # Coeur Mining (US)
    "EFR.TO",     # Energy Fuels (TSX)
    "WWW",        # Wolverine World Wide (US)
    "MFI.TO",     # Maple Leaf Foods (TSX)
    "RHM.DE",     # Rheinmetall (XETRA)
    "JOBY",       # Joby Aviation (US)
    "TPR",        # Tapestry (US)
    "MU",         # Micron Technology (US)
    "NVDA"        # NVIDIA (US)
]

TSX_ETFS = {
    "XIT.TO": "Information Technology",
    "XEG.TO": "Energy",
    "XFN.TO": "Financials",
    "XRE.TO": "Real Estate",
    
 
}

START_DATE = "2025-10-06"
END_DATE   = "2025-11-14"

# ---- Sector mapping (broad buckets)
SECTOR_MAP = {
    # VALUE
    "DIS": "Communication Services",
    "MAT": "Consumer Discretionary",
    "RCI-B.TO": "Communication Services",
    "T.TO": "Communication Services",
    "BAM.TO": "Financials",
    "SU.TO": "Energy",
    "EXC": "Utilities",
    "ALGN": "Health Care",
    "DLTR": "Consumer Staples",
    "CAG": "Consumer Staples",
    "STLA": "Consumer Discretionary",
    "HST": "Real Estate",
    "IBM": "Information Technology",
    "5930.T": "Industrials",
    "VTV": "Multi-Sector ETF",
    "6301.T": "Industrials",
    "6305.T": "Industrials",
    "CI": "Health Care",
    "C": "Financials",
    "EIX": "Utilities",
    "5802.T": "Industrials",
    "9532.T": "Utilities",
    # MOMENTUM
    "HOOD": "Financials",
    "PLTR": "Information Technology",
    "OKLO": "Energy",
    "TMC": "Materials",
    "K": "Consumer Staples",
    "AVGO": "Information Technology",
    "FMCC": "Financials",
    "RKLB": "Industrials",
    "HWKN": "Materials",
    "GE": "Industrials",
    "TSLA": "Consumer Discretionary",
    "MP": "Materials",
    "HIMS": "Health Care",
    "CDE": "Materials",
    "EFR.TO": "Materials",
    "WWW": "Consumer Discretionary",
    "MFI.TO": "Consumer Staples",
    "RHM.DE": "Industrials",
    "JOBY": "Industrials",
    "TPR": "Consumer Discretionary",
    "MU": "Information Technology",
    "NVDA": "Information Technology",
}


def fetch_prices(tickers, start_date, end_date):
    """Download adjusted close prices for all tickers."""
    raw_data = yf.download(tickers, start=start_date, end=end_date)

    if len(tickers) == 1:
        data = raw_data["Adj Close"].to_frame(name=tickers[0])
    else:
        if isinstance(raw_data.columns, pd.MultiIndex) and "Adj Close" in raw_data.columns.levels[0]:
            data = raw_data["Adj Close"]
        elif "Adj Close" in raw_data.columns:
            data = raw_data[["Adj Close"]]
        else:
            data = raw_data["Close"]

    return data.ffill().dropna(how="all")


if __name__ == "__main__":
    # 1) Fetch data
    all_tickers = list(set(VALUE_TICKERS + MOM_TICKERS))
    prices = fetch_prices(all_tickers, START_DATE, END_DATE)
    prices = prices.sort_index()

    # 2) Daily returns
    daily_rets = prices.pct_change().dropna()

    # 3) Equal-weight sleeve returns
    value_rets = daily_rets[VALUE_TICKERS].mean(axis=1)
    mom_rets   = daily_rets[MOM_TICKERS].mean(axis=1)

    # 4) Total return over the period for each sleeve
    value_total = (1 + value_rets).prod() - 1
    mom_total   = (1 + mom_rets).prod() - 1

    print("==== Sleeve Returns ({} to {}) ====".format(START_DATE, END_DATE))
    print(f"Value sleeve total return:     {value_total:.2%}")
    print(f"Momentum sleeve total return:  {mom_total:.2%}")

    # 5) Correlation analysis
    corr_daily    = mom_rets.corr(value_rets)
    corr_spearman = mom_rets.corr(value_rets, method='spearman')
    weekly_mom    = mom_rets.resample('W').sum()
    weekly_value  = value_rets.resample('W').sum()
    corr_weekly   = weekly_mom.corr(weekly_value)
    rolling_corr_series = mom_rets.rolling(5).corr(value_rets)
    rolling_corr = rolling_corr_series.median()

    print("\n==== Correlation Analysis ====")
    print(f"Daily returns correlation (Pearson):  {corr_daily:.3f}")
    print(f"Daily returns correlation (Spearman): {corr_spearman:.3f}")
    print(f"Weekly returns correlation:           {corr_weekly:.3f}")
    print(f"Median 5-day rolling correlation:     {rolling_corr:.3f}")

    # 6) Cumulative return plot (for slides)
    value_cum = (1 + value_rets).cumprod() - 1
    mom_cum   = (1 + mom_rets).cumprod() - 1

    plt.rcParams['font.family'] = 'Palatino'

    plt.figure(figsize=(12, 6))
    plt.plot(value_cum.index, value_cum, label="Value Stocks", linewidth=2.2,
             color=(30/255, 60/255, 96/255))
    plt.plot(mom_cum.index, mom_cum, label="Momentum Stocks", linewidth=2.2,
             color=(234/255, 51/255, 35/255))

    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_xticklabels([])
    ax.set_xticks([])

    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    plt.ylabel("Cumulative Return")
    plt.legend(frameon=False)
    plt.grid(False)
    plt.title("Momentum vs Value Stocks: Cumulative Returns (2025-10-06 to 2025-11-14)")
    plt.show()

    # 7) Sector-level performance inside each sleeve
    print("\n==== Sector Attribution (Equal-weight within sleeve) ====")

    def sector_attribution(ticker_list, name):
        # group tickers by sector
        sector_to_tickers = {}
        for t in ticker_list:
            if t not in daily_rets.columns:
                continue
            sector = SECTOR_MAP.get(t, "Other")
            sector_to_tickers.setdefault(sector, []).append(t)

        rows = []
        for sector, ticks in sector_to_tickers.items():
            sector_ret_series = daily_rets[ticks].mean(axis=1)
            total_ret = (1 + sector_ret_series).prod() - 1
            rows.append((sector, len(ticks), total_ret))

        df = pd.DataFrame(rows, columns=["Sector", "Num_Tickers", "Total_Return"])
        df = df.sort_values("Total_Return")
        print(f"\n{name} sleeve:")
        print(df.to_string(index=False))

    sector_attribution(VALUE_TICKERS, "Value")
    sector_attribution(MOM_TICKERS, "Momentum")
    
    # 8) Industry/Sector Performance Graph
    print("\n==== All Sector Performance Analysis ====")
    
    # Calculate sector returns across all tickers
    sector_returns = {}
    sector_tickers_count = {}
    
    for ticker in all_tickers:
        if ticker not in daily_rets.columns:
            continue
        sector = SECTOR_MAP.get(ticker, "Other")
        if sector not in sector_returns:
            sector_returns[sector] = []
            sector_tickers_count[sector] = 0
        sector_returns[sector].append(daily_rets[ticker])
        sector_tickers_count[sector] += 1
    
    # Calculate equal-weighted sector performance
    sector_performance = {}
    sector_cumulative = {}
    
    for sector, returns_list in sector_returns.items():
        if len(returns_list) >= 1:  # Include all sectors
            sector_daily_returns = pd.concat(returns_list, axis=1).mean(axis=1)
            sector_performance[sector] = sector_daily_returns
            sector_cumulative[sector] = (1 + sector_daily_returns).cumprod() - 1
    
    # Get all sectors sorted by total return
    sector_total_returns = {sector: (1 + returns).prod() - 1 
                           for sector, returns in sector_performance.items()}
    all_sectors = sorted(sector_total_returns.items(), key=lambda x: x[1], reverse=True)
    
    print(f"All Sectors by Total Return:")
    for i, (sector, total_ret) in enumerate(all_sectors, 1):
        ticker_count = sector_tickers_count[sector]
        print(f"{i}. {sector}: {total_ret:.2%} ({ticker_count} stocks)")
    
    # Plot all sectors
    plt.figure(figsize=(14, 8))
    
    # Color palette for all sectors - using a variety of colors
    import matplotlib.cm as cm
    import numpy as np
    colors = cm.tab10(np.linspace(0, 1, len(all_sectors)))
    
    for i, (sector, _) in enumerate(all_sectors):
        cum_returns = sector_cumulative[sector]
        plt.plot(cum_returns.index, cum_returns, 
                label=f"{sector} ({sector_tickers_count[sector]} stocks)", 
                linewidth=2.0, color=colors[i])
    
    # Apply same styling as value/momentum graph
    ax = plt.gca()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.set_xticklabels([])
    ax.set_xticks([])
    
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    plt.ylabel("Cumulative Return")
    plt.legend(frameon=False, loc='best')
    plt.grid(False)
    plt.title("All Sector Performance: Cumulative Returns (2025-10-06 to 2025-11-14)")
    plt.show()
