"""Reconstruct the Rotterdam duty-unpaid premium (DUP) from the duty-paid premium (DP).

The observed DUP series (investing.com) stops in Oct 2025, while DP (LME ED settlements) runs to
Aug 2026. Duty-paid metal has had the EU import duty (3% on unwrought aluminium, charged on the
value LME + DUP) paid, so

    DP = DUP + r * (LME + DUP)    =>    DUP = (DP - r * LME) / (1 + r)

where r is the *effective* duty rate. It sits below the statutory 3% because part of the metal in
Rotterdam comes from duty-free origins (Norway, Iceland, FTA partners), and it moves with how much
of that metal is around. It is fitted on the overlap Jul 2021 - Oct 2025:

    mid   median r over the overlap
    low   10th percentile -> higher DUP
    high  statutory 3% cap / 90th percentile, whichever is larger -> lower DUP

Feb-May 2025 is a regime break: r collapsed to ~0% as metal turned away from the US by the 25%
tariff flooded Europe. Those months are kept in the backtest but left out of the fit.

Output:
    data/europe_duty_unpaid_premium_reconstructed.csv
        date, lme_cash, dp, dup_observed, rate_observed, dup_mid, dup_low, dup_high,
        premium_usd_t, premium_cpl, source
    premium_usd_t is the observed DUP where it exists, dup_mid otherwise; source says which.

Usage:
    python scripts/reconstruct_duty_unpaid.py
"""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = DATA / "europe_duty_unpaid_premium_reconstructed.csv"

LB_PER_T = 2204.62262
STATUTORY = 0.03
BREAK = ("2025-02-01", "2025-05-01")  # tariff-shock months left out of the fit


def load() -> pd.DataFrame:
    lme = (pd.read_csv(DATA / "lme_aluminium.csv", parse_dates=["date"])
           .set_index("date")["cash"].resample("MS").mean())
    dup = pd.read_csv(DATA / "europe_duty_unpaid_premium.csv", parse_dates=["date"]).set_index("date")["premium_usd_t"]
    dp = pd.read_csv(DATA / "europe_duty_paid_premium.csv", parse_dates=["date"]).set_index("date")["premium_usd_t"]
    df = pd.DataFrame({"lme_cash": lme, "dp": dp, "dup_observed": dup}).dropna(subset=["dp"])
    return df.dropna(subset=["lme_cash"])


def reconstruct(dp: pd.Series, lme: pd.Series, r: float) -> pd.Series:
    return (dp - r * lme) / (1 + r)


def main() -> None:
    df = load()
    df["rate_observed"] = (df["dp"] - df["dup_observed"]) / (df["lme_cash"] + df["dup_observed"])

    fit = df["rate_observed"].dropna().drop(pd.date_range(*BREAK, freq="MS"), errors="ignore")
    r_mid, r_low = fit.median(), fit.quantile(0.10)
    r_high = max(STATUTORY, fit.quantile(0.90))
    print(f"Effective duty rate on {len(fit)} months: low {r_low:.2%}, mid {r_mid:.2%}, high {r_high:.2%}")

    df["dup_mid"] = reconstruct(df["dp"], df["lme_cash"], r_mid)
    df["dup_low"] = reconstruct(df["dp"], df["lme_cash"], r_high)  # higher rate -> lower DUP
    df["dup_high"] = reconstruct(df["dp"], df["lme_cash"], r_low)

    err = (df["dup_mid"] - df["dup_observed"]).dropna()
    calm = err.drop(pd.date_range(*BREAK, freq="MS"), errors="ignore")
    print(f"Backtest (mid - observed), USD/t: mean {calm.mean():+.1f}, MAE {calm.abs().mean():.1f}, "
          f"max {calm.abs().max():.1f} excl. break; break months {err.loc[BREAK[0]:BREAK[1]].round(0).tolist()}")

    df["source"] = df["dup_observed"].notna().map({True: "observed", False: "reconstructed"})
    df["premium_usd_t"] = df["dup_observed"].fillna(df["dup_mid"])
    df["premium_cpl"] = df["premium_usd_t"] * 100 / LB_PER_T
    df.index.name = "date"
    df.reset_index().to_csv(OUT, index=False, float_format="%.3f")
    print(f"Saved {len(df)} months ({df.index.min():%Y-%m} to {df.index.max():%Y-%m}), "
          f"{(df['source'] == 'reconstructed').sum()} reconstructed -> {OUT}")
    print(df.loc["2025-07":, ["lme_cash", "dp", "dup_observed", "dup_low", "dup_mid", "dup_high"]].round(0).to_string())


if __name__ == "__main__":
    main()
