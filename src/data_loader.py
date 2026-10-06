from pathlib import Path
import re

import pandas as pd
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "WLD Survey(1-8).xlsx"
CORE_TEAM_COLUMN = "As of 1-OCT-2026, How many are serving as core team member (Chair + Co-chairs + Active Member)?"
WOMEN_CORE_COLUMN = "As of 1-OCT-2026, How many women associates are serving as core team member?"
GROUP_TYPE_COLUMN = "Which Employee Engagement Group you are in?"
GROUP_NAME_COLUMN = "Employee Engagement Group (BRG/CoP/Club) Name"


def _parse_core_team_answer(value: object) -> float:
    if pd.isna(value):
        return float("nan")
    text = str(value).strip()
    if re.fullmatch(r"\d+(?:\.\d+)?", text):
        return float(text)
    numbers = [float(number) for number in re.findall(r"\d+(?:\.\d+)?", text)]
    return sum(numbers) if numbers else float("nan")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_excel(DATA_PATH, sheet_name="Sheet1", engine="openpyxl")
    df.columns = df.columns.astype(str).str.strip()
    for column in df.select_dtypes(include="object").columns:
        df[column] = df[column].str.strip()

    df = df.dropna(how="all").copy()
    df["Start time"] = pd.to_datetime(df["Start time"], errors="coerce")
    df["Completion time"] = pd.to_datetime(df["Completion time"], errors="coerce")
    df["Core team members"] = df[CORE_TEAM_COLUMN].map(_parse_core_team_answer)
    df["Women core team members"] = pd.to_numeric(df[WOMEN_CORE_COLUMN], errors="coerce")
    df["Women share of core team"] = (
        df["Women core team members"]
        .div(df["Core team members"].replace(0, pd.NA))
        .mul(100)
    )
    return df


def apply_filters(
    df: pd.DataFrame,
    group_types: list[str],
    group_names: list[str],
) -> pd.DataFrame:
    filtered = df.copy()
    if group_types:
        filtered = filtered[filtered[GROUP_TYPE_COLUMN].isin(group_types)]
    if group_names:
        filtered = filtered[filtered[GROUP_NAME_COLUMN].isin(group_names)]
    return filtered
