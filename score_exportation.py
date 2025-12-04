import os
import pandas as pd
import re
import matplotlib.pyplot as plt

'''
Note: This code creates boxplots of the scores (warning: scores are not always out of 6 so it should maybe be updated to fraction scores)
for different combinations of conditions and compares them with mathematical models predictions. Then, for each experiment, it saves arrival
times, odor choice times, the path chosen at each choice, and the success of each choice inside "combined_results.csv". Then, we copy paste
every column besides choice_row_last_Letter inside "combined_results_Check.csv" to manually verify the results with the tracking jpeg from Results
or Data because errors may remain. It also allows to verify that the tracking worked properly.
choice_row_last_Letter is used to get the activation plots (saved in a folder). 
It is important to note that for the Success column, 0 corresponds to the correct choice (purple) and 1 corresponds to the incorrect choice
(green). It was not intentional and it is not the standard.
For more detailed questions about the code itself, Anna should know more about it.
'''

#%% Directory where CSVs are stored
root_folder = "Results/"

# Conditions and lights definitions

odor_conditions = ["AIR", "ETAC"]
conditions = ["F", "H"]
lights = ["D", "LL", "HL"]
combinations = [(odor, cond, light) for odor in odor_conditions for cond in conditions for light in lights]

combined_light_label = "Light"

# Regex to parse filenames
#filename_pattern = re.compile(r"_([FH])_((?:D|LL|HL))_raw\.csv$", re.IGNORECASE)
filename_pattern = re.compile(r"^(AIR|EtAc)[^_]*_.*?_([FH])_((?:D|LL|HL))", re.IGNORECASE)

# Store full dataframes per (condition, light)
data_by_condition = {}

# Load each file and group by (condition, light)
for file in os.listdir(root_folder):
    if file.endswith(".csv"):
        match = filename_pattern.search(file)
        if match:
            # condition = match.group(1).upper()
            # light = match.group(2).upper()
            # key = (condition, light)

            odor_condition = match.group(1).upper()
            condition = match.group(2).upper()
            light = match.group(3).upper()
            key = (odor_condition, condition, light)
            file_path = os.path.join(root_folder, file)
            
            try:
                df = pd.read_csv(file_path, skiprows=1)
                print(df.head())  # Debug: print first few rows of the dataframe
                # Append df to group
                if key in data_by_condition:
                    data_by_condition[key] = pd.concat([data_by_condition[key], df], ignore_index=True)               
                else:
                    data_by_condition[key] = df
            except Exception as e:
                print(f"Error processing {file}: {e}")
        else:
            print(f"No regex match for file: {file}")

# Combine LL and HL into one "Light" group per condition
for condition in conditions:
    df_ll = data_by_condition.get((condition, "LL"))
    df_hl = data_by_condition.get((condition, "HL"))

    if df_ll is not None and df_hl is not None:
        combined_df = pd.concat([df_ll, df_hl], ignore_index=True)
    elif df_ll is not None:
        combined_df = df_ll
    elif df_hl is not None:
        combined_df = df_hl
    else:
        combined_df = None

    if combined_df is not None:
        data_by_condition[(condition, combined_light_label)] = combined_df


#%%
from collections import OrderedDict
import os
import re
import pandas as pd

arrival_times_by_condition = {}

# Regex pattern to extract date-time (adjust to your filename format)
datetime_pattern = re.compile(r'(\d{4}-\d{2}-\d{2}[_\-]\d{2}[-:]\d{2}[-:]\d{2})')

# This list will store one dict per CSV file for final DataFrame
all_data_rows = []

labels = ['A', 'B', 'C', 'D', 'E', 'F']


