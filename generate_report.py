import matplotlib.pyplot as plt
import pandas as pd
import os
import json
import numpy as np

# Prepare data collection
dfs = []

# Loop through all benchmark result files
for filename in os.listdir('./benchmark-data'):
    if filename.endswith('.json'):
        with open(f'./benchmark-data/{filename}', 'r') as file:
            data = json.load(file)
            split = filename.replace('.json', '').split('-')
            if len(split) >= 2:  # Prevents unpacking errors
                machine = split[0]+split[1]
                version = split[2]
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

# Calculate the improvement by sorting the lowest mean time
improvement_df = df.groupby("label")['mean_time'].min().reset_index()
improvement_df = improvement_df.sort_values(by="mean_time", ascending=True)

# Reorder the data by the biggest improvement
sorted_labels = improvement_df['label'].tolist()
df['label'] = pd.Categorical(df['label'], categories=sorted_labels, ordered=True)

# Recalculate unique labels for accurate plotting
unique_labels = df['label'].unique()
bar_width = 0.35  # Adjust bar width for better spacing

# Generate x_pos dynamically based on the number of labels
x_pos = np.arange(len(unique_labels))

# Plot the benchmark comparison (x_pos calculated for each loop)
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

# Finalize the plot with adjusted labels and ticks
plt.yticks(subset_x_pos, subset['label'])
plt.title('Benchmark Comparing Cached Install Time by Machine')
plt.xlabel('Mean Installation Time (s)')
plt.ylabel('Machine and Number of Files')
plt.legend(title="Pixi Version")
plt.grid(axis='x')
plt.tight_layout()

# Save the plot to a file
plt.savefig('benchmark_comparison_report.png', dpi=300)

# When debugging use this:
# plt.show()
