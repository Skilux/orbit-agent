# Discover the Opportunity (Loop Step 2)

**Tool:** `mcp__loomi-mcp__execute_analytics_eql`
**When:** the human gives a loose goal ("find a revenue opportunity"). The agent discovers the cohort worth chasing — **no human picks the segment.**
**Rate limit:** space ~12–14s, budget ~5–8 calls. Discover on aggregates only (PII is masked).

All queries below were **run live 2026-05-31** on `abe73626-5469-11f1-8a97-6e3fd3d5a22f` and returned the numbers shown. Use them verbatim.

## 1. Size the lapsed one-time-buyer cohort
```
select count customers matching (count event purchase = 1 and count event purchase in last 30 days = 0) by customer.country
```
→ Germany **2,555** · UK **6,060** · USA **7,276** = **15,891** lapsed one-time buyers.
This is the headline cohort: bought exactly once, ever, and nothing in the last 30 days.

## 2. Category split (what they bought)
`purchase` has **no category** property — categories live on the `purchase_item` event (`category_level_1` = Apparel/Jewelery only; the useful split is `category_level_2`).
```
select count event purchase_item by event purchase_item.category_level_2 grouping top 10 customers matching (count event purchase = 1 and count event purchase in last 30 days = 0)
```
→ women **10,320** · men **4,820** · shoes **631** · jewelery **343** (item counts; one order spans several items, so this sums above the customer count).

## 3. Repeat rate (why this cohort matters)
Repeat buyers (≥2 purchases) vs all buyers (≥1) — two calls:
```
select count customers matching (count event purchase >= 2) by customer.country
```
→ DE 401 · UK 818 · USA 1,009 = **2,228**
```
select count customers matching (count event purchase >= 1) by customer.country
```
→ DE 3,058 · UK 7,107 · USA 8,592 = **18,757**
Repeat rate = 2,228 / 18,757 = **~12%**. So ~88% of buyers never come back — the win-back upside.

## 4. AOV (sizing the $ opportunity)
```
select average event purchase.total_price by customer.country customers matching (count event purchase = 1 and count event purchase in last 30 days = 0)
```
→ DE **$1,002** · UK **$1,062** · USA **$965** ≈ **~$1,000 AOV**.

## The narratable headline
> ~15,891 customers bought once (~$1,000 each) and vanished; only ~12% of buyers ever repeat. Win back even a slice → real revenue.

## Gotcha
Breaking customers down by an *event* property (`by event purchase.category`) returns **empty rows** — and `purchase` has no category anyway. Break customers by **customer** properties; break **events** (`count event purchase_item`) by event properties. Don't pitch "ML churn score" — the sandbox has 0 prediction models; use the RFM proxy (see `author-offer-rfm.md`).