for file in os.listdir(root_folder):
    if file.endswith(".csv"):
        match = filename_pattern.search(file)
        if match:
            odor_condition = match.group(1).upper()
            condition = match.group(2).upper()
            light = match.group(3).upper()
            file_path = os.path.join(root_folder, file)

            # Extract date-time from filename
            datetime_match = datetime_pattern.search(file)
            if datetime_match:
                file_key = datetime_match.group(1)
            else:
                file_key = os.path.splitext(file)[0]

            try:
                df = pd.read_csv(file_path, skiprows=1)

                # Initialize nested OrderedDict for the condition if not exists
                if odor_condition not in arrival_times_by_condition:
                    arrival_times_by_condition[odor_condition] = {}

                if condition not in arrival_times_by_condition:
                    arrival_times_by_condition[condition] = OrderedDict([('LL', {}), ('HL', {}), ('D', {})])

                # Prepare containers for times, default empty lists if columns missing
                arrival_times = []
                odor_choice_times = []
                choice_row_last = None
                SuccessTT_series_last = None

                if "Chamber_arrival_Time" in df.columns:
                    arrival_times = df["Chamber_arrival_Time"].dropna()
                    arrival_times = arrival_times[arrival_times > 0].unique()
                    arrival_times = sorted(float(round(x, 5)) for x in arrival_times)
                else:
                    print(f"Warning: 'Chamber_arrival_Time' not found in {file}")

                if "Odor_choice_time" in df.columns:
                    odor_choice_times = df["Odor_choice_time"].dropna()
                    odor_choice_times = odor_choice_times[odor_choice_times > 0].unique()
                    odor_choice_times = sorted(float(round(x, 5)) for x in odor_choice_times)
                else:
                    print(f"Warning: 'Odor_choice_time' not found in {file}")

                if "choice_row" in df.columns:
                    choice_row_series = df["choice_row"].dropna()
                    if not choice_row_series.empty:
                        choice_row_last = choice_row_series.iloc[-1]
                        lst = choice_row_last.strip('[]').split(',')
                        lst = [x.strip() for x in lst]

                        choice_row_last_Letter = []
                        for i, val in enumerate(lst):
                            if val.lower() == 'nan':
                                choice_row_last_Letter.append('nan')
                            else:
                                label = labels[i] if i < len(labels) else f"X{i}"
                                choice_row_last_Letter.append(f"{label}{val}")


                if "SuccessTT" in df.columns:
                    SuccessTT_series = df["SuccessTT"].dropna()
                    if not SuccessTT_series.empty:
                        SuccessTT_series_last = SuccessTT_series.iloc[-1]
                else:
                    print(f"Warning: 'SuccessTT' not found in {file}")

                # Save all extracted data into your nested dict (optional)
                arrival_times_by_condition[condition][light][file_key] = {
                    "arrival_times": arrival_times,
                    "odor_choice_times": odor_choice_times,
                    "choice_row_last": choice_row_last,
                    "choice_row_last_Letter": choice_row_last_Letter,
                    "SuccessTT_last": SuccessTT_series_last
                }

                # Append a row dict to the list for final DataFrame
                all_data_rows.append({
                    "odor_condition": odor_condition,
                    "Condition": condition,
                    "Light": light,
                    "File_DateTime": file_key,
                    "Arrival_Times": arrival_times,
                    "Odor_Choice_Times": odor_choice_times,
                    "Choice_Row_Last": choice_row_last,
                    "choice_row_last_Letter": choice_row_last_Letter,
                    "SuccessTT_Last": SuccessTT_series_last
                })

                print(f"{odor_condition} {condition} ({light}) [{file_key}]: {len(arrival_times)} arrivals, "
                      f"{len(odor_choice_times)} odor choice times, "
                      f"choice_row_last_Letter: {choice_row_last_Letter}, SuccessTT last: {SuccessTT_series_last}")

            except Exception as e:
                print(f"Error processing {file}: {e}")

# After processing all files, convert all_data_rows to DataFrame and save to Excel
df_all = pd.DataFrame(all_data_rows)

output_excel_path = "combined_results.xlsx"
df_all.to_excel(output_excel_path, index=False)

print(f"\nAll data saved to {output_excel_path}")

#%% boxplot part 

import pandas as pd
import ast
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


# Load the previously saved Excel file
excel_file = "combined_results_Check.xlsx"
df_all = pd.read_excel(excel_file)

labels = ['A', 'B', 'C', 'D', 'E', 'F']

def create_choice_row_last_letter(choice_row_str):
    if pd.isna(choice_row_str):
        return []
    try:
        # Remove brackets and split by comma
        lst = choice_row_str.strip('[]').split(',')
        lst = [x.strip() for x in lst]
    except Exception:
        return []

    result = []
    for i, val in enumerate(lst):
        if val.lower() == 'nan':
            result.append('nan')
        else:
            label = labels[i] if i < len(labels) else f"X{i}"
            result.append(f"{label}{val}")
    return result

# Apply function to create new column
df_all['choice_row_last_Letter'] = df_all['Choice_Row_Last'].apply(create_choice_row_last_letter)

print(df_all[['Choice_Row_Last', 'choice_row_last_Letter']].head())




def parse_successTT(entry):
    if pd.isna(entry):
        return []
    if isinstance(entry, list):
        return entry
    entry = str(entry).strip()

    # Safety clean-up before eval
    entry = entry.replace('nan', 'np.nan')  # Prepare for eval to parse np.nan
    try:
        parsed = eval(entry, {"np": np})
        if isinstance(parsed, list):
            return parsed
        else:
            return [parsed]
    except Exception as e:
        print(f"Parse error for entry: {entry} | Error: {e}")
        return []


# Parse and sum SuccessTT_Last per CSV
df_all["SuccessTT_List"] = df_all["SuccessTT_Last"].apply(parse_successTT)

# # Clean and sum ignoring NaNs  number of 1 
# def clean_and_sum(lst):
#     clean = [float(x) if not pd.isna(x) else np.nan for x in lst]
#     return float(np.nansum(clean))

# # Compute Score
# df_all["Score"] = df_all["SuccessTT_List"].apply(clean_and_sum)

# Count number of zeros in SuccessTT_List
def count_zeros(lst):
    clean_list = [x for x in lst if pd.notna(x)]  # Remove NaNs
    return sum(x == 0 for x in clean_list)

df_all["Score"] = df_all["SuccessTT_List"].apply(count_zeros)

# Assuming df_all with columns "Condition", "Light", "Score"

# Define your custom colors for the hue levels
palette = {
    "D": "grey",
    "HL": "orange",
    "LL": "gold"  # gold = better visibility than pure yellow
}

# Make sure the hue order matches the palette keys
hue_order = ["D", "HL", "LL"]
# x_order = df_all["Condition"].unique()


# Create a combined column
df_all["Condition_T"] =  df_all["odor_condition"] + "_" + df_all["Condition"] 

# Define x_order based on unique combinations
x_order = df_all["Condition_T"].unique()


