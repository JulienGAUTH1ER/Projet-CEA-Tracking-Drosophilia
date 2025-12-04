import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import re
import random

#%% CONFIGURATION

# Choice point definitions
xabs = 16
yord = 67
x, y = 108, 343

choicepoints = {
    'Choice1': [[x-6, y-7], [x+6+xabs, y-7]],
    'Choice2': [[x-xabs, y-yord], [x, y-yord], [x+xabs, y-yord], [x+xabs*2, y-yord]],
    'Choice3': [[x-xabs*2, y-yord*2], [x-xabs, y-yord*2], [x, y-yord*2], [x+xabs, y-yord*2], [x+xabs*2, y-yord*2], [x+xabs*3, y-yord*2]],
    'Choice4': [[x-xabs*3, y-yord*3], [x-xabs*2, y-yord*3], [x-xabs, y-yord*3], [x, y-yord*3], [x+xabs, y-yord*3], [x+xabs*2, y-yord*3], [x+xabs*3, y-yord*3], [x+xabs*4, y-yord*3]],
    'Choice5': [[x-xabs*4, y-yord*4], [x-xabs*3, y-yord*4], [x-xabs*2, y-yord*4], [x-xabs, y-yord*4], [x, y-yord*4], [x+xabs, y-yord*4], [x+xabs*2, y-yord*4], [x+xabs*3, y-yord*4], [x+xabs*4, y-yord*4], [x+xabs*5, y-yord*4]],
    'Choice6': [[x-xabs*5, y-yord*5], [x-xabs*4, y-yord*5], [x-xabs*3, y-yord*5], [x-xabs*2, y-yord*5], [x-xabs, y-yord*5], [x, y-yord*5], [x+xabs, y-yord*5], [x+xabs*2, y-yord*5], [x+xabs*3, y-yord*5], [x+xabs*4, y-yord*5], [x+xabs*5, y-yord*5], [x+xabs*6, y-yord*5]],
}

# Generate odor positions
odor = {'Choice1': [[130, 336]],
 'Choice2': [ [108, 276], [124, 276]],
 'Choice3': [[92, 209], [108, 209], [140, 209]],
 'Choice4': [[60, 142], [92, 142], [140, 142], [172, 142]],
 'Choice5': [[44, 75], [92, 75], [108, 75], [140, 75],  [188, 75]],
 'Choice6': [[28, 8], [60, 8], [108, 8],  [140, 8], [156, 8], [204, 8]]}

# Collect non-odor points for plotting
non_odor_points = []
for choice, coords in choicepoints.items():
    odor_coords = set(map(tuple, odor[choice]))
    for point in coords:
        if tuple(point) not in odor_coords:
            non_odor_points.append(point)

# Generate chamber midpoints
chamber = {}
distance_below_choice = 17
for choice, points in choicepoints.items():
    chamber_midpoints = []
    for i in range(0, len(points) - 1, 2):
        chamber_x = round((points[i][0] + points[i + 1][0]) / 2)
        chamber_y = points[i][1] + distance_below_choice
        chamber_midpoints.append([chamber_x, chamber_y])
    chamber[choice] = chamber_midpoints

# Flatten overlays for plotting
odor_points = [pt for pts in odor.values() for pt in pts]
chamber_points = [pt for pts in chamber.values() for pt in pts]

#%% DATA LOADING

root_folder = "Results/"
columns_to_extract = ["Time_stamp", "Frame_number", "Larva_centroid_X", "Larva_centroid_Y"]

odor_conditions = ["AIR", "ETAC_10-2","ETAC_2X10-3"]
conditions = ["F", "H"]
lights = ["D", "LL", "HL"]
combinations = [(odor, cond, light) for odor in odor_conditions for cond in conditions for light in lights]

filename_pattern = re.compile(r"^(AIR|EtAc_10-2|EtAc_2x10-3)[^_]*_.*?_([FH])_((?:D|LL|HL))", re.IGNORECASE)

data_by_condition = {}

