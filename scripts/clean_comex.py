"""Clean the CME/COMEX Midwest premium futures price histories downloaded by hand into data/raw/comex.

Contract: Aluminum MW U.S. Transaction Premium Platts (25MT), CME symbol AUP, Barchart root IAU. It is
cash-settled on the monthly average of the Platts MW premium, like the LME contract in
midwest_premium_curve.csv, but it is where most of the volume trades. Barchart allows one download a day,
one contract per file, named e.g. iauv26_price-history-10-09-2026.csv (contract Oct 2026, downloaded
9 Oct 2026). Prices are in USD/lb. "Latest" on a past day is the settlement price, also on days with no
trades. The file ends with a "Downloaded from Barchart.com ..." footer row.

Output:
    data/midwest_premium_cme.csv  date, contract_month, premium_usd_t, premium_cpl, volume, open_interest

Usage:
    python scripts/clean_comex.py
"""

import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw" / "comex"
OUT = ROOT / "data" / "midwest_premium_cme.csv"

LB_PER_T = 2204.62262
MONTH_CODES = "FGHJKMNQUVXZ"   # Jan..Dec
FILE_RE = re.compile(r"^iau([fghjkmnquvxz])(\d{2})_price-history-(\d{2})-(\d{2})-(\d{4})\.csv$")


def read_file(path: Path) -> pd.DataFrame:
    code, yy, mm, dd, yyyy = FILE_RE.match(path.name).groups()
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["Time"], format="%Y-%m-%d", errors="coerce")
    df = df.dropna(subset=["date"])   # drops the Barchart footer row
    df["contract_month"] = pd.Timestamp(2000 + int(yy), MONTH_CODES.index(code.upper()) + 1, 1)
    df["downloaded"] = pd.Timestamp(int(yyyy), int(mm), int(dd))
    df["premium_cpl"] = df["Latest"] * 100
    df["premium_usd_t"] = df["Latest"] * LB_PER_T
    df = df.rename(columns={"Volume": "volume", "Open Int": "open_interest"})
    return df.astype({"volume": int, "open_interest": int})


def main() -> None:
    files = sorted(p for p in RAW.glob("*.csv") if FILE_RE.match(p.name))
    if not files:
        raise SystemExit(f"No Barchart IAU files in {RAW}")
    df = pd.concat([read_file(p) for p in files])
    # The same contract downloaded twice: keep the later download, which has the longer history
    df = (df.sort_values("downloaded")
            .drop_duplicates(["date", "contract_month"], keep="last")
            .sort_values(["contract_month", "date"]))
    cols = ["date", "contract_month", "premium_usd_t", "premium_cpl", "volume", "open_interest"]
    df[cols].to_csv(OUT, index=False, float_format="%.3f")
    for cm, g in df.groupby("contract_month"):
        print(f"{cm:%b %y}: {len(g)} days, {g['date'].min():%Y-%m-%d} to {g['date'].max():%Y-%m-%d}")
    print(f"Saved {len(df)} rows -> {OUT}")


if __name__ == "__main__":
    main()
