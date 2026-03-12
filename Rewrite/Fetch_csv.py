'''
Docstring for Réécriture.Fetch_excel
Ce code a pour but d'obtenir toutes les informations nécessaires sur une expérience
Les informations doivent être contenues dans un fichier csv.
- Odeurs utilisées et dans quelles chambres
- Si les chambres sont rejetées ou non

Pour l'instant aucun fichier csv n'a été mis en place
'''

import pandas as pd
from pathlib import Path

def fetch_excel(excel_path):

    excel_path = Path(excel_path)

    df = pd.read_excel(excel_path, header=None)

    experiments = {}

    i = 0
    while i < len(df):

        # Détection du début d'un bloc
        if str(df.iloc[i,0]) == "Date":

            date = str(df.iloc[i+1,0])
            exp_id = str(df.iloc[i+1,1])

            exp_key = f"{date}_Exp{exp_id}"
            experiments[exp_key] = {}

            # header des Mazes
            header_row = i + 4
            headers = df.iloc[header_row]

            Mazes = headers[2:].dropna().tolist()

            # chambres
            for ch in range(3):

                row = df.iloc[header_row + 1 + ch]

                chamber_id = row[0]

                for lab, odor in zip(Mazes, row[2:]):
                    if lab not in experiments[exp_key]:
                        experiments[exp_key][lab] = {}

                    experiments[exp_key][lab][f"Chambre_{chamber_id}"] = odor

            # rejected
            rejected_row = df.iloc[header_row + 4]

            for lab, val in zip(Mazes, rejected_row[2:]):
                experiments[exp_key][lab] = experiments[exp_key].get(lab, {})
                experiments[exp_key][lab]["rejected"] = str(val).lower() == "yes"

            # start
            start_row = df.iloc[header_row + 5]

            for lab, val in zip(Mazes, start_row[2:]):
                experiments[exp_key][lab]["start"] = int(val)

        i += 1

    return experiments

info = fetch_excel("C:/Users/julie/Downloads/Fichier_excel.xlsx")

print(info["10032026_Exp1"]["A_top"])