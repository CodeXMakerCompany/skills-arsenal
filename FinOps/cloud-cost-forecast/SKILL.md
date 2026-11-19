---
name: cloud-cost-forecast
description: Explain a cloud bill and forecast where it is going across AWS, Azure, GCP and Oracle: allocate spend to services and teams, separate the drivers from the noise, and rank the actions by what they actually save. Use for /cloud-cost-forecast, "why did the bill go up", "forecast our spend", "por qué subió la factura", or before a commitment, a reserved instance, or a budget conversation.
---

# Cloud cost forecast

Two different jobs, and conflating them produces a report nobody acts on:

- **Explain the past.** The bill moved. What moved it?
- **Forecast the future.** At this trajectory and this roadmap, what does it cost in three months?

Do them in that order. A forecast built on an unexplained bill forecasts the mystery.

---

## 1. Get the bill into one shape

Pull the detailed cost export per provider, not the console summary: AWS Cost and Usage Report, Azure cost details, GCP billing export, Oracle usage reports. Normalize to one table with the same columns: date, provider, account or subscription, service, resource, usage type, quantity, cost, and whatever tags exist.

**Then measure your allocation coverage before anything else.** The share of spend you cannot attribute to a team, a product, or an environment is the first finding, and it caps how useful everything downstream can be. Below about 80% coverage, fixing the tagging is the recommendation, because every other number is a guess with decimals.

Normalize for the honest comparisons: amortize commitments rather than counting them on the purchase date, separate credits and discounts from list usage, and compare equal day counts. A February that looks 10% cheaper than January is three fewer days.

## 2. Explain the move

Decompose the delta between two periods into four causes, in this order:

1. **Price.** A rate change, a committed discount starting or expiring, a currency effect, a region difference.
2. **Quantity.** More requests, more storage, more data scanned, more hours running.
3. **Mix.** The same work on different resources: a bigger instance class, a different storage tier, a managed service replacing a self-run one.
4. **Waste.** Spend with no corresponding work: idle compute, unattached volumes, orphaned load balancers and addresses, snapshots nobody restores, a dev environment running all weekend, logs retained for years, cross-AZ traffic that should never have crossed, a NAT gateway carrying traffic that should use an endpoint.

**Name the top three line items and the top three movers.** Both lists, because the largest line is usually known and boring while the fastest mover is the actual story. A bill is almost always Pareto: a handful of resources carry most of it.

## 3. Forecast

- **Start from a trend, not a multiplication.** Take at least three months of daily spend per major service, strip the one-offs, and extrapolate the per-service trend. Extrapolating a single month, or a month with a migration in it, forecasts the migration.
- **Add the roadmap explicitly.** Each planned launch comes in as its own line, from its **cost-per-request** number times its expected traffic. This is where the discipline pays off: a design that was priced at design time is a forecast line, and one that was not is a surprise.
- **Give a range, not a point.** Low, expected, high, with the assumption that separates them stated. A single number will be quoted back to you in a budget meeting as a commitment.
- **Name what breaks the forecast.** The traffic assumption, a retention change, a migration, a commitment expiring, a model price change, one feature that scales per user instead of per account.

## 4. Rank the actions

Each candidate action gets four things: the monthly saving, the effort, the risk, and whether it is reversible. Then order them by saving over effort, and say which ones you would not do.

- **Free and reversible first:** delete the orphans, fix the retention, right-size what is measurably idle, schedule the non-production environments off outside work hours, move the cross-AZ or egress traffic onto an endpoint.
- **Then structural:** a storage tier, a cheaper service for the same work, caching, a batch window, an architecture change.
- **Commitments last**, and only against demand you can defend for the whole term. A reserved instance or savings plan on workload that is about to be re-architected is a one-year bet against your own roadmap. Say the break-even and the utilization you need to beat on-demand.

## 5. Report

- **The bill**, by service and by team, with the allocation coverage stated.
- **The delta**, decomposed into price, quantity, mix, and waste, with the top three movers.
- **The forecast**, low to high, with the assumption that separates them and the roadmap lines included.
- **The ranked actions**, with saving, effort, risk, and reversibility.
- **The guardrail**, because a forecast without one just documents the surprise: the budget alarm, its threshold, who it pages, and the anomaly detector on the services that move fastest.

Every number carries its source and its date. A cost report with no date on its data gets quoted for a year.
