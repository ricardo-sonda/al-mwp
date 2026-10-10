#### Important dates: 
June 4 2025: raise tariffs from 25 to 50. The tariffs were based on weight not customs value.
April 2 2026: tariff overhaul; shift from weight based to full customs value based
June 1 2026: UK maintains 25% tariffs since june 2025 (smelted or casted in UK). Mexico trying to reduce tariffs.
August 22 2026: Talks of reducing tariffs to 25% for Canada broke down. US invoked section 338 and hitting Canada with 27.6 billion usd in tariffs for other goods. Canada goes dollar for dollar on US steel and aluminium, raising from 25 to 50. 
September 29 2026: US implements import ban on some canada goods.
October 2026: Layoffs, stoppages, and plant sell offs for cross border manufacturing lines for automotives. Escalating trade war.
Canada was exempt from tariffs from May 2019 until March 2025.

#### Clarifications:
LME = benchmark price
MAL3 = 3 month LME rolling futures
CME contracts = fixed-date futures (much less volume than LME)
LME + DUP = Market price of uncleared AL in Rotterdam
LME + DP = Market price of cleared AL in Rotterdam
LME + MW = Market price of metal delivered to consumser in MW

#### Overview of data on hand:
US AL monthly imports by country from aug 2021 to jun 2026
MW premium monthly from aug 2020 to jun 2026
MW premium daily futures curve from march 2019 to aug 2026
LME daily spot and 3 month futures from jan 2018 to today
LME daily stock levels
DUP daily from march 2019 to oct 2025
DP monthly from july 2021 to aug 2026 

#### Other
Midwest premium after June 2026 is the front-month futures settle at month-end, as your README describes, because the USGS monthly series stops at June 2026
Interesting to look at scrap an semi imports increase to make up for lower crude imports
Interesting to look at inventory changes in aluminium in the US and Canada over 2025-2026

next steps may be looking at basis risks, spreads, and hedging against exposure to these.

