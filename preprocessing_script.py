from pathlib import Path

import pandas as pd


DATA_DIR = Path("data")

FILE_NAME_MAP = {
    "API_SP.DYN.TFRT.IN_DS2_en_excel_v2_667.xls": "Total Fertility Rate (SP.DYN.TFRT.IN).xlsx",
    "API_SL.TLF.CACT.FE.ZS_DS2_en_excel_v2_2415.xls": "Female Labor Force Participation Rate (SL.TLF.CACT.FE.ZS).xlsx",
    "API_SL.UEM.TOTL.FE.ZS_DS2_en_excel_v2_473.xls": "Female Unemployment Rate (SL.UEM.TOTL.FE.ZS).xlsx",
    "API_SE.TER.ENRR.FE_DS2_en_excel_v2_810.xls": "Girls’ Tertiary Enrollment (SE.TER.ENRR.FE).xlsx",
    "API_NY.GDP.PCAP.CD_DS2_en_excel_v2_724.xls": "GDP per Capita (NY.GDP.PCAP.CD).xlsx",
    "API_NY.GDP.MKTP.KD.ZG_DS2_en_excel_v2_675.xls": "GDP Growth Rate (NY.GDP.MKTP.KD.ZG).xlsx",
}


def clean_excel_file(input_path: Path, output_path: Path) -> None:
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
    reshaped_df.to_excel(output_path, index=False)


def main() -> None:
    for source_name, target_name in FILE_NAME_MAP.items():
        input_path = DATA_DIR / source_name
        output_path = DATA_DIR / target_name

        if not input_path.exists():
            raise FileNotFoundError(f"Missing input file: {input_path}")

        clean_excel_file(input_path, output_path)
        print(f"Saved cleaned file to {output_path}")


if __name__ == "__main__":
    main()
