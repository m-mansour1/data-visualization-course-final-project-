# Tableau Dashboard Spec

This project does not yet include a hand-authored Tableau workbook (`.twb`), so this folder provides the next best production-ready package:

- cleaned Tableau-friendly CSV extracts
- event-marker data for annotations
- a packaging script to turn your Tableau workbook into a `.twbx`
- a screen-by-screen workbook blueprint that follows the proposal

## Data Files

- `tableau/data/proposal_dashboard_wide.csv`
  Use for most Tableau sheets and dashboards.
- `tableau/data/proposal_dashboard_long.csv`
  Use when a long-format indicator view is more convenient.
- `tableau/data/lebanon_event_markers.csv`
  Use for annotation reference lines, shapes, or tooltips.

## Recommended Tableau Data Model

Connect `proposal_dashboard_wide.csv` as the primary source.

Optionally connect `lebanon_event_markers.csv` as a secondary source on:

- `Country Code`
- `Year`

Use `proposal_dashboard_long.csv` only if you want a normalized long-format sheet for flexible indicator switching.

## Calculated Fields

These fields are already materialized in the wide CSV, but it is still useful to recreate them in Tableau so the workbook is self-documenting.

### `Arab Group`

```tableau
IF [Country Code] IN ("LBN", "JOR", "EGY", "TUN", "MAR", "DZA") THEN "Arab"
ELSE "Non-Arab"
END
```

### `Lebanon Highlight`

```tableau
IF [Country Code] = "LBN" THEN "Lebanon" ELSE "Comparator" END
```

### `Post-2019`

```tableau
IF [Year] >= 2019 THEN "Post-2019" ELSE "Pre-2019" END
```

### `Employed FLFPR`

```tableau
[Female Labor Force Participation Rate] * (1 - [Female Unemployment Rate] / 100)
```

### `Unemployed FLFPR Component`

```tableau
[Female Labor Force Participation Rate] - [Employed FLFPR]
```

### `GDP per Capita (sqrt)`

```tableau
SQRT(MAX(0, [GDP per Capita]))
```

## Screen 1: Lebanon Trends

Purpose: show fertility, female labor participation, and girls' tertiary enrollment in Lebanon from 1990 to 2024 with economic-shock markers.

Recommended worksheets:

1. `Lebanon Trend Dual Axis`
2. `Lebanon Event Labels`

Build:

- Filter `Country Code` to `LBN`.
- Put `Year` on Columns as continuous.
- Put `Total Fertility Rate` on Rows.
- Put `Female Labor Force Participation Rate` on Rows and make it dual-axis.
- Synchronize axes only if you intentionally want relative movement emphasized; otherwise keep separate visible axes.
- Add `Girls’ Tertiary Enrollment` as a third line using Measure Values, or place it in a second aligned worksheet if the dual-axis becomes crowded.
- Add event markers for `2019` and `2020`.

Design guidance:

- Lebanon should use a saturated accent color.
- Fertility should remain visually distinct from labor/education metrics.
- Show annotations for the 2019 financial collapse and COVID-19.

## Screen 2: Paradox Scatter

Purpose: compare fertility, labor participation, education, and GDP context across countries.

Recommended worksheets:

1. `TFR vs FLFPR Bubble`
2. `Education vs FLFPR Paradox`

Build for `TFR vs FLFPR Bubble`:

- Columns: `Total Fertility Rate`
- Rows: `Female Labor Force Participation Rate`
- Size: `GDP per Capita (sqrt)`
- Color: `Arab Group`
- Detail or Label: `Country Name`
- Pages or filter: `Year`

Build for `Education vs FLFPR Paradox`:

- Columns: `Girls’ Tertiary Enrollment`
- Rows: `Female Labor Force Participation Rate`
- Color: `Lebanon Highlight` or `Arab Group`
- Detail: `Country Name`
- Filter: `Year`

Design guidance:

- Use label-on-hover for all countries.
- Keep Lebanon always labeled or halo-highlighted.
- Add a year slider and default it to the most recent year available.

## Screen 3: Lebanon FLFPR Decomposition

Purpose: show how female labor force participation splits into employed and unemployed components over time.

Recommended worksheet:

1. `Lebanon FLFPR Decomposition`

Build:

- Filter `Country Code` to `LBN`.
- Columns: `Year`
- Rows: `Measure Values`
- Use only:
  - `Employed FLFPR`
  - `Unemployed FLFPR Component`
- Marks: Area
- Stack Marks: On

Design guidance:

- Use two tones from the same family so the decomposition reads as one concept.
- Add tooltips that show the raw unemployment rate alongside each stacked component.

## Screen 4: Country Comparison Map

Purpose: compare countries spatially with dynamic indicator selection.

Recommended worksheets:

1. `Country Indicator Map`
2. `Country KPI Tooltip`

Build:

- Generated latitude/longitude from `Country Name`
- Color: selected indicator
- Optional size: `GDP per Capita (sqrt)` if bubble map is clearer than filled map
- Filters:
  - `Year`
  - `Arab Group`
- Optional parameter: indicator selector for
  - `Total Fertility Rate`
  - `Female Labor Force Participation Rate`
  - `Female Unemployment Rate`
  - `Girls’ Tertiary Enrollment`
  - `GDP per Capita`

Because your country set is small, a symbol map is often clearer than a choropleth. If Tableau’s filled map feels visually sparse for 11 countries, prefer circles with rich tooltips.

## Dashboard Layout

Use four dashboards or one dashboard with four navigation buttons. Suggested names:

- `1. Lebanon Trends`
- `2. Paradox Scatter`
- `3. Labor Decomposition`
- `4. Country Map`

Suggested global filters:

- `Year`
- `Arab Group`
- `Country Name`

Suggested actions:

- Filter action from scatter plots to the map
- Highlight action for Lebanon across all dashboards
- Navigation buttons between screens

## Packaging

Once you save a Tableau workbook such as `tableau/Fertility_Labor_Economy.twb`, package it with:

```bash
chmod +x tableau/build_twbx.sh
./tableau/build_twbx.sh tableau/Fertility_Labor_Economy.twb
```

That will create `tableau/Fertility_Labor_Economy.twbx` with the data files embedded.