# Plot
plt.figure(figsize=(10, 6))
ax = sns.boxplot(data=df_all, x="Condition_T", y="Score", hue="Light", palette=palette, hue_order=hue_order)

# Get order of hue and x axis
hue_order = df_all["Light"].unique()
x_order = df_all["Condition_T"].unique()

# Count total boxes to match n positions
n_hue = len(hue_order)
n_x = len(x_order)

# Compute x positions manually
# Each Condition gets n_hue boxes (side by side)
xticks = np.arange(n_x)

width_per_box = 0.8 / n_hue  # total box group width = 0.8

positions = []

for xi in xticks:
    for hi in range(n_hue):
        pos = xi - 0.4 + width_per_box / 2 + hi * width_per_box
        positions.append(pos)

# Get counts (n) for each (Condition, Light)
group_counts = df_all.groupby(["Condition_T", "Light"]).size().reset_index(name='n')

# Annotate counts
for i, row in group_counts.iterrows():
    x_pos = positions[i]
    y_pos = df_all["Score"].max() * 0.75  # adjust vertically

    print(row)

    ax.text(x_pos, y_pos, f"n={row['n']}", ha='center', va='bottom', fontsize=9, color='black')

# Final plot tweaks

plt.ylabel("Score")
plt.xlabel("Condition")
plt.legend(title="Light")
plt.tight_layout()


plt.savefig("Score_by_Condition_and_Light.svg", format="svg",  transparent=True)
plt.show()

#%% 

# Combine LL and HL into one group "Light"
df_all_combined = df_all.copy()

# Replace LL and HL by "Light" in Light column
df_all_combined.loc[df_all_combined["Light"].isin(["LL", "HL"]), "Light"] = "Light"

# Now plot with new hue_order
palette_combined = {
    "D": "grey",
    "Light": "orange",  # or any color you like
}

hue_order_combined = ["D", "Light"]

plt.figure(figsize=(10, 6))
ax = sns.boxplot(data=df_all_combined, x="Condition_T", y="Score", hue="Light",
                 palette=palette_combined, hue_order=hue_order_combined)

# Count total boxes for annotation
n_hue = len(hue_order_combined)
n_x = df_all_combined["Condition_T"].nunique()

xticks = np.arange(n_x)
width_per_box = 0.8 / n_hue
positions = []

for xi in xticks:
    for hi in range(n_hue):
        pos = xi - 0.4 + width_per_box / 2 + hi * width_per_box
        positions.append(pos)

# Group counts for annotation
group_counts = df_all_combined.groupby(["Condition_T", "Light"]).size().reset_index(name='n')

# for i, row in group_counts.iterrows():
#     x_pos = positions[i]
#     y_pos = df_all_combined["Score"].max() * 0.75

#     ax.text(x_pos, y_pos, f"n={row['n']}", ha='center', va='bottom', fontsize=9, color='black')

plt.ylabel("Score")
plt.xlabel("Condition")
plt.legend(title="Light")
plt.tight_layout()
plt.savefig("Score_by_Condition_and_Combined_Light.svg", format="svg",  transparent=True)
plt.show()



#%%Combined Boxplot of Total Scores from Both Simulations 0.5


Rep_def = {
    1: { "Ment": {"A0", "B0", "C0", "D1", "E3", "F5", "D7", "E9", "F11" }, 
        "Ethyl": {"A1", "B3", "C5", "D6", "E6", "F6", "D0", "E0", "F0" }},
    21: { "Ment": {}, 
             "Ethyl": {"A1", "B1", 'B2', "C1", "C2", "C4", "D0", "D2", "D5", "D7", "E0", "E3", "E4", "E6", "E9", "F0", "F2", "F5", "F7", "F8", "F11" }},
    22: { "Ment": {"A0", "B0" ,"B3", "C0", "C3", "C5", "D1", "D3", "D4", "D6", "E1", "E2", "E5", "E7", "E8", "F1", "F3", "F4", "F6", "F9", "F10"}, 
             "Ethyl": {}},
    3: { "Ment": {}, 
        "Ethyl": {}},
    4: { "Ment": {"A0", "B0" ,"B3", "C0", "C3", "C5", "D1", "D3", "D4", "D6", "E1", "E2", "E5", "E7", "E8", "F1", "F3", "F4", "F6", "F9", "F10"}, 
    "Ethyl": {"A1", "B1", 'B2', "C1", "C2", "C4", "D0", "D2", "D5", "D7", "E0", "E3", "E4", "E6", "E9", "F0", "F2", "F5", "F7", "F8", "F11" }},
}

N = 100  # number of trials

# Fixed p = 0.5
tot_score_fixed = []
for _ in range(N):
    score = 0
    for _ in range(6):
        choice = np.random.choice([0, 1], p=[0.5, 0.5])
        score += choice
    tot_score_fixed.append(score)

# Normal distribution around p = 0.5
tot_score_normal = []
p_values = []
for _ in range(N):
    score = 0
    for _ in range(6):
        p_withError = np.random.normal(loc=0.5, scale=0.05)
        p_withError = np.clip(p_withError, 0, 1)
        p_values.append(p_withError)
        choice = np.random.choice([0, 1], p=[1 - p_withError, p_withError])
        score += choice
    tot_score_normal.append(score)

