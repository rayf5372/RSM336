import os, re
import numpy as np
import pandas as pd
import yfinance as yf


INPUT_CSV = r"C:\Users\rfang\Documents\RSM336\yf_us_can.csv"  
OUT_DIR   = r"C:\Users\rfang\Documents\RSM336\out"

LOOKBACK_MONTHS = 18    
MIN_MONTHS      = 14    

CORRECTIONS = {
    # US share classes
    "BRK.A":"BRK-A", "BF.B":"BF-B",
    "FWON-K":"FWONK", "FWON-A":"FWONA",
    "BATR-K":"BATRK", "BATR-A":"BATRA",
    "LBRD-K":"LBRDK", "LBRD-A":"LBRDA",
    "LBTY-A":"LBTYA", "LBTY-K":"LBTYK",
    "RUSH-A":"RUSHA", 
    "BBD.B.TO":"BBD-B.TO", "BEI.UN.TO":"BEI-UN.TO",
    "ARTG.TO":"ARTG.V",  
    "TOI.TO":"TOI.V",   
}

ALLOWED_SUFFIXES = {"", ".TO", ".V", ".NE"} 

def sanitize(t: str) -> str:
    if not isinstance(t, str): return ""
    s = t.strip().upper()
    s = re.sub(r"\s+", "", s)
    s = CORRECTIONS.get(s, s)
    s = re.sub(r"\.([A-Z])$", r"-\1", s)
    s = re.sub(r"^([A-Z0-9]+)-([A-Z])$", r"\1\2", s)
    s = re.sub(r"^([A-Z0-9]+)\.([A-Z0-9]+)\.(TO|V|NE)$", r"\1-\2.\3", s)
    m = re.search(r"\.[A-Z]{1,3}$", s)
    if m and m.group(0) not in ALLOWED_SUFFIXES:
        return ""
    return s

def to_month_end(df):  
    return df.resample("ME").last()

def compute_mom_12_1(prices_m):
    rets = prices_m.pct_change()
    ex_last = rets.shift(1)                               
    sig = (1.0 + ex_last).rolling(11).apply(np.prod) - 1.0  
    s = sig.iloc[-1]; s.name = "mom_12_1"
    return s

def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # 1) Load + clean tickers
    dfu = pd.read_csv(INPUT_CSV, encoding="utf-8-sig")
    if "ticker" not in dfu.columns:
        dfu = dfu.rename(columns={dfu.columns[0]:"ticker"})
    tickers = [sanitize(x) for x in dfu["ticker"].astype(str).tolist()]
    tickers = [t for t in tickers if t]               
    tickers = sorted(set(tickers))
    if not tickers:
        raise RuntimeError("No valid US/CA tickers after sanitization.")

    # 2) Download daily closes 
    days = int(LOOKBACK_MONTHS * 31)
    data = yf.download(
        tickers, period=f"{days}d",
        auto_adjust=True, progress=False,
        group_by="column", threads=False
    )
    close = data["Close"] if isinstance(data, pd.DataFrame) and "Close" in data.columns else data
    if close is None or close.empty:
        raise RuntimeError("No price data returned. Update yfinance or check network.")

    close = close.loc[:, close.notna().sum() > 0]
    if close.shape[1] == 0:
        raise RuntimeError("All tickers had no price history in the window.")

    # 3) Monthly series 
    prices_m = to_month_end(close)
    keep = prices_m.count() >= MIN_MONTHS
    prices_m = prices_m.loc[:, keep.index[keep]]
    if prices_m.shape[1] == 0:
        raise RuntimeError("No tickers have enough monthly history for 12–1.")

    # 4) Momentum + last-month
    mom = compute_mom_12_1(prices_m)
    last_m = prices_m.pct_change().iloc[-1].rename("ret_t_1")

    out = pd.concat([mom, last_m], axis=1)
    out.index.name = "ticker"         
    out = out.reset_index().dropna(subset=["mom_12_1"])

    # 5) Global ranking 
    out["rank"] = out["mom_12_1"].rank(method="first", ascending=False)
    out["pct_rank"] = out["mom_12_1"].rank(pct=True, ascending=False)

    top10 = out[out["pct_rank"] > 0.90].sort_values("rank")[["ticker","mom_12_1","rank","pct_rank"]]
    bot10 = out[out["pct_rank"] <= 0.10].sort_values("rank")[["ticker","mom_12_1","rank","pct_rank"]]

    # 6) Save
    top_path = os.path.join(OUT_DIR, "top_10pct.csv")
    bot_path = os.path.join(OUT_DIR, "bottom_10pct.csv")
    top10.to_csv(top_path, index=False)
    bot10.to_csv(bot_path, index=False)

    print(f"Done.\n  {top_path}\n  {bot_path}")

if __name__ == "__main__":
    main()
