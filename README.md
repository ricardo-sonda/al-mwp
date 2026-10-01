# How much of the US aluminium tariff is the market pricing in?

## The question

> **How much of the 50% Section 232 tariff does the US Midwest premium price in, and what does the forward curve imply about the chance that the tariff on Canadian metal is cut?**

Three sub-questions, each with one output:

1. **Parity:** What Midwest premium would fully pass the tariff through, and how far has the actual premium been from that level since 2025?
   *Output: chart of the actual premium against tariff parity.*
2. **Pass-through:** When the tariff rose from 25% to 50% on 4 June 2025, what share of the increase in parity showed up in the premium?
   *Output: one pass-through ratio.*
3. **Expectations:** On 20 August 2026, reports that Canada's rate would fall to 25% sent the premium down about 8%. Talks collapsed on 21 August. What probability of a cut does the premium curve imply before the episode, during it and today?
   *Output: one probability per date.*

## Why this matters to MST

The job ad names "trade tariff implications for global metal flows" as a core market theme. MST's job is to place Hydro's standard ingot (from Norway, Qatalum and Albras) wherever it earns the most. So the practical form of this question is a netback question: at today's premium, does US-bound metal earn more than metal sold into Europe or Asia, and what tariff outcome would flip that? The parity model answers it. The gap between actual and parity is the arbitrage margin, and the probability tells you how long that margin is likely to last.

Canada is the focus because it supplies most US primary imports, so Canadian metal is the marginal tonne that sets the premium.

## Method

**Tariff parity.** The US levies duty on customs value, which is roughly the FOB transaction price (LME plus the origin premium, excluding freight):

```
Parity(t) = P_alt + Freight + t × (LME + P_alt)
```

- `P_alt` is the premium the metal could earn elsewhere, i.e. its opportunity cost. The first pass uses the Rotterdam duty-unpaid premium as the proxy.
- `t` is the tariff rate (0.25 or 0.50). A cut for Canada means putting t = 0.25 into the Canadian leg.

**Gap.** `Gap = MWP_actual − Parity(0.50)`. A negative gap means the market is not passing through the full tariff, because it expects a cut, has surplus domestic or inventory metal, or has weak demand. A positive gap means US tightness beyond the tariff.

**Pass-through (sub-question 2).** `β = ΔMWP / ΔParity` over a window around 4 June 2025, with care over the pre-announcement drift.

**Implied probability (sub-question 3).** Treat the premium futures price for maturity T as a mix of two outcomes and solve for p:

```
F(T) = p × Parity(0.25) + (1 − p) × Parity(0.50) + basis
p    = (Parity(0.50) + basis − F(T)) / (Parity(0.50) − Parity(0.25))
```

`basis` is the pre-event gap, held constant. Run this for the days before, during and after 20–21 August 2026. This is a rough reading of expectations, not a precise one, and the write-up should say so.

## Data (free sources first)

| Series | Source | Frequency |
|---|---|---|
| LME aluminium cash and 3M | westmetall.com (free history) | Daily |
| US Midwest premium (Platts) | USGS *Aluminum Mineral Industry Surveys* (monthly averages); news reports around event dates | Monthly, plus event points |
| Midwest premium futures curve | CME "Aluminum MW US Transaction Premium Platts" (AUP) settlements, LME equivalent | Daily snapshots |
| Rotterdam duty-unpaid premium | CME European Duty-Unpaid futures, news reports | Monthly |
| Transatlantic freight | Fixed assumption ($/t) with a sensitivity range | – |
| US imports by origin | USITC DataWeb, HTS 7601 | Monthly |

Daily spot Midwest premium history sits behind the Platts and Fastmarkets paywalls. Monthly data is enough for sub-questions 1 and 2. Sub-question 3 needs futures settlements for only a handful of dates.

## Out of scope

- Derivatives and fabricated products (the April and June 2026 changes to the customs-value rules for derivatives)
- Forecasting where the premium will go
- Every exporting country. The analysis covers Canada plus one non-Canadian origin (for example the Middle East) for contrast.

## Deliverables

- `notebook.ipynb`: data, parity model and the three outputs, in Python (pandas). The ad asks for Python.
- `memo.md`: a one-page write-up with two charts, three numbers and a "so what for Hydro" paragraph.

## Plan (application deadline: 16 October 2026)

| Dates | Work |
|---|---|
| 30 Sep – 4 Oct | Collect data: LME, monthly premium, Rotterdam premium, import volumes |
| 5 – 8 Oct | Build the parity model and the gap chart (sub-question 1); calculate pass-through (sub-question 2) |
| 9 – 11 Oct | Event study and implied probability (sub-question 3) |
| 12 – 14 Oct | Write the memo; add one line to the CV and cover letter |
| 15 Oct | Buffer; submit |

## Background facts (check before citing)

- Section 232 tariff on aluminium: 10% (2018), then 25% from 12 March 2025, then 50% from 4 June 2025.
- The premium hit a record of about $1.19/lb (≈ $2,620/t) in June 2026.
- On 20 August 2026 the September contract fell 8.2% to 95¢/lb on reports that Canada's rate would be cut to 25%. US–Canada talks collapsed on 21 August.
- Platts spot premium: $1.097/lb on 10 September 2026.
- The tariff stays at 50%, with Russia at 200% and the UK at a reduced 25%.
