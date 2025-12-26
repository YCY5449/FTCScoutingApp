
import pandas as pd
import matplotlib.pyplot as plt
import os

def load_data(filepath):
    """Loads data from a CSV file."""
    if not os.path.exists(filepath):
        print(f"Error: File not found at {filepath}")
        return None
    return pd.read_csv(filepath)

def plot_endgame_actions(df):
    """Plots the frequency of endgame actions."""
    if 'End Game' not in df.columns:
        print("Error: 'End Game' column not found in data.")
        return

    # Split the 'End Game' string into individual actions and count their occurrences
    endgame_actions = df['End Game'].str.split('; ').explode().str.strip()
    action_counts = endgame_actions.value_counts()

    if action_counts.empty:
        print("No endgame action data to plot.")
        return

    plt.figure(figsize=(10, 6))
    action_counts.plot(kind='bar', color='skyblue')
    plt.title('Frequency of End Game Actions')
    plt.xlabel('End Game Action')
    plt.ylabel('Number of Occurrences')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def plot_total_score_distribution(df):
    """Plots the distribution of total scores."""
    if 'total_score' not in df.columns:
        print("Error: 'total_score' column not found in data.")
        return

    plt.figure(figsize=(10, 6))
    df['total_score'].hist(bins=20, color='lightgreen', edgecolor='black')
    plt.title('Distribution of Total Scores')
    plt.xlabel('Total Score')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.show()

def plot_team_average_scores(df):
    """Plots the average total score for each team."""
    if 'Team Number' not in df.columns or 'total_score' not in df.columns:
        print("Error: Required columns ('Team Number' or 'total_score') not found for team average scores.")
        return

    team_avg_scores = df.groupby('Team Number')['total_score'].mean().sort_values(ascending=False)

    if team_avg_scores.empty:
        print("No team average score data to plot.")
        return

    plt.figure(figsize=(12, 7))
    team_avg_scores.plot(kind='bar', color='coral')
    plt.title('Average Total Score Per Team')
    plt.xlabel('Team Number')
    plt.ylabel('Average Total Score')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

def plot_cycle_counts(df):
    """Plots cycle counts per team."""
    if 'Team Number' not in df.columns:
        print("Error: 'Team Number' column not found.")
        return
    
    cycle_cols = ['Total Cycles', 'Auto Cycles', 'Tele-Op Cycles']
    available_cols = [col for col in cycle_cols if col in df.columns]
    
    if not available_cols:
        print("Error: No cycle columns found in data.")
        return
    
    team_cycles = df.groupby('Team Number')[available_cols].mean().sort_values(by=available_cols[0] if available_cols else 'Team Number', ascending=False)
    
    if team_cycles.empty:
        print("No cycle data to plot.")
        return
    
    plt.figure(figsize=(12, 7))
    team_cycles.plot(kind='bar', stacked=False)
    plt.title('Average Cycle Counts Per Team')
    plt.xlabel('Team Number')
    plt.ylabel('Average Cycles')
    plt.xticks(rotation=45, ha='right')
    plt.legend(title='Cycle Type')
    plt.tight_layout()
    plt.show()

def plot_hit_rates(df):
    """Plots hit rates (命中率) per team."""
    if 'Team Number' not in df.columns:
        print("Error: 'Team Number' column not found.")
        return
    
    # Calculate hit rates if not already in dataframe
    if 'auto_hit_rate' not in df.columns or 'tele_hit_rate' not in df.columns:
        # Try to calculate from sequences
        # Hit rate = total value / (cycles * 3) where 3 is max score
        if 'Auto Scored At Near' in df.columns and 'Auto Scored At Far' in df.columns:
            auto_total = df['Auto Scored At Near'] + df['Auto Scored At Far']
            if 'Auto Cycles' in df.columns:
                df['auto_hit_rate'] = auto_total / (df['Auto Cycles'] * 3).replace(0, 1)
            else:
                print("Warning: Auto Cycles not found, cannot calculate auto hit rate.")
        
        if 'Tele-Op Scored At Near' in df.columns and 'Tele-Op Scored At Far' in df.columns:
            tele_total = df['Tele-Op Scored At Near'] + df['Tele-Op Scored At Far']
            if 'Tele-Op Cycles' in df.columns:
                df['tele_hit_rate'] = tele_total / (df['Tele-Op Cycles'] * 3).replace(0, 1)
            else:
                print("Warning: Tele-Op Cycles not found, cannot calculate tele hit rate.")
    
    hit_rate_cols = []
    if 'auto_hit_rate' in df.columns:
        hit_rate_cols.append('auto_hit_rate')
    if 'tele_hit_rate' in df.columns:
        hit_rate_cols.append('tele_hit_rate')
    
    if not hit_rate_cols:
        print("Error: No hit rate data found.")
        return
    
    team_hit_rates = df.groupby('Team Number')[hit_rate_cols].mean().sort_values(by=hit_rate_cols[0], ascending=False)
    
    if team_hit_rates.empty:
        print("No hit rate data to plot.")
        return
    
    plt.figure(figsize=(12, 7))
    team_hit_rates.plot(kind='bar', color=['skyblue', 'lightcoral'])
    plt.title('Hit Rates (命中率) Per Team')
    plt.xlabel('Team Number')
    plt.ylabel('Hit Rate')
    plt.xticks(rotation=45, ha='right')
    plt.legend(['Auto Hit Rate', 'Tele-Op Hit Rate'])
    plt.ylim(0, max(team_hit_rates.max().max() * 1.1, 1.0))
    plt.tight_layout()
    plt.show()

def provide_insights(df):
    """Provides key insights from the dataset."""
    print("\n--- Key Insights ---")

    # Example Insight 1: Most common endgame action
    if 'End Game' in df.columns:
        endgame_actions = df['End Game'].str.split('; ').explode().str.strip()
        most_common_action = endgame_actions.mode()[0] if not endgame_actions.empty else "N/A"
        print(f"Most common End Game action: {most_common_action}")

    # Example Insight 2: Average match number
    if 'Match Number' in df.columns:
        avg_match_number = df['Match Number'].mean()
        print(f"Average Match Number: {avg_match_number:.2f}")

    # Example Insight 3: Total records
    print(f"Total scouting records: {len(df)}")

    print("--------------------")

if __name__ == "__main__":
    # Assuming the processed data is saved as 'scouting_data.csv' in the reports directory
    data_filepath = 'reports/all_records_with_scores.csv'
    
    df = load_data(data_filepath)
    
    if df is not None:
        plot_endgame_actions(df)
        plot_total_score_distribution(df)
        plot_team_average_scores(df)
        plot_cycle_counts(df)
        plot_hit_rates(df)
        provide_insights(df)
