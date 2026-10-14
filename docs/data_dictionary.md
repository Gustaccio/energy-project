# Data dictionary

One row per column of the hourly dataset built by `build_hourly_dataset()`.
All timestamps are in Europe/Brussels. D is the delivery day and D-1 the day before.

The last column applies the rule of the project: at 11:59 on D-1, just before the day-ahead gate closure,
is the value known, in this version?

| Column | Unit | Source | Native time step | Publication | Known at 11:59 on D-1? |
|---|---|---|---|---|---|
| da_price_eur_mwh | EUR/MWh | ENTSO-E, day-ahead prices (BE) | 60 min until 2025-09-30, 15 min from 2025-10-01 | About 12:45 on D-1, after the SDAC auction (gate closure 12:00) | Yes up to D-1. The price of D is the target and does not exist at 11:59. |
| load_fc_mw | MW | ENTSO-E, total load day-ahead forecast (BE) | 15 min | 10:00 on D-1 at the latest (2 h before gate closure); updated if it changes by 10 % or more | Yes in principle. A late update is possible, and only the latest version is downloaded. |
| solar_fc_mw | MW | ENTSO-E, wind and solar day-ahead forecast (BE) | 60 min | 18:00 on D-1 at the latest; at least one update at 08:00 on D | Not guaranteed. The 18:00 deadline is after the 12:00 gate closure: treat it as a possible leak until checked. |
| wind_onshore_fc_mw | MW | ENTSO-E, wind and solar day-ahead forecast (BE) | 60 min | 18:00 on D-1 at the latest; at least one update at 08:00 on D | Not guaranteed. The 18:00 deadline is after the 12:00 gate closure: treat it as a possible leak until checked. |
| wind_offshore_fc_mw | MW | ENTSO-E, wind and solar day-ahead forecast (BE) | 60 min | 18:00 on D-1 at the latest; at least one update at 08:00 on D | Not guaranteed. The 18:00 deadline is after the 12:00 gate closure: treat it as a possible leak until checked. |
| load_actual_mw | MW | ENTSO-E, actual total load (BE) | 15 min | After real time: the last hours are missing at download time | No for D and for the end of D-1. Safe only for D-2 and before. |

- An hourly value is the mean of the native steps in that hour. An incomplete hour is NaN.
- Publication times are regulatory deadlines, not measured times: entsoe-py does not read the creation time or the revision number of the documents.
- Raw files: `data/raw/BE/<series>/YYYY-MM.parquet`, not versioned.

## Elia imbalance prices (dataset ods134)

Raw file: `data/raw/BE/imbalance/`, exported by hand, quarter-hourly since 2024-05-22, not versioned.
Not known at 11:59 on D-1 and validated only weeks later: used for the backtest at step 10, never as a forecasting feature.

| Column | Unit | Meaning |
|---|---|---|
| datetime | - | Start of the quarter-hour. Check the time zone with `df.dtypes`. |
| resolutioncode | - | Not defined on Elia's page. Check the values with `df['resolutioncode'].unique()`. |
| qualitystatus | - | Validation status of the row: Validated, NotValidated or DataIssue. Only validated prices are used for invoicing. |
| ace | MW | Area Control Error of the Belgian control area. |
| systemimbalance | MW | System imbalance, SI = ACE - NRV, per quarter-hour. |
| alpha | €/MWh | Additional incentive added to the regulation costs when the system imbalance is large. |
| alpha_prime | €/MWh | Not defined on Elia's page. To find in the dataset description. |
| marginalincrementalprice | €/MWh | Highest price paid by Elia for upward regulation in the quarter-hour. |
| marginaldecrementalprice | €/MWh | Lowest price received by Elia for downward regulation in the quarter-hour. |
| imbalanceprice | €/MWh | Imbalance price of the quarter-hour. Indicative until validated. |