# Prepare model data as a DataFrame
df_model_fixed = pd.DataFrame({
    "Condition": ["Model_Fixed"] * len(tot_score_fixed),
    "Light": ["Sim"] * len(tot_score_fixed),
    "Score": tot_score_fixed
})

df_model_normal = pd.DataFrame({
    "Condition": ["Model_Normal"] * len(tot_score_normal),
    "Light": ["Sim"] * len(tot_score_normal),
    "Score": tot_score_normal
})

# Combine both model datasets
df_model_combined = pd.concat([df_model_fixed, df_model_normal], ignore_index=True)


# Extract relevant columns from real data
df_real_subset = df_all[["odor_condition", "Condition", "Light", "Score"]].copy()

# Create combined condition + odor column for real data
df_real_subset["Condition_Odor"] = df_real_subset["odor_condition"] + "_" + df_real_subset["Condition"]

# For model data, assign combined column equal to Condition (Model_Fixed/Model_Normal)
df_model_combined["Condition_Odor"] = df_model_combined["Condition"]

# Combine real and model data
df_combined = pd.concat([df_real_subset, df_model_combined], ignore_index=True)

# Create a new column for combined Light groups
def combine_hl_ll(light):
    if light in ["HL", "LL"]:
        return "HL_LL"
    else:
        return light

df_combined["Light_Combined"] = df_combined["Light"].apply(combine_hl_ll)

# Update palette for combined hues
combined_palette = {
    "D": "grey",
    "HL_LL": "orange",  # Pick one color to represent both HL and LL combined
    "Sim": "lightblue"
}

# Update hue order
hue_order = ["D", "HL_LL", "Sim"]

# Plot with combined hues
plt.figure(figsize=(12, 6))

sns.boxplot(
    data=df_combined,
    x="Condition_Odor",
    y="Score",
    hue="Light_Combined",
    palette=combined_palette,
    hue_order=hue_order,
    medianprops=dict(color='black', linewidth=2)
)

plt.ylabel("Score")
plt.xlabel("Condition")
plt.title("Experimental and Model Score Comparison (HL and LL combined)")
plt.legend(title="Light / Simulation")

plt.tight_layout()
plt.savefig("Combined_Experimental_Model_Score_Combined_HL_LL.svg", format="svg",  transparent=True)
plt.show()

# %% import model and plot comparaison
# extract choice has one point to plot has/ next to Kenza figure 
# try with original concentration half of it with F + HL


#Boxplot of arrival times by condition and light

#Boxplot ofOdor choice times by condition and light

def define_custom_group(row):
    odor = row["odor_condition"]
    condition = row["Condition"]
    light = row["Light"]
    
    # Basic logic with odor_condition prefix
    if light == "D":
        return f"{odor}_{condition}_D"
    elif light in ["HL", "LL"]:
        return f"{odor}_{condition}_(HL+LL)"
    else:
        return f"{odor}_{condition}_Unknown"


def pad_to_six(lst):
    """Ensure list has exactly 6 elements (padding with np.nan or trimming as needed)."""
    if lst is None:
        return [np.nan] * 6
    lst = list(lst)
    if len(lst) < 6:
        lst.extend([np.nan] * (6 - len(lst)))
    elif len(lst) > 6:
        lst = lst[:6]
    return lst


custom_palette = {
    "F_D": "#6d6c6c",          # dark grey
    "H_D": "#bfbfbf",          # light grey
    "F_(HL+LL)": "#ff7700",   # orange1
    "H_(HL+LL)": "#fdca97",   # orange2 (lighter)
}

# Mapping from Group -> base fill color key
def base_group_from_group(group_name):
    # Remove odor prefix from group name: e.g. 'AIR_F_D' -> 'F_D'
    parts = group_name.split("_")
    # odor_condition is parts[0], rest is parts[1..]
    return "_".join(parts[1:])

# Outline colors by odor_condition
outline_colors = {
    "AIR": "black",
    "ETAC": "yellowgreen"
}

# Define line styles by odor_condition
line_styles = {
    "AIR": "--",     # dashed for AIR
    "ETAC": "-"      # solid for ETAC
}


#%%

# Apply custom group
df_all["Group"] = df_all.apply(define_custom_group, axis=1)

# Parse and pad lists as before
df_all["Arrival_Times_List"] = df_all["Arrival_Times"].apply(parse_successTT).apply(pad_to_six)
df_all["Odor_Choice_Times_List"] = df_all["Odor_Choice_Times"].apply(parse_successTT).apply(pad_to_six)

# Explode Arrival Times
arrival_cols = [f"Arrival_{i+1}" for i in range(6)]
df_all[arrival_cols] = pd.DataFrame(df_all["Arrival_Times_List"].tolist(), index=df_all.index)

df_arrival_melted = df_all.melt(id_vars=["Group"], value_vars=arrival_cols,
                                var_name="Position", value_name="Arrival_Time")
df_arrival_melted["Position"] = df_arrival_melted["Position"].str.extract("(\d+)").astype(int)

plt.figure(figsize=(10, 6))
ax = sns.boxplot(data=df_arrival_melted, 
                 palette={g: custom_palette[base_group_from_group(g)] for g in df_arrival_melted["Group"].unique()},
                 x="Position", y="Arrival_Time", hue="Group", medianprops=dict(color='black', linewidth=2))

