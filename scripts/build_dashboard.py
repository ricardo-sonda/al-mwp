"""Build dashboard/index.html: recomputes the series behind the README findings and injects them into
dashboard/template.html as JSON. Calculations follow notebook.ipynb (same freight, tariff steps and windows).

Run from the repo root:  python scripts/build_dashboard.py
Output is a standalone page (GitHub Pages: <user>.github.io/al-mwp/dashboard/).
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

# ---------------------------------------------------------------- inputs (as in the notebook)
lme = pd.read_csv(DATA / "lme_aluminium.csv", parse_dates=["date"])
mwp_m = pd.read_csv(DATA / "midwest_premium.csv", parse_dates=["date"])
fut = pd.read_csv(DATA / "midwest_premium_curve.csv", parse_dates=["date"])
dp = pd.read_csv(DATA / "europe_duty_paid_premium.csv", parse_dates=["date"])
dup_r = pd.read_csv(DATA / "europe_duty_unpaid_premium_reconstructed.csv", parse_dates=["date"]).set_index("date")
imports = pd.read_csv(DATA / "us_imports_by_country.csv", parse_dates=["date"])
ca = pd.read_csv(DATA / "canada_exports_by_country.csv", parse_dates=["date"])

FREIGHT = {"rtm_mw": (100, 150, 200), "ca_rtm": (30, 50, 80), "ca_mw": (30, 50, 80)}
LO, MID, HI = 0, 1, 2
TARIFF_STEPS = {
    "Canada": [("2019-05-20", 0.00), ("2025-03-12", 0.25), ("2025-06-04", 0.50)],
    "Other": [("2018-03-23", 0.10), ("2025-03-12", 0.25), ("2025-06-04", 0.50)],
}


def tariff_rate(month_start, origin="Other"):
    days = pd.date_range(month_start, month_start + pd.offsets.MonthEnd(0), freq="D")
    steps = pd.Series({pd.Timestamp(d): r for d, r in TARIFF_STEPS[origin]})
    return steps.reindex(steps.index.union(days)).ffill().loc[days].mean()


def rate_on(day, origin):
    return max([rate for start, rate in TARIFF_STEPS[origin] if pd.Timestamp(start) <= day], default=0.0)


def hac_ols(y, X, lags):
    return sm.OLS(y, sm.add_constant(X), missing="drop").fit(cov_type="HAC", cov_kwds={"maxlags": lags})


def ym(idx):
    return [d.strftime("%Y-%m") for d in idx]


def rnd(s, n=0):
    return [None if pd.isna(v) else round(float(v), n) for v in s]


lme_m = lme.set_index("date")["cash"].resample("MS").mean().rename("lme")
dp_m = dp.set_index("date")["premium_usd_t"].rename("dp")
m01 = fut[fut["tenor"] == 1].set_index("date")["premium_usd_t"].resample("MS").last()
mwp_all = mwp_m.set_index("date")["premium_usd_t"].combine_first(m01).rename("mwp")

# ---------------------------------------------------------------- 1. price: Canada import parity
r = pd.concat([lme_m, dp_m, mwp_all, dup_r["premium_usd_t"].rename("dup")], axis=1).dropna()
r["t_ca"] = [tariff_rate(d, "Canada") for d in r.index]


def parity_ca(f_net, f_mw, lme_px=None, dp_=None, t=None):
    lme_px = r["lme"] if lme_px is None else lme_px
    dp_ = r["dp"] if dp_ is None else dp_
    t = r["t_ca"] if t is None else t
    p = dp_ - f_net
    return p + f_mw + t * (lme_px + p)       # landed − LME


r["par_mid"] = parity_ca(FREIGHT["ca_rtm"][MID], FREIGHT["ca_mw"][MID])
r["par_lo"] = parity_ca(FREIGHT["ca_rtm"][HI], FREIGHT["ca_mw"][LO])
r["par_hi"] = parity_ca(FREIGHT["ca_rtm"][LO], FREIGHT["ca_mw"][HI])
pr = r.loc["2023-01-01":]
price = {"months": ym(pr.index), "mwp": rnd(pr["mwp"]), "parity": rnd(pr["par_mid"]),
         "parity_lo": rnd(pr["par_lo"]), "parity_hi": rnd(pr["par_hi"]), "lme": rnd(pr["lme"])}


# ---------------------------------------------------------------- implied tariff rate (Canada route)
curve = fut.pivot(index="date", columns="tenor", values="premium_usd_t")
last_day = curve.groupby(curve.index.to_period("M")).tail(1)
me = pd.DataFrame({"m01": last_day[1].values, "m03": last_day[3].values, "trade_date": last_day.index},
                  index=last_day.index.to_period("M").to_timestamp())
me["slope"] = me["m03"] - me["m01"]
lme3m_me = lme.set_index("date")["three_month"].groupby(lambda d: d.to_period("M").to_timestamp()).last()

imp = r.join(me[["m03"]], how="inner").join(lme3m_me.rename("lme3m"), how="inner")
p_ca = imp["dp"] - FREIGHT["ca_rtm"][MID]
f_ca = FREIGHT["ca_mw"][MID]
imp["impl_actual"] = (imp["mwp"] - p_ca - f_ca) / (imp["lme"] + p_ca) * 100
imp["impl_fwd"] = (imp["m03"] - p_ca - f_ca) / (imp["lme3m"] + p_ca) * 100
imp["stat"] = [tariff_rate(d + pd.DateOffset(months=2), "Canada") * 100 for d in imp.index]
imp["stat_now"] = imp["t_ca"] * 100
it = imp.loc["2024-01-01":]
implied = {"months": ym(it.index), "actual": rnd(it["impl_actual"], 1), "forward": rnd(it["impl_fwd"], 1),
           "statutory": rnd(it["stat_now"], 1)}


def window_mean(s, a, b):
    return float(s.loc[a:b].mean())


implied_regimes = {
    "actual_25": window_mean(imp["impl_actual"], "2025-04-01", "2025-05-01"),
    "actual_50": window_mean(imp["impl_actual"], "2025-07-01", "2025-12-01"),
    "fwd_50": window_mean(imp["impl_fwd"], "2025-07-01", "2025-12-01"),
}

# ---------------------------------------------------------------- 2. futures: curve slope and forecast test
sl = me.loc["2024-01-01":]
slope = {"months": ym(sl.index), "slope": rnd(sl["slope"])}

HORMUZ = pd.Timestamp("2026-03-02")
month_end = curve.groupby(curve.index.to_period("M")).tail(1)
m03_moved = curve[3].diff().ne(0).rolling(5).max().astype(bool)
fc = pd.DataFrame({"trade_date": month_end.index, "m03": month_end[3].values,
                   "fresh": m03_moved.loc[month_end.index].values},
                  index=month_end.index.to_period("M").to_timestamp())
fc["target"] = fc.index + pd.DateOffset(months=2)
fc["now"] = mwp_all.reindex(fc.index).values
fc["realised"] = mwp_all.reindex(fc["target"]).values
f_net, f_mw = FREIGHT["ca_rtm"][MID], FREIGHT["ca_mw"][MID]
fc["t_ca"] = [rate_on(day, "Canada") for day in fc["trade_date"]]
fc["lme3m"] = lme3m_me.reindex(fc.index).values
fc["dp"] = dp_m.reindex(fc.index).values
fc["parity"] = (fc["dp"] - f_net) + f_mw + fc["t_ca"] * (fc["lme3m"] + fc["dp"] - f_net)
fc = fc.dropna(subset=["m03", "realised"])
fc["err_fut"] = fc["realised"] - fc["m03"]
fc["err_nochange"] = fc["realised"] - fc["now"]
fc["err_parity"] = fc["realised"] - fc["parity"]


def forecast_window(t):
    target = t + pd.DateOffset(months=2)
    if target <= pd.Timestamp("2025-01-01"):
        return "pre"
    if t >= pd.Timestamp("2025-06-01") and target < pd.Timestamp("2026-03-01"):
        return "t50"
    if t >= pd.Timestamp("2026-03-01"):
        return "hormuz"
    return "spans"


fc["window"] = [forecast_window(t) for t in fc.index]


def rmse(e):
    return float(np.sqrt((e.dropna() ** 2).mean()))


fstats = {}
for w, s in fc[fc["window"] != "spans"].groupby("window", sort=False):
    nw = hac_ols(s["err_fut"], pd.Series(np.zeros(len(s)), index=s.index), 1) if len(s) > 2 else None
    fstats[w] = {"n": len(s), "mean_err": float(s["err_fut"].mean()), "share_pos": float((s["err_fut"] > 0).mean()),
                 "rmse_fut": rmse(s["err_fut"]), "rmse_nochange": rmse(s["err_nochange"]),
                 "rmse_parity": rmse(s["err_parity"])}
# Newey–West t-stat on the mean error (regress on a constant only)
for w, s in fc[fc["window"] != "spans"].groupby("window", sort=False):
    fit = sm.OLS(s["err_fut"].values, np.ones(len(s))).fit(cov_type="HAC", cov_kwds={"maxlags": 1})
    fstats[w]["t_nw"] = float(fit.tvalues[0])

has_par = fc.dropna(subset=["parity"])
longs = has_par[has_par["parity"] > has_par["m03"]]
rule = {"signal": {"n": len(longs), "pnl": float(longs["err_fut"].mean()), "wins": int((longs["err_fut"] > 0).sum())},
        "always": {"n": len(has_par), "pnl": float(has_par["err_fut"].mean()),
                   "wins": int((has_par["err_fut"] > 0).sum())}}

pf = fc.loc["2024-01-01":]
forecast = {"months": ym(pf["target"]), "realised": rnd(pf["realised"]), "m03": rnd(pf["m03"]),
            "parity": rnd(pf["parity"]), "err": rnd(pf["err_fut"]), "window": pf["window"].tolist(),
            "fresh": [bool(v) for v in pf["fresh"]], "stats": fstats, "rule": rule}

# August 2026: Canada parity at 50% vs a Canada-only 25%, at Aug 26 levels (mid freight)
aug = r.loc["2026-08-01"]
par50 = float(parity_ca(f_net, f_mw, aug["lme"], aug["dp"], 0.50))
par25 = float(parity_ca(f_net, f_mw, aug["lme"], aug["dp"], 0.25))
aug26 = {"parity50": par50, "parity25": par25, "parity_drop": par50 - par25, "cme_drop": 270}

# ---------------------------------------------------------------- 3. risk: the tariff couples the premium to LME
# Monthly: slope of Δ premium on Δ LME cash (monthly averages) by regime, MW premium and Rotterdam DP (the control).
# Months whose change spans a tariff announcement or step are left out.
STEP_MONTHS = pd.to_datetime(["2025-02-01", "2025-03-01", "2025-04-01", "2025-06-01", "2025-07-01"])
dmo = pd.concat([lme_m, dp_m, mwp_all], axis=1).diff().drop(STEP_MONTHS)
dmo["t_ca"] = [tariff_rate(d, "Canada") for d in dmo.index]
risk_monthly = {}
for k, (a, b) in {"pre": ("2021-08-01", "2025-01-01"), "t50": ("2025-08-01", "2026-02-01"),
                  "hormuz": ("2026-03-01", "2026-08-01")}.items():
    s = dmo.loc[a:b]
    mw, eu = hac_ols(s["mwp"], s["lme"], 1), hac_ols(s["dp"], s["lme"], 1)
    risk_monthly[k] = {"months": len(s), "t": float(s["t_ca"].mean()),
                       "mw": float(mw.params["lme"]), "mw_se": float(mw.bse["lme"]),
                       "dp": float(eu.params["lme"]), "dp_se": float(eu.bse["lme"])}
BETA_PRE = risk_monthly["pre"]["mw"]
pool = dmo.loc["2021-08-01":"2026-08-01"].dropna()
X = pd.DataFrame({"lme": pool["lme"], "t_lme": pool["t_ca"] * pool["lme"]})
f1, f2 = hac_ols(pool["mwp"], X, 2), hac_ols(pool["mwp"], X.assign(dp=pool["dp"]), 2)
risk_pooled = {"months": len(pool), "c": float(f1.params["t_lme"]), "se": float(f1.bse["t_lme"]),
               "c_dp": float(f2.params["t_lme"]), "se_dp": float(f2.bse["t_lme"])}

# Futures: CME Oct-26 MW contract on LME 3M, 1 Jun – 30 Sep 2026, tariff-news days left out, over 1/5/10-day changes
cme = pd.read_csv(DATA / "midwest_premium_cme.csv", parse_dates=["date", "contract_month"])
oct26 = cme[cme["contract_month"] == "2026-10-01"].set_index("date")["premium_usd_t"]
l3m = lme.set_index("date")["three_month"]
px = pd.concat([oct26.rename("fut"), l3m.rename("lme3m")], axis=1, join="inner").loc["2026-06-01":"2026-09-30"]
POLICY_DAYS = pd.to_datetime(["2026-08-20", "2026-08-21", "2026-08-24"])
T_NOW = 0.5
cme_betas = []
for h in (1, 5, 10):
    ch = (px - px.shift(h)).dropna()
    hit = pd.Series(px.index.isin(POLICY_DAYS), index=px.index).rolling(h, min_periods=1).max().astype(bool)
    ch = ch[~hit.reindex(ch.index)]
    fit = hac_ols(ch["fut"], ch["lme3m"], h)
    cme_betas.append({"h": h, "n": len(ch), "beta": float(fit.params["lme3m"]), "se": float(fit.bse["lme3m"]),
                      "r2": float(fit.rsquared), "risk": float(ch["fut"].std()),
                      "risk_overlay": float((ch["fut"] - T_NOW * ch["lme3m"]).std())})
daily = px.diff().dropna()
policy = {"drop": float(daily.loc["2026-08-20", "fut"]), "rise": float(daily.loc["2026-08-24", "fut"]),
          "daily_sd": float(daily.drop(POLICY_DAYS, errors="ignore")["fut"].std())}
cme_path = {"dates": [d.strftime("%Y-%m-%d") for d in px.index], "fut": rnd(px["fut"] - px["fut"].iloc[0]),
            "half_lme": rnd(T_NOW * (px["lme3m"] - px["lme3m"].iloc[0]))}

# Pre-tariff futures baseline: the LME MW contract (the CME one barely traded), month-end to month-end changes in the
# contract 3 months after the start month, on LME 3M; start months Mar 2019 – Dec 2024
by_contract = (fut.assign(contract_month=pd.to_datetime(fut["contract_month"]))
               .pivot_table(index="date", columns="contract_month", values="premium_usd_t"))
month_ends = by_contract.index.to_series().groupby(by_contract.index.to_period("M")).last()
base = []
for p0, d0 in month_ends.loc[:"2024-12"].items():
    d1, cm = month_ends.get(p0 + 1), (p0 + 3).to_timestamp()
    if d1 is None or cm not in by_contract:
        continue
    base.append({"dfut": by_contract.loc[d1, cm] - by_contract.loc[d0, cm],
                 "dlme": l3m.loc[:d1].iloc[-1] - l3m.loc[:d0].iloc[-1]})
base = pd.DataFrame(base).dropna()
bf = hac_ols(base["dfut"], base["dlme"], 1)
risk = {"monthly": risk_monthly, "pooled": risk_pooled, "beta_pre": BETA_PRE, "t": T_NOW,
        "cme_betas": cme_betas, "cme_path": cme_path, "policy": policy,
        "fut_base": {"n": len(base), "beta": float(bf.params["dlme"]), "se": float(bf.bse["dlme"])}}

# ---------------------------------------------------------------- 4. flows
BASE = ("2024-03-01", "2025-02-01")
T50 = ("2025-07-01", "2026-03-01")
crude = (imports[imports["country"] != "Total"]
         .pivot_table(index="date", columns="country", values="crude_t", aggfunc="sum").fillna(0))
tot = imports[imports["country"] == "Total"].set_index("date")
NAMED = ["Canada", "United Arab Emirates", "India", "Argentina", "Bahrain"]
top = (crude.loc["2024-01-01":].drop(columns="Other").sum().sort_values(ascending=False).index[:6].tolist())
named = [c for c in top if c != "Canada"][:4]
fl = crude[["Canada"] + named].copy()
fl["Rest"] = tot["crude_t"] - fl.sum(axis=1)
fl = fl.loc["2024-01-01":] / 1e3
flows_origin = {"months": ym(fl.index), "series": {c: rnd(fl[c], 1) for c in fl.columns}}
origin_change = {}
for c in list(fl.columns):
    b, a = fl[c].loc[BASE[0]:BASE[1]].mean(), fl[c].loc[T50[0]:T50[1]].mean()
    origin_change[c] = {"base": float(b), "t50": float(a), "pct": float((a / b - 1) * 100)}
tc = fl.sum(axis=1)
origin_change["Total crude"] = {"base": float(tc.loc[BASE[0]:BASE[1]].mean()), "t50": float(tc.loc[T50[0]:T50[1]].mean())}
origin_change["Total crude"]["pct"] = (origin_change["Total crude"]["t50"] / origin_change["Total crude"]["base"] - 1) * 100
canada_share = {"base": float(fl["Canada"].loc[BASE[0]:BASE[1]].mean() / tc.loc[BASE[0]:BASE[1]].mean() * 100),
                "t50": float(fl["Canada"].loc[T50[0]:T50[1]].mean() / tc.loc[T50[0]:T50[1]].mean() * 100)}

prod = tot[["crude_t", "semis_t", "scrap_t"]].loc["2024-01-01":] / 1e3
prod.columns = ["Crude", "Semis", "Scrap"]
q = prod.resample("QS").mean()
q = q[prod.resample("QS").size() == 3]          # full quarters only
products = {"quarters": [f"Q{d.quarter} {d.year}" for d in q.index],
            "series": {c: rnd(q[c], 1) for c in q.columns}}
pb = prod.loc[BASE[0]:BASE[1]].mean()
q2 = prod.loc["2026-04-01":"2026-06-01"].mean()
product_change = {c: {"base": float(pb[c]), "q2_26": float(q2[c]), "pct": float((q2[c] / pb[c] - 1) * 100)}
                  for c in prod.columns}
product_change["crude_share"] = {"base": float(pb["Crude"] / pb.sum() * 100), "q2_26": float(q2["Crude"] / q2.sum() * 100)}
product_change["total"] = {"base": float(pb.sum()), "q2_26": float(q2.sum())}

c7 = ca[ca["hs"] == 7601]
ex = c7[c7["country"] != "World"].pivot_table(index="date", columns="country", values="tonnes", aggfunc="sum").fillna(0)
world = c7[c7["country"] == "World"].set_index("date")["tonnes"]
exm = pd.DataFrame({"USA": ex["USA"], "Netherlands": ex["Netherlands"]})
exm["Other"] = world - exm.sum(axis=1)
exm = exm.loc["2024-01-01":] / 1e3
canada_exports = {"months": ym(exm.index), "series": {c: rnd(exm[c], 1) for c in exm.columns}}
us_share = ex["USA"] / world * 100
canada_x_change = {"us_share_base": float(ex["USA"].loc[BASE[0]:BASE[1]].sum() / world.loc[BASE[0]:BASE[1]].sum() * 100),
                   "us_share_t50": float(ex["USA"].loc[T50[0]:T50[1]].sum() / world.loc[T50[0]:T50[1]].sum() * 100),
                   "nl_base": float(ex["Netherlands"].loc[BASE[0]:BASE[1]].mean() / 1e3),
                   "nl_t50": float(ex["Netherlands"].loc[T50[0]:T50[1]].mean() / 1e3)}

out = {"price": price,
       "implied": implied, "implied_regimes": implied_regimes, "slope": slope, "forecast": forecast,
       "aug26": aug26, "risk": risk,
       "flows_origin": flows_origin, "origin_change": origin_change, "canada_share": canada_share,
       "products": products, "product_change": product_change,
       "canada_exports": canada_exports, "canada_x_change": canada_x_change,
       "data_through": {"premium": mwp_all.index.max().strftime("%Y-%m"), "imports": tot.index.max().strftime("%Y-%m"),
                        "canada": world.index.max().strftime("%Y-%m")}}

if __name__ == "__main__":
    summary = {k: out[k] for k in ["implied_regimes", "aug26", "origin_change",
                                   "canada_share", "product_change", "canada_x_change", "data_through"]}
    summary["fstats"] = fstats
    summary["rule"] = rule
    summary["risk"] = {k: v for k, v in risk.items() if k != "cme_path"}
    print(json.dumps(summary, indent=1, default=float))
    tpl = ROOT / "dashboard" / "template.html"
    if tpl.exists():
        page = tpl.read_text(encoding="utf-8").replace("__DATA__", json.dumps(out, separators=(",", ":")))
        # The template is a fragment (head tags, then the body from <div class="wrap">). Wrap it in a full document
        # for GitHub Pages; `--fragment PATH` also writes the bare fragment, which is what the claude.ai artifact takes.
        head, body = page.split('<div class="wrap">', 1)
        doc = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
               '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
               f'{head.strip()}\n</head>\n<body>\n<div class="wrap">{body}</body>\n</html>\n')
        (ROOT / "dashboard" / "index.html").write_text(doc, encoding="utf-8")
        print("wrote dashboard/index.html")
        if "--fragment" in sys.argv:
            frag = Path(sys.argv[sys.argv.index("--fragment") + 1])
            frag.write_text(page, encoding="utf-8")
            print(f"wrote {frag}")
