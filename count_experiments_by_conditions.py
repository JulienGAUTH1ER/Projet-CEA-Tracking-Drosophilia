import os
import itertools
import pandas as pd

def count_experiments_by_conditions(root_dir, output_excel="experiment_counts.xlsx"):
    """
    Counts experiment folders by:
      • Odor type: EtAc vs AIR (from the first token of the name)
      • Light mode: Dark, Low Light, High Light
      • Maze type: Half, Full
    Outputs an Excel with columns:
      Odor_Type | Light | Chamber_Size | Count
    """
    # 1) Define your condition sets
    odor_types   = ["EtAc", "AIR"]
    light_modes  = ["D", "LL", "HL"]
    chamber_sizs = ["H", "F"]

    # human‐readable maps
    odor_labels = {"EtAc": "1 odor: EtAc", "AIR": "no odor"}
    light_labels = {"D": "Dark", "LL": "Low Light", "HL": "High Light"}
    chamber_labels = {"H": "Half", "F": "Full"}

    # 2) All combos
    combos = list(itertools.product(odor_types, light_modes, chamber_sizs))

    # 3) List subdirectories
    entries = [e for e in os.scandir(root_dir) if e.is_dir()]

    records = []
    for od, lt, ch in combos:
        count = 0
        for entry in entries:
            name = entry.name
            # prefix
            prefix = name.split("_", 1)[0]
            if prefix.lower() != od.lower():
                continue
            # tokens
            tokens = [t.upper() for t in name.split("_")]
            if lt.upper() in tokens and ch.upper() in tokens:
                count += 1

        records.append([
            odor_labels[od],
            light_labels[lt],
            chamber_labels[ch],
            count
        ])

    # 4) Build DataFrame
    df = pd.DataFrame(
        records,
        columns=["Odor_Type", "Light", "Chamber_Size", "Count"]
    )

    # 5) Save to Excel
    df.to_excel(output_excel, index=False)
    print(f"Saved experiment counts to {output_excel}")
    return df

# Example usage:
if __name__ == "__main__":
    summary_df = count_experiments_by_conditions("Data", output_excel="counts_by_conditions.xlsx")
