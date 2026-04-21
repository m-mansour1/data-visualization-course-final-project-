# Tableau Starter Assets

This folder contains the Tableau-ready assets derived from the project proposal and the cleaned panel data.

## What is included

- `data/proposal_dashboard_wide.csv`: wide table for most sheets
- `data/proposal_dashboard_long.csv`: long table for indicator-driven views
- `data/lebanon_event_markers.csv`: event markers for 2019 and 2020 annotations
- `dashboard_spec.md`: workbook blueprint mapped to the proposal
- `build_twbx.sh`: packages a `.twb` workbook plus the local data files into a `.twbx`

## Why there is no finished `.twbx` yet

Creating a polished Tableau workbook from scratch requires Tableau-authored workbook XML or direct in-app authoring. This repo did not include an existing `.twb`, so the safest reproducible path is:

1. Open Tableau Public.
2. Connect to `tableau/data/proposal_dashboard_wide.csv`.
3. Build the four proposal screens using `dashboard_spec.md`.
4. Save the workbook as `.twb` in this repo.
5. Run `./tableau/build_twbx.sh path/to/workbook.twb`.

## Suggested workbook name

`Fertility_Female_Labor_Economic_Conditions.twb`
