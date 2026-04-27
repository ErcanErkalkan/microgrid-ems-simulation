import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import numpy as np

def plot_resilience_results():
    output_dir = Path('outputs_fgcs_extensions')
    figures_dir = Path('manuscript/figures')
    figures_dir.mkdir(parents=True, exist_ok=True)
    
    csv_path = output_dir / 'fgcs_robustness_summary.csv'
    if not csv_path.exists():
        print(f"Data file {csv_path} not found. Waiting for experiments to complete.")
        return
        
    df = pd.read_csv(csv_path)
    
    # 1. Plot Resilience Score Bar Chart
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x='case', y='resilience_score', hue='controller', palette='viridis')
    plt.title('Cyber-Physical Resilience Score Across Network Dropout Rates')
    plt.ylabel('Resilience Score (%)')
    plt.xlabel('Disruption Scenario')
    plt.ylim(0, 105)
    plt.legend(title='Controller Architecture')
    plt.tight_layout()
    plt.savefig(figures_dir / 'resilience_score_bar.pdf')
    plt.close()
    
    # 2. Plot Cap Violation Comparison
    plt.figure(figsize=(8, 5))
    sns.barplot(data=df, x='case', y='cap_violation_pct_total', hue='controller', palette='rocket')
    plt.title('Grid Cap Violation Impact During Network Dropouts')
    plt.ylabel('Total Cap Violation (%)')
    plt.xlabel('Disruption Scenario')
    plt.legend(title='Controller Architecture')
    plt.tight_layout()
    plt.savefig(figures_dir / 'cap_violation_bar.pdf')
    plt.close()
    
    print("Successfully generated FGCS resilience plots in manuscript/figures/")

if __name__ == '__main__':
    plot_resilience_results()