#group_counts = df_arrival_melted.groupby(['Position', 'Group']).size().reset_index(name='count')

group_counts = df_arrival_melted.dropna(subset=['Arrival_Time']).groupby(['Position', 'Group']).size().reset_index(name='count')



# Get the unique positions and groups in the order they appear (no forced ordering)
positions = list(df_arrival_melted['Position'].unique())
groups = list(df_arrival_melted['Group'].unique())

n_groups = len(groups)
dodge_amount = 0.8  # default dodge width in seaborn

for _, row in group_counts.iterrows():
    pos = row['Position']
    grp = row['Group']
    count = row['count']

    xpos = positions.index(pos)
    grp_idx = groups.index(grp)

    offset = dodge_amount * (grp_idx - (n_groups - 1) / 2) / n_groups

    max_y = df_arrival_melted[
        (df_arrival_melted['Position'] == pos) & (df_arrival_melted['Group'] == grp)
    ]['Arrival_Time'].max()

    ax.text(
        xpos + offset,
        max_y + 10,
        f"n={count}",
        ha='center',
        va='bottom',
        fontsize=9,
        color='black',
    )

plt.xlabel("Position in Sequence")
plt.ylabel("Arrival Time")
plt.title("Arrival Times by Position (4 Custom Groups)")
plt.legend(title="Group")
plt.tight_layout()
plt.savefig("Arrival_Times_by_Position.svg", format="svg",  transparent=True)
plt.show()


#%%

# Extract and categorize odor condition
df_arrival_melted["odor_condition"] = df_arrival_melted["Group"].apply(lambda x: x.split("_")[0])
df_arrival_melted["odor_condition"] = pd.Categorical(df_arrival_melted["odor_condition"], categories=["AIR", "ETAC"], ordered=True)

# Plot mean lines without error bars
plt.figure(figsize=(10, 6))
sns.lineplot(
    data=df_arrival_melted,
    x="Position",
    y="Arrival_Time",
    hue="Group",
    style="odor_condition",
    style_order=["AIR", "ETAC"],
    dashes={"AIR": (4, 2), "ETAC": ""},  # AIR = dashed, ETAC = solid
    palette={g: custom_palette[base_group_from_group(g)] for g in df_arrival_melted["Group"].unique()},
    errorbar=None,  # No error bars
    markers=True
)

plt.xlabel("Position in Sequence")
plt.ylabel("Arrival Time (mean only)")
plt.title("Mean Arrival Time by Position (Dashed AIR, Solid ETAC)")
plt.legend(title="Group / Odor")
plt.tight_layout()
plt.savefig("Mean_Arrival_Times_No_Error_Bars.svg", format="svg",  transparent=True)
plt.show()


#%%
# Extract odor choice columns into new DataFrame columns
odor_cols = [f"OdorChoice_{i+1}" for i in range(6)]
df_all[odor_cols] = pd.DataFrame(df_all["Odor_Choice_Times_List"].tolist(), index=df_all.index)

# Melt into long format
df_odor_melted = df_all.melt(
    id_vars=["Group"],
    value_vars=odor_cols,
    var_name="Position",
    value_name="Odor_Choice_Time"
)

# Extract position index (1–6) as integer
df_odor_melted["Position"] = df_odor_melted["Position"].str.extract("(\d+)").astype(int)

# Build custom palette mapping full group names via base_group_from_group()
palette = {
    g: custom_palette.get(base_group_from_group(g), "#999999")
    for g in df_odor_melted["Group"].unique()
}

# Create the plot
plt.figure(figsize=(10, 6))
ax = sns.boxplot(
    data=df_odor_melted,
    x="Position",
    y="Odor_Choice_Time",
    hue="Group",
    palette=palette,
    medianprops=dict(color='black', linewidth=2)
)

# Count observations per group and position (excluding NaNs)
group_counts = (
    df_odor_melted
    .dropna(subset=['Odor_Choice_Time'])
    .groupby(['Position', 'Group'])
    .size()
    .reset_index(name='count')
)

# Determine label positions
positions = list(df_odor_melted["Position"].unique())
groups = list(df_odor_melted["Group"].unique())
n_groups = len(groups)
dodge_amount = 0.8  # Seaborn's default dodge width

# Add n= annotations
for _, row in group_counts.iterrows():
    pos = row['Position']
    grp = row['Group']
    count = row['count']

    xpos = positions.index(pos)
    grp_idx = groups.index(grp)
    offset = dodge_amount * (grp_idx - (n_groups - 1) / 2) / n_groups

    max_y = df_odor_melted[
        (df_odor_melted['Position'] == pos) & (df_odor_melted['Group'] == grp)
    ]['Odor_Choice_Time'].max()

    ax.text(
        xpos + offset,
        max_y + 10,  # vertical offset above boxplot
        f"n={count}",
        ha='center',
        va='bottom',
        fontsize=9,
        color='black',
    )

# Final plot formatting
plt.xlabel("Position in Sequence")
plt.ylabel("Odor Choice Time")
plt.title("Odor Choice Times by Position (4 Custom Groups)")
plt.legend(title="Group")
plt.tight_layout()
plt.savefig("Odor_Choice_Times_by_Position.svg", format="svg",  transparent=True)
plt.show()


#%%

