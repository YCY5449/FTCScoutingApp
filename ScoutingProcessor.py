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


def parse_sequence(value):
    """Parse sequence string (e.g., '1, 2, 3') or number into list of values."""
    if pd.isna(value):
        return []
    if isinstance(value, str) and ',' in value:
        # Parse sequence string
        return [int(x.strip()) for x in value.split(',') if x.strip().isdigit()]
    # Try to parse as number (old format)
    try:
        num = int(float(value))
        return [num] if num > 0 else []
    except (ValueError, TypeError):
        return []


def normalize(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # numeric fields
    for col in [
        "Match Number",
        "Team Number",
    ]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    
    # Parse sequences and calculate values
    df["auto_near_seq"] = df["Auto Scored At Near"].apply(parse_sequence)
    df["auto_far_seq"] = df["Auto Scored At Far"].apply(parse_sequence)
    df["tele_near_seq"] = df["Tele-Op Scored At Near"].apply(parse_sequence)
    df["tele_far_seq"] = df["Tele-Op Scored At Far"].apply(parse_sequence)
    
    # Calculate totals from sequences
    df["Auto Scored At Near"] = df["auto_near_seq"].apply(lambda x: sum(x) if x else 0)
    df["Auto Scored At Far"] = df["auto_far_seq"].apply(lambda x: sum(x) if x else 0)
    df["Tele-Op Scored At Near"] = df["tele_near_seq"].apply(lambda x: sum(x) if x else 0)
    df["Tele-Op Scored At Far"] = df["tele_far_seq"].apply(lambda x: sum(x) if x else 0)
    
    # Calculate off target from sequences (3 - value for each entry)
    def combine_off_target(near_seq, far_seq):
        near_off = [3 - v for v in near_seq]
        far_off = [3 - v for v in far_seq]
        return near_off + far_off
    
    df["auto_off_seq"] = df.apply(lambda row: combine_off_target(row["auto_near_seq"], row["auto_far_seq"]), axis=1)
    df["tele_off_seq"] = df.apply(lambda row: combine_off_target(row["tele_near_seq"], row["tele_far_seq"]), axis=1)
    df["Auto Off Target"] = df["auto_off_seq"].apply(lambda x: sum(x) if x else 0)
    df["Tele-Op Off Target"] = df["tele_off_seq"].apply(lambda x: sum(x) if x else 0)
    
    # Get cycle counts
    df["Auto Cycles"] = pd.to_numeric(df.get("Auto Cycles", 0), errors="coerce").fillna(
        df["auto_near_seq"].apply(len) + df["auto_far_seq"].apply(len)
    ).astype(int)
    df["Tele-Op Cycles"] = pd.to_numeric(df.get("Tele-Op Cycles", 0), errors="coerce").fillna(
        df["tele_near_seq"].apply(len) + df["tele_far_seq"].apply(len)
    ).astype(int)
    df["Total Cycles"] = pd.to_numeric(df.get("Total Cycles", 0), errors="coerce").fillna(
        df["Auto Cycles"] + df["Tele-Op Cycles"]
    ).astype(int)

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
        auto_cycles_sum=("Auto Cycles", "sum"),
        tele_cycles_sum=("Tele-Op Cycles", "sum"),
        total_cycles_sum=("Total Cycles", "sum"),
        end_score_sum=("end_game_score", "sum"),
        total_score_sum=("total_score", "sum"),
    ).reset_index()

    # averages per match
    agg["auto_near_avg"] = agg["auto_near_sum"] / agg["matches"]
    agg["auto_far_avg"] = agg["auto_far_sum"] / agg["matches"]
    agg["tele_near_avg"] = agg["tele_near_sum"] / agg["matches"]
    agg["tele_far_avg"] = agg["tele_far_sum"] / agg["matches"]
    agg["auto_cycles_avg"] = agg["auto_cycles_sum"] / agg["matches"]
    agg["tele_cycles_avg"] = agg["tele_cycles_sum"] / agg["matches"]
    agg["total_cycles_avg"] = agg["total_cycles_sum"] / agg["matches"]
    agg["end_score_avg"] = agg["end_score_sum"] / agg["matches"]
    agg["total_score_avg"] = agg["total_score_sum"] / agg["matches"]
    
    # Calculate hit rates (命中率)
    # Hit rate = average score / max score (3)
    # Auto hit rate = (auto near + auto far) total value / (auto near + auto far) total cycles / 3
    # Tele hit rate = (tele near + tele far) total value / (tele near + tele far) total cycles / 3
    agg["auto_hit_rate"] = (agg["auto_near_sum"] + agg["auto_far_sum"]) / (agg["auto_cycles_sum"] * 3).replace(0, 1)
    agg["tele_hit_rate"] = (agg["tele_near_sum"] + agg["tele_far_sum"]) / (agg["tele_cycles_sum"] * 3).replace(0, 1)
    # Replace inf with 0 (when cycles is 0)
    agg["auto_hit_rate"] = agg["auto_hit_rate"].replace([float('inf'), -float('inf')], 0)
    agg["tele_hit_rate"] = agg["tele_hit_rate"].replace([float('inf'), -float('inf')], 0)

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
            "auto_cycles_avg",
            "tele_cycles_avg",
            "total_cycles_avg",
            "auto_hit_rate",
            "tele_hit_rate",
            "end_score_avg",
            "total_score_avg",
            "auto_near_sum",
            "auto_far_sum",
            "tele_near_sum",
            "tele_far_sum",
            "auto_cycles_sum",
            "tele_cycles_sum",
            "total_cycles_sum",
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

