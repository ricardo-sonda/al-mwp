# Has the US Midwest premium priced in the Section 232 tariff?

## The question

> **To what extent has the US Midwest aluminium price absorbed the cost of the Section 232 tariffs, and what explains the part that has not been passed through?**

Two strands, kept deliberately simple: careful landed-cost arithmetic and physical trade flows. There is no econometric modelling.

1. **Price: pass-through.** Compare the physical Midwest price (LME + MW premium) with the *landed cost* of importing a tonne. The landed cost is LME + origin premium + freight + tariff. The gap between the two is the import margin. A gap near zero means full pass-through. A persistent gap means the market is coping some other way: running down inventory, substituting domestic or scrap units, or expecting the tariff to be reversed.
2. **Volume: flows.** How did US primary imports by origin (Canada against everyone else) change around each tariff step? Did an arbitrage window open (margin > 0, so imports should rise) or close (margin < 0, so imports should fall), and did the flows respond?

The project ends with a short summary of when import arbitrage was open or shut, and why.

## Why this matters to MST

The job ad names "trade tariff implications for global metal flows" as a core theme. MST places Hydro's standard ingot wherever it nets back the most. The landed-cost gap is that netback comparison: it tells you whether a tonne earns more delivered to the Midwest or left in Rotterdam.

## The tariff timeline (the whole project hinges on this)

Every date and rate below must be checked against the proclamation or Federal Register text before it is used. The rate depends on the **origin**, not only on the date.

| Effective | Change | Rate on Canada | Rate on others |
|---|---|---|---|
| 23 Mar 2018 | Section 232 introduced | exempt, then 10% from 1 Jun 2018 | 10% |
| 20 May 2019 | Canada and Mexico exempted | 0% | 10% |
| 16 Aug – 15 Sep 2020 | 10% briefly reimposed on Canadian non-alloyed unwrought metal | 10% (part) | 10% |
| 12 Mar 2025 | All exemptions end; rate raised | 25% | 25% |
| 4 Jun 2025 | Rate doubled (UK kept at 25%) | 50% | 50% (UK 25%) |
| 2 Apr 2026 | Customs-value overhaul for derivatives; no change for unwrought aluminium | 50% | 50% |
| Aug 2026 | Reported deal to cut Canada to 25%; talks collapse | 50% | 50% |

Two consequences for the model:

- **Canada paid 0% for most of 2019–2025, while other origins paid 10%.** The first event that hit the marginal (Canadian) tonne was 12 March 2025, not June 2025, so both steps need their own pass-through number.
- **Duty basis.** For primary metal (HTS 7601) the duty has always been ad valorem on customs value. Customs value is roughly the FOB price, LME + origin premium, and excludes international freight. The 2 April 2026 overhaul changed how derivatives are valued and does not affect the product analysed here, so it is not treated as an event.

## Method

**Landed cost by route (USD/t, monthly):**

```
FOB(origin, m)    = LME(m) + P_origin(m)                     # what the tonne is worth where it sits
Landed(origin, m) = FOB(origin, m) + Freight_origin→MW + t_origin(m) × FOB(origin, m)
Gap(origin, m)    = (LME(m) + MWP(m)) − Landed(origin, m)
```

`P_origin` is the premium the tonne gives up by going to the US instead of its best alternative. That alternative differs by route, so the two routes use different European premiums:

- **Rotterdam → Midwest: `P_origin` = DUP.** This is the world-market tonne. Metal in Rotterdam bonded warehouses that is re-exported never clears EU customs, so it never pays the EU's 3% duty. Its opportunity cost is the duty-unpaid price, LME + DUP. Using DP here would charge the US route with an EU duty it never pays (about 3% × (LME + DUP), ≈ 70–90 $/t). Freight is transatlantic plus inland. Europe ships almost no primary metal to the US, so this route is a *would-it-pay* test rather than an observed flow.
- **Canada → Midwest: `P_origin` = DP − Freight_Canada→Rotterdam.** This is the marginal tonne, about 60–75% of US crude imports. Canadian aluminium enters the EU duty-free under CETA, so a Canadian tonne diverted to Europe can be cleared and sold at the *duty-paid* price without paying the duty. Its alternative is therefore LME + DP, *netted back* to Canada by subtracting transatlantic freight. Adding the full Rotterdam premium and then Canada→MW freight on top would price Canadian metal as if it were already in Rotterdam. Freight to the Midwest is short rail or truck haul.

Freight is an assumption with a sensitivity band, because no free series exists. All results are shown at low, mid and high freight. The Canada route has two freight legs: the netback leg (Canada → Rotterdam) and the delivery leg (Canada → Midwest).

**Tariff base.** US duty is charged on the customs value of the actual import, i.e. the transaction price excluding international freight. `FOB` above is a proxy for that value, not the invoice itself.

**Pass-through:** `β = ΔMWP / ΔLanded` for each tariff step (12 Mar 2025, 4 Jun 2025). It is measured on monthly data and on the daily front-month curve around each date. The report shows how long it takes the gap to close, not only the jump on the day.

**Explaining the gap** uses descriptive evidence only:
- **Expectations:** the shape of the MW premium futures curve. Backwardation means the market expects the premium to fall. Use the August 2026 Canada episode as the case study.
- **Inventory:** LME stock levels. These are global; there are no US-specific stocks.
- **Supply response:** import volumes by origin, i.e. whether the shortfall was met by other origins.

**Flows:** monthly and quarterly US crude imports by origin. Compare Canada's share and volume before and after each step, and set it against the sign of the gap in the same months. On the Canadian side, track where the tonnes that stopped going to the US went (Europe, Asia, or nowhere, i.e. into stock), and how Canada's FOB unit value by destination compares.

