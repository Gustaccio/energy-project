## 2026-09-12 · Data source
Context: the SDAC price is published on ENTSO-E; Elia publishes a non-binding reference price and, at quarter-hour resolution, load and generation forecasts.
Decision: prices, forecasts and load via ENTSO-E (entsoe-py); imbalance prices via Elia (ods134).
Consequence: a single library for the base series. Elia forecasts remain a lead for step 5, if they pass the "known at 11:59 the day before?" test.

## 2026-09-12 · Data period
Context: The year 2022 was unusual due to the gas crisis. Only data from 2023 onwards will be used.
Decision : Data used as from 2023-01-01.
Consequence: Data available only as from 2023-01-01.

## 2026-09-14 · Time step for the forecast
Context: day-ahead has been quarter-hourly since 1 October 2025, hourly before.
Decision: model at hourly resolution (mean of the quarter-hours) over 2023-2026.
Consequence: the shape within the hour is lost. To revisit at step 10.