What's been done
Landed cost against the Midwest price. There are two versions. The first prices everything off Rotterdam DP. The second splits two routes: Canada uses DP minus the freight to Rotterdam, and Rotterdam uses DUP. Both include freight and DUP sensitivity bands and a pass-through β for each step.
US import flows by origin (crude) and by product (crude, semis, scrap), plus semis and scrap by origin.
Canadian HS 7601 exports by destination.
MW premium futures: the month-end M01/M03 slope, moves in fixed contracts around six events, and an implied tariff rate from import parity.
Takeaways
Pass-through is roughly complete, in levels. The implied tariff rate follows the statutory rate closely: about 25% in Apr–May 2025 and about 50% from Jul 2025 for both routes. The premium is mostly import parity at the statutory rate.
The market priced the 50% step in fast, and before it was effective. The Jul-25 contract was up 399 $/t five days after 4 June. Most of the move came from the 30 May announcement, not the effective date. At step 1 the market had already moved by 12 March (Feb-25 gap +511 for Canada).
Canada was the marginal tonne and it got redirected. US imports from Canada fell about 38% (224 → ~140 kt/month). Canadian exports to the Netherlands went from ~4 to ~43 kt/month, and the US share of Canadian exports fell from 94% to 71%. Total Canadian exports fell only about 38 kt/month, so most of the lost US volume found another home.
The US replaced only part of the lost crude. Crude imports were down about 25%. UAE and India picked up some of it. By Apr–Jun 2026, semis (+54 kt) and scrap (+50 kt) had more than offset the crude drop. Note that the cell-13 conclusion ("semis and scrap rose to make up") rests on the 2026 window. Over Jul 25–Mar 26 they were up only about 7 and 5 kt.
The curve was in backwardation through most of the 50% regime (M03 − M01 between −120 and −230 in Aug–Dec 2025, Feb 2026 and Aug 2026). The market kept pricing some relief that never came.
Problems with the current numbers
β is inflated toward 1 by construction. The code computes Δmw_physical / Δlanded, and LME sits in both. The README defines β as ΔMWP / ΔLanded. Using premium against parity premium (landed − LME) gives Canada 0.70 at step 1 (vs 0.56) and 1.00 at step 2. Rotterdam is 1.40 and 1.09. Step 2 holds up, but it should be computed the README's way.
The "Jul 25 on" window is 14 months long. It mixes the tariff effect with LME rising from about 2,400 to 3,600 and DP rising from 190 to 590. A Jul–Sep 2025 window gives β ≈ 0.94 for Canada.
The 50% regime gap average of +15 hides large swings. The Canada gap runs from −172 (Jun 25) to +256 (Feb 26) to −206 (Apr 26). The 2026 swings come mostly from DP jumping (361 → 596), not from the MW premium. In 2026 the European side moves the arbitrage as much as the US side does.
Cell 5 is superseded but still in the notebook, along with its "full pass-through, margin still negative" takeaway. The negative margin was an artefact of charging the EU duty. Cell 8 still says "Takeaway: to fill in".
The baseline isn't at parity. Before 2025 the Canada route sat 80–180 $/t above parity at a 0% tariff. Either freight is understated or the Canadian netback isn't really DP − freight. That baseline needs explaining before small post-tariff gaps can be read as arbitrage.
notes.md and the README disagree on the duty basis. notes.md says duty was by weight until April 2026. The README says customs value throughout for HTS 7601. If notes.md is right, the tariff formula is wrong for Jun 2025–Mar 2026.
Open questions
Who actually pays the tariff? I checked the Canadian FOB unit value to the US, which the README plans but the notebook doesn't do yet. It was about LME + 450–600 before the tariff and fell to about LME + 0–250 at 50%, before jumping in mid-2026. That suggests Canadian sellers absorbed part of the duty for a while. This is the central incidence question, and it's currently missing from the notebook. Caveats: unit values lag (contract pricing), the product mix differs (value-added billet to the US vs P1020 to Europe), and Netherlands unit values sit oddly below LME.
Why does Canada still send about 140 kt/month to the US when the margin was negative in some months? Likely term contracts, value-added products, logistics lock-in, or customers with no alternative. Those flows don't follow spot arbitrage.
Where did the US shortfall come from? Total imports recovered by 2026 (~484 kt) but crude didn't. Without US stocks or production data, it's an open question whether consumption fell, inventories were drawn down, or domestic restarts covered it. Global LME stocks fell from about 560 kt (Oct 25) to 240 kt, which fits a tight market, but they say nothing US-specific.
What did the Aug 2026 Canada episode do to the curve? The data ends on 28 Aug, so the event table has NaN for +5 and +20 days. Only the month-end slope (−192) is available.
Worth exploring
Recompute β on premiums (MWP vs parity premium), with short windows and the time to close the gap. The README asks for that time and the notebook doesn't report it yet.
Add Canadian unit values by destination as a chart. It's the cleanest evidence on who absorbs the duty.
Decompose the gap's month-to-month changes into ΔMWP, ΔDP/DUP, ΔLME × t and the tariff. This shows what drove the 2026 swings.
Set the gap sign against the flows. The README promises this and it's the core of the arbitrage summary. For example, the Canada gap was negative in Jun 25 and Apr–May 26; did US-bound volume drop in the following one to two months?
Check whether an implied ~8–10 $/t per point of tariff explains the sustained backwardation, or whether the curve is just stale (M02+ unchanged on 80% of days).
Pin down the freight assumptions with a cited source. The baseline gap is the same size as the freight band.
I'd do #1 and #2 first. #1 fixes a headline number, and #2 answers the question the memo will be judged on.


project is mainly two things:
Import export changes - global metal flows 
Whether tariffs are priced in futures and optimal hedging

Insight onto tariff change:
Previously shocks to LME are independent of shocks to MWP. However, becuase of tariffs, MWP has delta with LME equal to tariff rate. Thus, shocks to LME are now correlated to shocks to MWP, and MWP has gained direct exposure to LME. 
Built an import-parity model of US aluminium landed costs from LME, USGS, UN Comtrade and futures data; the Midwest premium fully priced in the 50% tariff.
