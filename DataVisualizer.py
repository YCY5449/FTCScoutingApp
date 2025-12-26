#!/usr/bin/env python3
"""
Interactive table to view team rankings from team_score_summary.csv.

Run:
  streamlit run DataVisualizer.py

Dependencies:
  pip install streamlit pandas
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


DEFAULT_SUMMARY = Path("reports/team_score_summary.csv")


def load_summary(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    if "total_score_avg" not in df.columns:
        raise ValueError("total_score_avg not found in CSV.")

    # Default ranking by total_score_avg desc
    df = df.sort_values("total_score_avg", ascending=False).reset_index(drop=True)
    df.insert(0, "Rank", df.index + 1)
    return df


def main():
    st.set_page_config(page_title="Team Ranking", layout="wide")
    st.title("Team Ranking")
    st.caption("Sortable table for team scoring summary. Click column headers to sort.")

    # Sidebar file selector
    with st.sidebar:
        st.header("Data Source")
        default_exists = DEFAULT_SUMMARY.exists()
        use_default = st.checkbox(
            f"Use default: {DEFAULT_SUMMARY}", value=default_exists
        )
        uploaded = st.file_uploader("Or upload team_score_summary.csv", type=["csv"])

    df = None
    if uploaded is not None:
        df = pd.read_csv(uploaded)
    elif use_default and default_exists:
        df = load_summary(DEFAULT_SUMMARY)

    if df is None:
        st.warning("Please upload a CSV or ensure reports/team_score_summary.csv exists.")
        return

    # Ensure rank column present and recalc default ordering
    if "Rank" not in df.columns:
        df = df.sort_values("total_score_avg", ascending=False).reset_index(drop=True)
        df.insert(0, "Rank", df.index + 1)

    # Select columns to display
    display_cols = [
        "Rank",
        "Team Number",
        "matches",
        "auto_near_avg",
        "auto_far_avg",
        "tele_near_avg",
        "tele_far_avg",
        "auto_cycles_avg",
        "tele_cycles_avg",
        "total_cycles_avg",
        "auto_hit_rate",
        "tele_hit_rate",
        "end_score_avg",
        "total_score_avg",
    ]
    # Filter out missing columns
    available_cols = [c for c in display_cols if c in df.columns]
    missing = [c for c in display_cols if c not in df.columns]
    if missing:
        st.warning(f"Some columns missing (may be from old data format): {missing}")
    
    if not available_cols:
        st.error("No valid columns found in CSV.")
        return

    df_display = df[available_cols].copy()
    
    # Rename columns
    rename_map = {
        "Team Number": "Team",
        "matches": "Played",
        "auto_near_avg": "Auto Near AVG",
        "auto_far_avg": "Auto Far AVG",
        "tele_near_avg": "Tele Near AVG",
        "tele_far_avg": "Tele Far AVG",
        "auto_cycles_avg": "Auto Cycles AVG",
        "tele_cycles_avg": "Tele Cycles AVG",
        "total_cycles_avg": "Total Cycles AVG",
        "auto_hit_rate": "Auto Hit Rate",
        "tele_hit_rate": "Tele Hit Rate",
        "end_score_avg": "End AVG",
        "total_score_avg": "Total AVG",
    }
    df_display = df_display.rename(columns={k: v for k, v in rename_map.items() if k in df_display.columns})
    
    # Format hit rates as percentages
    if "Auto Hit Rate" in df_display.columns:
        df_display["Auto Hit Rate"] = df_display["Auto Hit Rate"].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A")
    if "Tele Hit Rate" in df_display.columns:
        df_display["Tele Hit Rate"] = df_display["Tele Hit Rate"].apply(lambda x: f"{x:.2%}" if pd.notna(x) else "N/A")

    st.dataframe(
        df_display,
        width="stretch",
        hide_index=True,
    )


if __name__ == "__main__":
    main()

