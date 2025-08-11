import re

import pandas as pd

from Config import Config


def load_csv() -> pd.DataFrame:
    """
    Load the input CSV file specified in the configuration.
    """
    input_csv = Config["INPUT_CSV"]
    try:
        df = pd.read_csv(input_csv, sep=";")
        return df
    except FileNotFoundError:
        print(f"Error: The file {input_csv} does not exist.")
        return pd.DataFrame()


def clean_text(text: str) -> str:
    if pd.isna(text):
        return ""

    text = re.sub(
        r"\s+", " ", text
    ).strip()  # replace multiple spaces with a single space

    return text

# TODO: add more preprocessing if necessary
def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Preprocess the DataFrame by cleaning text columns.
    """
    if df.empty:
        print("DataFrame is empty. No preprocessing needed.")
        return df

    df = df.copy()

    if "descricao" in df.columns:
        df["descricao_clean"] = df["descricao"].apply(clean_text)
    else:
        print("Warning: 'descricao' column not found in DataFrame.")
        df["descricao_clean"] = ""

    return df
