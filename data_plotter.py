
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
    action_counts = endgamuye_actions.value_counts()

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
    data_filepath = 'reports/scouting_data.csv'
    
    df = load_data(data_filepath)
    
    if df is not None:
        plot_endgame_actions(df)
        provide_insights(df)