# Extract odor condition from Group
df_odor_melted["odor_condition"] = df_odor_melted["Group"].apply(lambda x: x.split("_")[0])
df_odor_melted["odor_condition"] = pd.Categorical(df_odor_melted["odor_condition"], categories=["AIR", "ETAC"], ordered=True)

# Plot using lineplot (supports line styles, no error bars)
plt.figure(figsize=(10, 6))
sns.lineplot(
    data=df_odor_melted,
    x="Position",
    y="Odor_Choice_Time",
    hue="Group",
    style="odor_condition",
    style_order=["AIR", "ETAC"],
    dashes={"AIR": (4, 2), "ETAC": ""},
    palette={g: custom_palette[base_group_from_group(g)] for g in df_odor_melted["Group"].unique()},
    errorbar=None,  # No error bars
    markers=True
)

plt.xlabel("Position in Sequence")
plt.ylabel("Odor Choice Time (mean only)")
plt.title("Mean Odor Choice Time (Dashed AIR, Solid ETAC)")
plt.legend(title="Group / Odor")
plt.tight_layout()
plt.savefig("Mean_Odor_Choice_Times_No_Error_Bars.svg", format="svg",  transparent=True)
plt.show()



# %% diff 
# Compute difference between Odor Choice and Arrival Times (element-wise per row)
def compute_differences(row):
    arrival = np.array(row["Arrival_Times_List"], dtype=float)
    odor = np.array(row["Odor_Choice_Times_List"], dtype=float)
    return odor - arrival

df_all["OdorMinusArrival_List"] = df_all.apply(compute_differences, axis=1)

# Expand differences into separate columns
diff_cols = [f"OdorMinusArrival_{i+1}" for i in range(6)]
df_all[diff_cols] = pd.DataFrame(df_all["OdorMinusArrival_List"].tolist(), index=df_all.index)

# Melt long format for plotting
df_diff_melted = df_all.melt(
    id_vars=["Group"],
    value_vars=diff_cols,
    var_name="Position",
    value_name="OdorMinusArrival_Time"
)
df_diff_melted["Position"] = df_diff_melted["Position"].str.extract("(\d+)").astype(int)

# Generate palette using base group mapping
palette = {
    g: custom_palette.get(base_group_from_group(g), "#999999")
    for g in df_diff_melted["Group"].unique()
}

# Plot boxplot
plt.figure(figsize=(10, 6))
ax = sns.boxplot(
    data=df_diff_melted,
    x="Position",
    y="OdorMinusArrival_Time",
    hue="Group",
    palette=palette,
    medianprops=dict(color='black', linewidth=2)
)

# Count non-NaN values for annotation
group_counts = (
    df_diff_melted
    .dropna(subset=['OdorMinusArrival_Time'])
    .groupby(['Position', 'Group'])
    .size()
    .reset_index(name='count')
)

positions = list(df_diff_melted['Position'].unique())
groups = list(df_diff_melted['Group'].unique())
n_groups = len(groups)
dodge_amount = 0.8  # default seaborn dodge

# Add n= annotations
for _, row in group_counts.iterrows():
    pos = row['Position']
    grp = row['Group']
    count = row['count']

    xpos = positions.index(pos)
    grp_idx = groups.index(grp)
    offset = dodge_amount * (grp_idx - (n_groups - 1) / 2) / n_groups

    max_y = df_diff_melted[
        (df_diff_melted['Position'] == pos) & (df_diff_melted['Group'] == grp)
    ]['OdorMinusArrival_Time'].max()

    ax.text(
        xpos + offset,
        max_y + 10,
        f"n={count}",
        ha='center',
        va='bottom',
        fontsize=9,
        color='black',
    )

# Final plot touches
plt.xlabel("Position in Sequence")
plt.ylabel("Odor Choice Time − Arrival Time")
plt.title("Decision Time by Position (4 Custom Groups)")
# plt.axhline(0, color='black', linestyle='--', linewidth=0.8)  # Optional zero baseline
plt.legend(title="Group")
plt.tight_layout()
plt.savefig("Odor_Choice_Time_minus_Arrival_Time_by_Position.svg", format="svg",  transparent=True)
plt.show()

#%%

def compute_choice_intervals(odor_list):
    odor_array = np.array(odor_list, dtype=float)
    diffs = [odor_array[0]]  # from start (0) to first choice
    diffs.extend(np.diff(odor_array))  # differences between consecutive choices
    return diffs

df_all["Odor_Choice_Intervals"] = df_all["Odor_Choice_Times_List"].apply(compute_choice_intervals)

interval_cols = [f"Interval_{i+1}" for i in range(6)]
df_all[interval_cols] = pd.DataFrame(df_all["Odor_Choice_Intervals"].tolist(), index=df_all.index)


# Expand interval columns
interval_cols = [f"Interval_{i+1}" for i in range(6)]
df_all[interval_cols] = pd.DataFrame(df_all["Odor_Choice_Intervals"].tolist(), index=df_all.index)

# Melt for lineplot
df_intervals_melted = df_all.melt(
    id_vars=["Group"],
    value_vars=interval_cols,
    var_name="Interval",
    value_name="ChoiceInterval_Time"
)

# Extract numeric interval index for plotting
df_intervals_melted["Interval"] = df_intervals_melted["Interval"].str.extract("(\d+)").astype(int)
df_intervals_melted = df_intervals_melted.dropna(subset=["ChoiceInterval_Time"])

