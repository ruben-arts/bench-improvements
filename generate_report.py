import matplotlib.pyplot as plt
import pandas as pd
import os
import json
import numpy as np

# Prepare data collection
dfs = []

# Loop through all benchmark result files
for filename in os.listdir('./benchmark-data'):
    with open(f'./benchmark-data/{filename}', 'r') as file:
        data = json.load(file)
        split = filename.replace('.json', '').split('_')
        if len(split) >= 2:  # Prevent unpacking errors
            machine = split[0]
            version = split[1]
            for entry in data['results']:
                e_flag = entry['command'].split('-e')[-1].strip()
                dfs.append({
                    'machine_type': machine,
                    'pixi_version': version,
                    'e_flag': e_flag,
                    'mean_time': entry['mean']
                })

# Convert data into DataFrame
df = pd.DataFrame(dfs)

# Check if 'label' exists, if not create it
if 'label' not in df.columns:
    df['label'] = df['machine_type'] + " - " + df['e_flag']

# Calculate the improvement by taking the difference between old and new versions
improvement_df = df.groupby("label")['mean_time'].min().reset_index()
improvement_df = improvement_df.sort_values(by="mean_time", ascending=True)

# Reorder the data by the biggest improvement (smallest mean_time)
sorted_labels = improvement_df['label'].tolist()
df['label'] = pd.Categorical(df['label'], categories=sorted_labels, ordered=True)

# Recalculate unique labels for accurate plotting
unique_labels = df['label'].unique()

# Calculate the amount of versions for dynamic plotting
num_versions = len(df['pixi_version'].unique())
bar_width = 0.90/num_versions  # Adjust bar width for better spacing

# Generate x_pos dynamically based on the number of labels
x_pos = np.arange(len(unique_labels))

# === BAR CHART ===
plt.figure(figsize=(14, 10))

# Plot each version separately with dynamically calculated x_pos
for idx, version in enumerate(df['pixi_version'].unique()):
    subset = df[df['pixi_version'] == version].sort_values(by="label")
    subset_x_pos = np.arange(len(subset))  # Match the length of the subset
    if not subset.empty:
        plt.barh(
            subset_x_pos + (idx * bar_width) - (bar_width / 2),
            subset['mean_time'].values,
            height=bar_width,
            label=f"Pixi {version}"
        )

# Finalize the bar plot with adjusted labels and ticks
plt.yticks(subset_x_pos, subset['label'])
plt.title('Benchmark Comparing Cached Install Time by Machine')
plt.xlabel('Mean Installation Time (s)')
plt.ylabel('Machine and Environment')
plt.legend(title="Pixi Version")
plt.grid(axis='x')
plt.tight_layout()

# Save the bar chart to a file
plt.savefig('benchmark_comparison_bar_chart.png', dpi=300)

# === LINE GRAPH ===
plt.figure(figsize=(14, 10))

# Line plot for each machine and environment over multiple pixi versions
for label in unique_labels:
    subset = df[df['label'] == label].sort_values(by="pixi_version")
    plt.plot(
        subset['pixi_version'],
        subset['mean_time'],
        marker='o',
        label=label
    )

# Finalize the line plot with adjusted labels and ticks
plt.title('Benchmark Trend Over Pixi Versions')
plt.xlabel('Pixi Version')
plt.ylabel('Mean Installation Time (s)')
plt.legend(title="Machine and Environment", loc="upper right")
plt.grid(axis='y')
plt.tight_layout()

# Save the line chart to a separate file
plt.savefig('benchmark_comparison_line_graph.png', dpi=300)

# Optional: Show plots (commented out since you're saving files)
# plt.show()