## Data on hand

| File | Series | Frequency | Coverage | Notes |
|---|---|---|---|---|
| `lme_aluminium.csv` | LME cash, 3M, stocks (westmetall.com) | Daily | Jan 2018 – Oct 2026 | Monthly means match the USGS LME cash column to within 0.5 $/t. |
| `midwest_premium.csv` | MW premium and all-in MW price (USGS, Platts monthly averages) | **Monthly** | Aug 2020 – Jun 2026 | Monthly averages, not daily spot. Premium = all-in MW − LME cash. |
| `midwest_premium_curve.csv` | LME MW premium futures (Platts), M01–M15 | Daily | Mar 2019 – Aug 2026 | Cash-settled on the monthly average of the Platts MW premium. M01 is the trade date's own calendar month, so it is part-fixed and converges to that month's average. M01 at month-end matches the USGS monthly premium within ~10 $/t (median; max 34), which justifies extending the monthly series to Aug 2026. **M01 is not a spot price**: within a month it lags the spot premium, and it switches contract on the first trading day of each month. Back months are illiquid or stale. |
| `europe_duty_unpaid_premium.csv` | Rotterdam DUP (investing.com continuous series) | Daily → monthly | Mar 2019 – **Oct 2025** | Ends before the most interesting period. Looks like a rolling front-month futures series rather than the Fastmarkets assessment itself (month-end roll spikes, ~70% unchanged days). Source definition not yet confirmed. |
| `europe_duty_paid_premium.csv` | Rotterdam DP (LME ED final settlement = monthly average of Fastmarkets assessment) | Monthly | Jul 2021 – Aug 2026 | |
| `europe_duty_unpaid_premium_reconstructed.csv` | Rotterdam DUP, observed and then reconstructed from DP | Monthly | Jul 2021 – Aug 2026 | `source` column marks reconstructed months; low/mid/high band. See below. |
| `us_imports_by_country.csv` | US imports by country: crude, semis, scrap (USGS) | Monthly | Aug 2021 – Jun 2026 | Contains `Total` and `Other` rows, so do not sum across countries. Two months are derived from year-to-date differences. |
| `canada_exports_by_country.csv` | Canadian exports by destination, HS 7601 (unwrought) and 7602 (scrap), tonnes and FOB USD (UN Comtrade, from StatCan) | Monthly | 7601: Jan 2018 – Jul 2026; 7602: to Oct 2024 so far | `country == "World"` is the total, so do not sum it with the rest. Comtrade drops the weight in about 9 months for the US and World rows. These are filled from value ÷ interpolated unit value (`qty_imputed`). Exports to the US match US-reported imports from Canada within about 3% in most quarters. |

### Gaps and how to handle them

- **DUP after Oct 2025: reconstructed.** Duty-paid metal carries the EU import duty (3% on unwrought aluminium, charged on LME + DUP), so `DUP = (DP − r·LME) / (1 + r)`. Here `r` is the *effective* duty rate. It is lower than 3% because part of the metal in Rotterdam comes from duty-free origins. Fitted on the overlap months, r has a median of 2.7% and a 10–90% range of 1.9–3.3%. The backtest error is about ±13 $/t. Feb–May 2025 is the exception: r collapsed to about 0% as metal turned away from the US flooded Europe, and the reconstruction overstates DUP by 50–80 $/t in those months. Plot reconstructed months as a dashed line and carry the band into the landed-cost sensitivity. DUP is needed only for the Rotterdam route; the Canada route uses DP, which is observed through Aug 2026.
- **Freight.** Fixed assumptions with a range, citing whatever public figures are available.
- **US-located inventory.** Not on hand. The global LME stock series is used, and the memo states this limitation.

## Out of scope

- Econometric models and forecasting the premium.
- Formal implied-probability extraction from the curve. The curve shape is used qualitatively.
- Derivatives and fabricated products.
- Events after the data ends (the Sep 2026 import ban and the Oct 2026 layoffs) are context only.

## Deliverables

- `notebook.ipynb`: tariff table, landed-cost model, gap chart, pass-through numbers and flow charts (Python/pandas).
- `memo.md`: one page with a landed cost against actual chart, a Canada-share chart, the two pass-through numbers, an arbitrage summary and a "so what for Hydro" paragraph.

## Plan (deadline 16 October 2026)

| Dates | Work |
|---|---|
| 6 Oct | Lock the tariff table from primary sources; extend DUP; set freight assumptions |
| 7–8 Oct | Landed-cost model and gap chart; pass-through for Mar 2025 and Jun 2025 |
| 9–10 Oct | Flow analysis: Canada against others, before and after, set against the gap sign |
| 11 Oct | Explaining the gap: curve shape (incl. Aug 2026), stocks, origin switching |
| 12–14 Oct | Memo; one line for the CV and cover letter |
| 15–16 Oct | Buffer; submit |

## Scripts

- `scripts/fetch_lme.py`: LME prices and stocks
- `scripts/fetch_usgs.py`: USGS Mineral Industry Surveys (MW premium, imports by country)
- `scripts/clean_lme_premiums.py`: LME MW premium curve and Rotterdam DP
- `scripts/clean_duty_unpaid.py`: Rotterdam DUP (investing.com export)
- `scripts/reconstruct_duty_unpaid.py`: extends DUP past Oct 2025 from DP (run after the two cleaning scripts)
- `scripts/fetch_canada_exports.py`: Canadian exports by destination from the UN Comtrade public API (no key needed; one month per call, cached in `data/raw/comtrade`)