for file in os.listdir(root_folder):
    if file.endswith(".csv"):
        match = filename_pattern.search(file)
        if match:
            odor_condition = match.group(1).upper()
            print(odor_condition)
            condition = match.group(2).upper()
            light = match.group(3).upper()
            key = (odor_condition, condition, light)

            file_path = os.path.join(root_folder, file)
            try:
                df = pd.read_csv(file_path, skiprows=1)
                df_filtered = df[columns_to_extract].dropna()
                df_filtered["Larva_centroid_X"] = df_filtered["Larva_centroid_X"].astype(int)
                df_filtered["Larva_centroid_Y"] = df_filtered["Larva_centroid_Y"].astype(int)

                if key in data_by_condition:
                    data_by_condition[key] = pd.concat([data_by_condition[key], df_filtered], ignore_index=True)
                else:
                    data_by_condition[key] = df_filtered

            except Exception as e:
                print(f"Error processing {file}: {e}")
        else:
            print(f"No match for file: {file}")

# Combine LL and HL into "Light"
for odor_condition in odor_conditions:
    for condition in conditions:
        df_ll = data_by_condition.get((odor_condition, condition, "LL"))
        df_hl = data_by_condition.get((odor_condition, condition, "HL"))

        if df_ll is not None and df_hl is not None:
            combined_df = pd.concat([df_ll, df_hl], ignore_index=True)
        elif df_ll is not None:
            combined_df = df_ll
        elif df_hl is not None:
            combined_df = df_hl
        else:
            combined_df = None

        if combined_df is not None:
            data_by_condition[(odor_condition, condition, "Light")] = combined_df

#%% PLOTTING FUNCTION

def plot_heatmaps(data_dict, odor_condition, lights_list, title_prefix, overlay=True):
    fig_cols = len(lights_list)
    fig_rows = len(conditions)
    fig, axes = plt.subplots(fig_rows, fig_cols, figsize=(5 * fig_cols, 5 * fig_rows))
    fig.suptitle(f"{title_prefix} ({odor_condition})", fontsize=16)
    cbar_ax = fig.add_axes([0.92, 0.25, 0.015, 0.5])

    all_values = []
    for key, df in data_dict.items():
        if key[0] == odor_condition and df is not None and not df.empty:
            heatmap_data = df.groupby(["Larva_centroid_Y", "Larva_centroid_X"]).size().unstack(fill_value=0)
            all_values.extend(heatmap_data.values.flatten())

    global_vmax = np.percentile(all_values, 99) if all_values else 1

    for i, condition in enumerate(conditions):
        for j, light in enumerate(lights_list):
            ax = axes[i, j] if fig_rows > 1 else axes[j]
            title = f"{condition} / {light}"

            df_clean = data_dict.get((odor_condition, condition, light))
            if df_clean is None or df_clean.empty:
                ax.set_title(f"{title}\n(No Data)")
                ax.axis("off")
                continue

            heatmap_data = df_clean.groupby(["Larva_centroid_Y", "Larva_centroid_X"]).size().unstack(fill_value=0)
            heatmap_data_clipped = heatmap_data.clip(upper=global_vmax)
            heatmap_data_norm = heatmap_data_clipped / global_vmax
            mask = heatmap_data_norm == 0

            sns.heatmap(
                heatmap_data_norm,
                cmap="OrRd",
                cbar=(i == 0 and j == 0),
                cbar_ax=cbar_ax if (i == 0 and j == 0) else None,
                xticklabels=False,
                yticklabels=False,
                mask=mask,
                square=True,
                ax=ax
            )

            if overlay:
                if odor_points:
                    xs, ys = zip(*odor_points)
                    ax.scatter(xs, ys, color='blue', s=40, marker='+', label='Odor', zorder=5)
                if non_odor_points:
                    xs, ys = zip(*non_odor_points)
                    ax.scatter(xs, ys, color='gray', s=40, marker='x', label='Non-Odor', zorder=5)
                if chamber_points:
                    xs, ys = zip(*chamber_points)
                    ax.scatter(xs, ys, color='black', s=20, marker='o', label='Chambers', zorder=5)

                if i == 0 and j == 0:
                    ax.legend(loc='upper right', fontsize=7)

            ax.set_title(title)
            ax.set_xlabel("")
            ax.set_ylabel("")

    plt.tight_layout(rect=[0, 0, 0.9, 0.95])
    plt.show()

#%% GENERATE HEATMAPS

for odor_condition in odor_conditions:
    plot_heatmaps(data_by_condition, odor_condition, lights, "Larva Heatmaps", overlay=False)

# Combined LL + HL as "Light"
for odor_condition in odor_conditions:
    plot_heatmaps(data_by_condition, odor_condition, ["D", "Light"], "Larva Heatmaps (LL+HL Combined)", overlay=True)
