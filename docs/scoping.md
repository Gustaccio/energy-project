# Scoping

## Decision to improve
When a battery operator has to commit to the next day's charge and discharge schedule before the day-ahead auction closes at 12:00 CET, the schedule depends on a forecast of tomorrow's prices. A better forecast gives a better schedule and more revenue.

## Horizon and time resolution
- One forecast per day, made before 12:00 on day D, for the 24 hours of day D+1.
- Hourly resolution, zone BE, local time (Europe/Brussels). The 15-minute prices introduced on 1 October 2025 are averaged to hours.
- Rule against data leakage: an input is allowed only if it was known at 11:59 on day D.

## Reference asset
Illustrative assumptions, not a real installation.
- Power: 10 MW, same limit for charging and discharging
- Capacity: 20 MWh
- Round-trip efficiency: 88%
- State of charge: 50% at the start and at the end of each day

## Success metric
Share of the perfect-foresight revenue captured by the schedule built on the forecast, measured on the last three months of data, which are used only once, at the end. The forecast itself is checked with MAE (EUR/MWh) against a naive baseline: the same hour one week earlier.

## Out of scope
- Intraday and balancing markets (imbalance prices appear only in optional extensions)
- Ancillary services (FCR, aFRR, mFRR)
- Grid fees, taxes and network constraints
- Battery degradation