# Proposed Benchmark Metrics

These are the candidate metrics for the m/operations benchmark report. During Phase 2, the community will select ~10 metrics that enough contributors can provide data for.

## Selection Criteria

A metric makes the cut if:
1. **At least 5 contributors** can provide real data for it
2. **It can be anonymized** without losing comparability
3. **It measures something that breaks** — not vanity metrics
4. **It's comparable across organizations** with clear definitions

---

## Freight & Logistics

| # | Metric | Definition | Unit |
|---|--------|-----------|------|
| F1 | **Rate Accuracy** | % of loads where invoiced amount matches quoted amount within 5% | % |
| F2 | **Accessorial Surprise Rate** | % of loads with unquoted accessorial charges at invoice | % |
| F3 | **Average Accessorial Overage** | Mean $ amount of unquoted accessorials per affected load | USD |
| F4 | **Tender Acceptance Rate** | % of load tenders accepted by first carrier offered | % |
| F5 | **On-Time Delivery Rate** | % of loads delivered within agreed delivery window | % |
| F6 | **Average Dwell Time** | Mean time (hours) between truck arrival and load/unload completion | hours |
| F7 | **Claims Rate** | % of loads with damage or loss claims filed | % |

## Finance & Invoicing

| # | Metric | Definition | Unit |
|---|--------|-----------|------|
| I1 | **Invoice First-Pass Match Rate** | % of invoices matching PO/rate on first review (no manual intervention) | % |
| I2 | **Exception Rate** | % of invoices requiring manual review or dispute | % |
| I3 | **Average Days to Pay** | Mean days from invoice receipt to payment | days |
| I4 | **Reconciliation Time** | Average time to resolve an invoice discrepancy | hours |

## Warehouse & Fulfillment

| # | Metric | Definition | Unit |
|---|--------|-----------|------|
| W1 | **Order Accuracy** | % of orders picked/packed correctly on first attempt | % |
| W2 | **Inventory Accuracy** | Cycle count accuracy % | % |
| W3 | **Average Pick Time** | Mean time per order line from assignment to pack | minutes |

## Last Mile / Delivery

| # | Metric | Definition | Unit |
|---|--------|-----------|------|
| L1 | **First-Attempt Delivery Success** | % of deliveries completed on first attempt | % |
| L2 | **Failed Delivery Cost** | Average total cost of a failed delivery attempt (redelivery + customer service + opportunity) | USD |
| L3 | **Proactive Notification Rate** | % of deliveries where customer received status update before arrival | % |

## Operational Health

| # | Metric | Definition | Unit |
|---|--------|-----------|------|
| O1 | **Data Quality Effort** | Estimated % of operational time spent fixing data issues vs doing productive work | % |
| O2 | **System-of-Record Accuracy** | % of carrier/vendor/customer records that are current and correct | % |
| O3 | **Exception-to-Resolution Time** | Average time from exception detection to resolution | hours |

---

## How to Propose New Metrics

Open an issue with:
- Metric name and definition
- Why it matters (what decision does it inform?)
- How it can be measured consistently across contributors
- Whether it can be anonymized without losing value