# Extract odor condition and set style
df_intervals_melted["odor_condition"] = df_intervals_melted["Group"].apply(lambda x: x.split("_")[0])
df_intervals_melted["odor_condition"] = pd.Categorical(
    df_intervals_melted["odor_condition"],
    categories=["AIR", "ETAC"],
    ordered=True
)

# Prepare palette mapping
palette = {
    g: custom_palette.get(base_group_from_group(g), "#999999")
    for g in df_intervals_melted["Group"].unique()
}

# Plot lineplot
plt.figure(figsize=(10, 6))
sns.lineplot(
    data=df_intervals_melted,
    x="Interval",
    y="ChoiceInterval_Time",
    hue="Group",
    style="odor_condition",
    style_order=["AIR", "ETAC"],
    dashes={"AIR": (4, 2), "ETAC": ""},
    palette=palette,
    errorbar=None,
    markers=True
)

plt.xlabel("Interval in Sequence (0→1, 1→2, ...)")
plt.ylabel("Time Interval (s)")
plt.title("Time Intervals Between Choices (Dashed AIR, Solid ETAC)")
plt.legend(title="Group / Odor")
plt.tight_layout()
plt.savefig("Time_Intervals_Between_Choices_by_Group_LinePlot.svg", format="svg",  transparent=True)
plt.show()


#%% time between each odor ?
# Compute intervals between odor choices (including first from start)
def compute_choice_intervals(odor_list):
    odor_array = np.array(odor_list, dtype=float)
    diffs = [odor_array[0]]  # from start (0) to first choice
    diffs.extend(np.diff(odor_array))  # differences between consecutive choices
    return diffs

df_all["Odor_Choice_Intervals"] = df_all["Odor_Choice_Times_List"].apply(compute_choice_intervals)

interval_cols = [f"Interval_{i+1}" for i in range(6)]
df_all[interval_cols] = pd.DataFrame(df_all["Odor_Choice_Intervals"].tolist(), index=df_all.index)

# Melt for plotting
df_intervals_melted = df_all.melt(
    id_vars=["Group"],
    value_vars=interval_cols,
    var_name="Interval",
    value_name="ChoiceInterval_Time"
)

# Extract numeric interval for ordering
df_intervals_melted["Interval"] = df_intervals_melted["Interval"].str.extract("(\d+)").astype(int)

# Generate palette like before
palette = {
    g: custom_palette.get(base_group_from_group(g), "#999999")
    for g in df_intervals_melted["Group"].unique()
}

plt.figure(figsize=(10, 6))
ax = sns.boxplot(
    data=df_intervals_melted,
    x="Interval",
    y="ChoiceInterval_Time",
    hue="Group",
    palette=palette,
    medianprops=dict(color='black', linewidth=2)
)

# Calculate counts for annotations
group_counts = (
    df_intervals_melted
    .dropna(subset=["ChoiceInterval_Time"])
    .groupby(["Interval", "Group"])
    .size()
    .reset_index(name="count")
)

positions = list(df_intervals_melted["Interval"].unique())
groups = list(df_intervals_melted["Group"].unique())
n_groups = len(groups)
dodge_amount = 0.8  # seaborn default dodge

# Add sample size annotations above boxes
for _, row in group_counts.iterrows():
    pos = row["Interval"]
    grp = row["Group"]
    count = row["count"]

    xpos = positions.index(pos)
    grp_idx = groups.index(grp)

    offset = dodge_amount * (grp_idx - (n_groups - 1) / 2) / n_groups

    max_y = df_intervals_melted[
        (df_intervals_melted["Interval"] == pos) & (df_intervals_melted["Group"] == grp)
    ]["ChoiceInterval_Time"].max()

    ax.text(
        xpos + offset,
        max_y + 10,  # Adjust vertical offset for clarity
        f"n={count}",
        ha="center",
        va="bottom",
        fontsize=9,
        color="black",
    )

plt.xlabel("Interval in Sequence (0→1, 1→2, ...)")
plt.ylabel("Time Interval (s)")
plt.title("Time Intervals Between Choices (Including First From Start)")
plt.legend(title="Group")
plt.tight_layout()

plt.savefig("Time_Intervals_Between_Choices_by_Group.svg", format="svg",  transparent=True)
plt.show()

#%%




# %%
from collections import Counter, defaultdict
import os
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from PIL import Image

