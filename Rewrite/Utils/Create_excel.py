'''
Ce script convertit les fichiers JSON de tracking en fichiers Excel.
Il traite tous les fichiers *_tracking.json présents dans les sous-dossiers de Data/*/Video/Mazes/.
'''



import json
import pandas as pd
from pathlib import Path
import os


def json_to_excel(json_path):
    json_path = Path(json_path)

    with open(json_path, "r") as f:
        data = json.load(f)

    tracking = data.get("tracking", [])

    if not tracking:
        print(f"Aucune donnée : {json_path}")
        return

    # ===== DATAFRAME PRINCIPAL =====
    df = pd.DataFrame(tracking)

    # Extraire x / y depuis position
    df["x"] = df["position"].apply(lambda p: p["x"] if p else None)
    df["y"] = df["position"].apply(lambda p: p["y"] if p else None)

    df = df.drop(columns=["position"])

    # Réorganiser colonnes (plus propre)
    df = df[[
        "frame",
        "time_sec",
        "detected",
        "x",
        "y",
        "distance_px",
        "speed_px_per_sec"
    ]]

    # ===== METADATA =====
    metadata = {
        "fps": data.get("fps"),
        **data.get("parameters_python", {})
    }

    df_meta = pd.DataFrame(list(metadata.items()), columns=["parameter", "value"])

    # ===== SAUVEGARDE =====
    output_path = json_path.with_suffix(".xlsx")

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="tracking", index=False)
        df_meta.to_excel(writer, sheet_name="metadata", index=False)

    print(f"✔ Excel créé : {output_path}")


def process_folder(folder_path):
    folder = Path(folder_path)

    for json_file in folder.rglob("*_tracking.json"):
        json_to_excel(json_file)






if __name__ == "__main__":
    project_root = Path(".").resolve()
    data_dir = project_root / "Data"

    if not data_dir.exists():
        raise FileNotFoundError(f"Dossier introuvable : {data_dir}")

    for experiment_folder in data_dir.iterdir():
        maz_dir = experiment_folder / "Video" / "Mazes"
        if maz_dir.exists():
            process_folder(maz_dir)