#!/usr/bin/env python3
"""
Aggregate scouting CSVs by team, compute scores, and export summary.

Rules:
- Every scored piece (auto/tele near/far) = 3 points each
- End Game:
    Partially: 5 pts
    Fully: 10 pts
    Double Park Beneficiary: 10 pts
    Double Park Dealer: 20 pts

For each team:
- Sum all counts
- Compute average per match (auto near, auto far, tele near, tele far)
- Compute average end-game score and total score
- Export CSV sorted by Team Number

Usage:
  python ScoutingProcessor.py             # reads *.csv in CWD, writes to ./reports
  python ScoutingProcessor.py --input ./csvs --output ./reports
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

ENDGAME_POINTS = {
    "Partially": 5,
    "Fully": 10,
    "Double Park Beneficiary": 10,
    "Double Park Dealer": 20,
}

SCORE_PER_PIECE = 3


def load_csvs(folder: Path) -> pd.DataFrame:
    files = sorted(folder.glob("*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {folder}")
    frames = []
    for f in files:
        df = pd.read_csv(f)
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # numeric fields
    for col in [
        "Match Number",
        "Team Number",
        "Auto Scored At Near",
        "Auto Scored At Far",
        "Auto Off Target",
        "Tele-Op Scored At Near",
        "Tele-Op Scored At Far",
        "Tele-Op Off Target",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # End game: take first option if multiple are present
    def endgame_value(val: str) -> str:
        if not isinstance(val, str):
            return ""
        parts = [p.strip() for p in val.split(";") if p.strip()]
        return parts[0] if parts else ""

    df["End Game (Norm)"] = df["End Game"].apply(endgame_value)

    # Compute climb score
    df["end_game_score"] = df["End Game (Norm)"].map(ENDGAME_POINTS).fillna(0).astype(float)

    # Total score: each scored piece is 3 pts
    df["piece_score"] = (
        df["Auto Scored At Near"]
        + df["Auto Scored At Far"]
        + df["Tele-Op Scored At Near"]
        + df["Tele-Op Scored At Far"]
    ) * SCORE_PER_PIECE
    df["total_score"] = df["piece_score"] + df["end_game_score"]
    return df


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    agg = df.groupby("Team Number").agg(
        matches=("Match Number", "nunique"),
        auto_near_sum=("Auto Scored At Near", "sum"),
        auto_far_sum=("Auto Scored At Far", "sum"),
        tele_near_sum=("Tele-Op Scored At Near", "sum"),
        tele_far_sum=("Tele-Op Scored At Far", "sum"),
        end_score_sum=("end_game_score", "sum"),
        total_score_sum=("total_score", "sum"),
    ).reset_index()

    # averages per match
    agg["auto_near_avg"] = agg["auto_near_sum"] / agg["matches"]
    agg["auto_far_avg"] = agg["auto_far_sum"] / agg["matches"]
    agg["tele_near_avg"] = agg["tele_near_sum"] / agg["matches"]
    agg["tele_far_avg"] = agg["tele_far_sum"] / agg["matches"]
    agg["end_score_avg"] = agg["end_score_sum"] / agg["matches"]
    agg["total_score_avg"] = agg["total_score_sum"] / agg["matches"]

    agg = agg.sort_values("Team Number")

    # Reorder / select columns for export
    return agg[
        [
            "Team Number",
            "matches",
            "auto_near_avg",
            "auto_far_avg",
            "tele_near_avg",
            "tele_far_avg",
            "end_score_avg",
            "total_score_avg",
            "auto_near_sum",
            "auto_far_sum",
            "tele_near_sum",
            "tele_far_sum",
            "end_score_sum",
            "total_score_sum",
        ]
    ]


def main():
    parser = argparse.ArgumentParser(description="Aggregate scouting CSVs by team.")
    parser.add_argument(
        "--input",
        default=".",
        help="Folder containing CSV exports (default: current working directory)",
    )
    parser.add_argument("--output", default="reports", help="Output folder")
    args = parser.parse_args()

    input_dir = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = load_csvs(input_dir)
    df_norm = normalize(df)
    summary = summarize(df_norm)

    summary_path = output_dir / "team_score_summary.csv"
    detail_path = output_dir / "all_records_with_scores.csv"

    summary.to_csv(summary_path, index=False)
    df_norm.to_csv(detail_path, index=False)

    print(f"Saved summary: {summary_path}")
    print(f"Saved detailed records: {detail_path}")


if __name__ == "__main__":
    main()