# Assume button_coordinates dict is already defined here (your provided one)
# Example (partial):
button_coordinates = {
    "A0": {"top": 88, "left": 47}, "A1": {"top": 88, "left": 55},
    "B0": {"top": 75, "left": 39}, "B1": {"top": 75, "left": 47}, "B2": {"top": 75, "left": 55}, "B3": {"top": 75, "left": 63},
    "C0": {"top": 61, "left": 31}, "C1": {"top": 61, "left": 40}, "C2": {"top": 61, "left": 47}, "C3": {"top": 61, "left": 56}, "C4": {"top": 61, "left": 63}, "C5": {"top": 61, "left": 71},
    "D0": {"top": 48, "left": 24}, "D1": {"top": 48, "left": 32}, "D2": {"top": 48, "left": 40}, "D3": {"top": 48, "left": 47}, "D4": {"top": 48, "left": 55}, "D5": {"top": 48, "left": 63}, "D6": {"top": 48, "left": 71}, "D7": {"top": 48, "left": 79},
    "E0": {"top": 32, "left": 16}, "E1": {"top": 32, "left": 24}, "E2": {"top": 32, "left": 32}, "E3": {"top": 32, "left": 40}, "E4": {"top": 32, "left": 47}, "E5": {"top": 32, "left": 55}, "E6": {"top": 32, "left": 62}, "E7": {"top": 32, "left": 71}, "E8": {"top": 32, "left": 79}, "E9": {"top": 32, "left": 86},
    "F0": {"top": 19, "left": 8}, "F1": {"top": 19, "left": 16}, "F2": {"top": 19, "left": 23}, "F3": {"top": 19, "left": 31}, "F4": {"top": 19, "left": 40}, "F5": {"top": 19, "left": 48}, "F6": {"top": 19, "left": 55}, "F7": {"top": 19, "left": 63}, "F8": {"top": 19, "left": 71}, "F9": {"top": 19, "left": 78}, "F10": {"top": 19, "left": 86}, "F11": {"top": 19, "left": 94}
}

# Use your existing 'df_all' DataFrame loaded previously with columns including:
# 'odor_condition', 'Condition', 'Light', 'choice_row_last_Letter'
# Make sure choice_row_last_Letter is a list of strings (like ['A1', 'B2', ...])

# Step 1: Aggregate counts of each button label by odor_condition, condition, and light
counts_by_group = defaultdict(lambda: defaultdict(lambda: defaultdict(Counter)))
trial_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))

for idx, row in df_all.iterrows():
    odor = row['odor_condition']
    cond = row['Condition']
    light_raw = row['Light']
    if light_raw in ['LL', 'HL']:
        light = 'LL_HL'   # combined group name
    else:
        light = light_raw

    # Increment trial count for this group
    trial_counts[odor][cond][light] += 1

    # Some rows may have NaN or missing choice_row_last_Letter
    choice_letters = row.get('choice_row_last_Letter')
    if isinstance(choice_letters, list):
        # Clean out nan or 'nan' strings if any
        clean_choices = [str(x) for x in choice_letters if x not in [None, 'nan', 'NaN'] and not (isinstance(x, float) and np.isnan(x))]
    else:
        clean_choices = []

    counts_by_group[odor][cond][light].update(clean_choices)


# Step 2: Define plotting function
def plot_activation_counts_by_condition(image_path, counts_by_group, output_dir, trial_counts):
    """
    Plot activation counts of buttons for each condition group on an image background.
    Always shows all buttons. Highlights a subset in green for odor_condition == 'ETAC'.
    """

    img = Image.open(image_path)
    img_width, img_height = img.size

    os.makedirs(output_dir, exist_ok=True)
    cmap = plt.cm.Reds

    etac_highlight_buttons = {
        "A1", "B1", "B2", "C1", "C2", "C4", "D0", "D2", "D5", "D7",
        "E0", "E3", "E4", "E6", "E9", "F0", "F2", "F5", "F7", "F8", "F11"
    }

    for odor_condition, cond_dict in counts_by_group.items():
        for condition, light_dict in cond_dict.items():
            for light, counter in light_dict.items():
                full_counter = Counter({key: 0 for key in button_coordinates})
                full_counter.update(counter)  # Add actual counts

                fig, ax = plt.subplots(figsize=(10, 10))
                ax.imshow(img, alpha=0.5)
                ax.axis('off')

                max_count = max(full_counter.values()) if full_counter else 1
                norm = plt.Normalize(vmin=0, vmax=max_count)

                for button, coords in button_coordinates.items():
                    norm_top = coords["top"] / 100 * img_height
                    norm_left = coords["left"] / 100 * img_width
                    count = full_counter[button]

                    fill_color = cmap(norm(count))

                    if odor_condition == 'ETAC' and button in etac_highlight_buttons:
                        edge_color = 'green'
                        edge_width = 3
                    else:
                        edge_color = 'black'
                        edge_width = 1

                    ax.scatter(norm_left, norm_top, color=fill_color, s=700, edgecolor=edge_color, linewidth=edge_width)

                    if count > 0:
                        ax.text(norm_left, norm_top, str(count),
                                color="black", ha='center', va='center', fontsize=12, fontweight='bold')

                # Get number of trials for this group
                N = trial_counts.get(odor_condition, {}).get(condition, {}).get(light, 0)
                ax.text(0.05 * img_width, 0.05 * img_height, f'N = {N} trials',
                        color='black', fontsize=14, fontweight='bold',
                        bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', boxstyle='round,pad=0.3'))

                plt.title(f"Activation Counts: {odor_condition} {condition} {light}")

                sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
                sm.set_array([])
                cbar = plt.colorbar(sm, ax=ax)
                cbar.set_label('Activation Count')

                fname = f"Activation_{odor_condition}_{condition}_{light}.png"
                save_path = os.path.join(output_dir, fname)
                plt.savefig(save_path, bbox_inches='tight', dpi=300,  transparent=True)
                print(f"Saved plot for {odor_condition} {condition} {light} to {save_path}")


# Step 3: Call plot function with your image and output directory

# Provide path to your button map image
image_path = "IMG_5612_V2.jpg"



# Folder to save plots
output_dir = "activation_plots"
plot_activation_counts_by_condition(image_path, counts_by_group, output_dir, trial_counts)

# %%
