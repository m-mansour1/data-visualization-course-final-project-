from pathlib import Path

import numpy as np
import pandas as pd


DATA_DIR = Path("data")
START_YEAR = 1990
END_YEAR = 2024

COUNTRY_NAME_MAP = {
    "ALB": "Albania",
    "ARM": "Armenia",
    "DZA": "Algeria",
    "EGY": "Egypt",
    "GEO": "Georgia",
    "IRN": "Iran",
    "JOR": "Jordan",
    "LBN": "Lebanon",
    "MAR": "Morocco",
    "TUN": "Tunisia",
    "TUR": "Turkey",
}

INDICATOR_LABEL_MAP = {
    "SP.DYN.TFRT.IN": "Total Fertility Rate",
    "SL.TLF.CACT.FE.ZS": "Female Labor Force Participation Rate",
    "SL.UEM.TOTL.FE.ZS": "Female Unemployment Rate",
    "SE.TER.ENRR.FE": "Girls’ Tertiary Enrollment",
    "NY.GDP.PCAP.CD": "GDP per Capita",
    "NY.GDP.MKTP.KD.ZG": "GDP Growth Rate",
}

FILE_NAME_MAP = {
    "API_SP.DYN.TFRT.IN_DS2_en_excel_v2_667.xls": "Total Fertility Rate (SP.DYN.TFRT.IN).xlsx",
    "API_SL.TLF.CACT.FE.ZS_DS2_en_excel_v2_2415.xls": "Female Labor Force Participation Rate (SL.TLF.CACT.FE.ZS).xlsx",
    "API_SL.UEM.TOTL.FE.ZS_DS2_en_excel_v2_473.xls": "Female Unemployment Rate (SL.UEM.TOTL.FE.ZS).xlsx",
    "API_SE.TER.ENRR.FE_DS2_en_excel_v2_810.xls": "Girls’ Tertiary Enrollment (SE.TER.ENRR.FE).xlsx",
    "API_NY.GDP.PCAP.CD_DS2_en_excel_v2_724.xls": "GDP per Capita (NY.GDP.PCAP.CD).xlsx",
    "API_NY.GDP.MKTP.KD.ZG_DS2_en_excel_v2_675.xls": "GDP Growth Rate (NY.GDP.MKTP.KD.ZG).xlsx",
}

MERGED_LONG_OUTPUT = DATA_DIR / "merged_panel_long.xlsx"
MERGED_WIDE_OUTPUT = DATA_DIR / "merged_panel_wide.xlsx"


def clean_excel_file(input_path: Path, output_path: Path) -> pd.DataFrame:
    df = pd.read_excel(input_path, sheet_name="Data", header=None)
    cleaned_df = df.iloc[3:].reset_index(drop=True)
    cleaned_df.columns = cleaned_df.iloc[0]
    cleaned_df = cleaned_df.iloc[1:].reset_index(drop=True)

    id_columns = [
        "Country Name",
        "Country Code",
        "Indicator Name",
        "Indicator Code",
    ]
    year_columns = [column for column in cleaned_df.columns if column not in id_columns]

    reshaped_df = cleaned_df.melt(
        id_vars=id_columns,
        value_vars=year_columns,
        var_name="Year",
        value_name="Value",
    )
    reshaped_df["Year"] = pd.to_numeric(reshaped_df["Year"], errors="coerce").astype("Int64")
    reshaped_df["Value"] = pd.to_numeric(reshaped_df["Value"], errors="coerce")
    reshaped_df.to_excel(output_path, index=False)

    return reshaped_df


def build_long_panel(cleaned_frames: list[pd.DataFrame]) -> pd.DataFrame:
    long_df = pd.concat(cleaned_frames, ignore_index=True)
    long_df = long_df[long_df["Country Code"].isin(COUNTRY_NAME_MAP)]
    long_df = long_df[long_df["Year"].between(START_YEAR, END_YEAR)]
    long_df["Country Name"] = long_df["Country Code"].map(COUNTRY_NAME_MAP)
    long_df["Indicator Label"] = long_df["Indicator Code"].map(INDICATOR_LABEL_MAP)
    long_df = long_df.sort_values(
        by=["Country Code", "Indicator Code", "Year"],
        kind="stable",
    ).reset_index(drop=True)

    long_df["Value"] = long_df.groupby(
        ["Country Code", "Indicator Code"],
        group_keys=False,
    )["Value"].transform(lambda series: series.interpolate(limit_direction="both"))

    return long_df


def build_wide_panel(long_df: pd.DataFrame) -> pd.DataFrame:
    wide_df = long_df.pivot_table(
        index=["Country Name", "Country Code", "Year"],
        columns="Indicator Label",
        values="Value",
        aggfunc="first",
    ).reset_index()
    wide_df.columns.name = None

    wide_df = wide_df.sort_values(
        by=["Country Code", "Year"],
        kind="stable",
    ).reset_index(drop=True)

    flfpr = wide_df["Female Labor Force Participation Rate"]
    female_unemployment = wide_df["Female Unemployment Rate"]
    gdp_per_capita = wide_df["GDP per Capita"]

    wide_df["Employed FLFPR"] = flfpr * (1 - (female_unemployment / 100))
    wide_df["GDP per Capita (sqrt)"] = np.sqrt(gdp_per_capita.clip(lower=0))

    return wide_df


def main() -> None:
    cleaned_frames = []

    for source_name, target_name in FILE_NAME_MAP.items():
        input_path = DATA_DIR / source_name
        output_path = DATA_DIR / target_name

        if not input_path.exists():
            raise FileNotFoundError(f"Missing input file: {input_path}")

        cleaned_df = clean_excel_file(input_path, output_path)
        cleaned_frames.append(cleaned_df)
        print(f"Saved cleaned file to {output_path}")

    merged_long_df = build_long_panel(cleaned_frames)
    merged_wide_df = build_wide_panel(merged_long_df)

    merged_long_df.to_excel(MERGED_LONG_OUTPUT, index=False)
    merged_wide_df.to_excel(MERGED_WIDE_OUTPUT, index=False)

    print(f"Saved merged long panel to {MERGED_LONG_OUTPUT}")
    print(f"Saved merged wide panel to {MERGED_WIDE_OUTPUT}")


if __name__ == "__main__":
    main()
