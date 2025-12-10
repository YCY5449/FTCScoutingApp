## ScoutingApp Usage Guide

### 1) Environment
```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt    # or: pip install pandas matplotlib streamlit
```

### 2) Data Collection (FTC2026ScoutingApp.html)
- Open `FTC2026ScoutingApp.html` in a browser (mobile/tablet full screen recommended).
- Required fields: Match Number, Team Number, Alliance Color, Starting Position, Pre-match (choose one), End Game (choose one), Remarks, Submitter.
- Counters: Auto/Tele Near/Far/Off Target; Defense toggle; End Game four options.
- Export: click `Export CSV` to generate `FTC_Scouting_Data_YYYY-MM-DD.csv`.

### 3) Processing (ScoutingProcessor.py)
Reads all exported CSVs in a folder, aggregates by team, scores, and outputs summaries.
```bash
source .venv/bin/activate
# default: read *.csv in current dir, output to ./reports
python ScoutingProcessor.py
# custom input/output
python ScoutingProcessor.py --input ./csvs --output ./reports
```
Scoring (hard-coded):
- Each scored piece (Auto/Tele Near/Far) = 3 pts
- End Game: Partially 5; Fully 10; Double Park Beneficiary 10; Double Park Dealer 20
- Per team: sums all counts; per-match averages (auto_near_avg / auto_far_avg / tele_near_avg / tele_far_avg / end_score_avg / total_score_avg)

Outputs (default `reports/`):
- `team_score_summary.csv`: sorted by team number, includes averages and sums
- `all_records_with_scores.csv`: per-record with piece_score / end_game_score / total_score

### 4) Visualization (DataVisualizer.py)
Interactive sortable table of team rankings.
```bash
source .venv/bin/activate
streamlit run DataVisualizer.py
```
Features:
- Default reads `reports/team_score_summary.csv`; sidebar allows uploading a custom CSV.
- Click column headers to sort. Columns: Rank, Team, Played, Auto/Tele Near/Far AVG, End AVG, Total AVG.

### 5) FAQ
- Running `python DataVisualizer.py` shows “missing ScriptRunContext”; use `streamlit run DataVisualizer.py`.
- If you see invalid config `global.loggerLevel` or `global.browser`, remove them from `~/.streamlit/config.toml`.
- “No CSV files found”: ensure the `--input` directory contains `.csv` files.

### 6) Minimal dependencies
```
pandas
matplotlib
streamlit
```
