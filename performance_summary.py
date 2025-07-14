import pandas as pd

def summarize_performance_report(file_path):
    df = pd.read_csv(file_path)
    
    print(f"Performance Report Summary from: {file_path}\n")
    print(df.describe())  # General stats
    
    # Show first few rows for quick glance
    print("\nSample data:")
    print(df.head())

if __name__ == "__main__":
    path = "results/NAS100_performance_report.csv"  # Update with your actual file path
    summarize_performance_report(path)
