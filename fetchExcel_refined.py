import csv
import ast
import re
import os

'''
Used in main.py to get information on the experiment before doing the analysis part.
'''

def FethExcel(data_path, f_path):
    file_path = f'{data_path}{f_path}'
    for csvs in os.listdir(file_path):
        if csvs.endswith(".csv"):
            csv_name =  csvs




    # We start by extracting the date and the experiment ID from the folder name
    # Pattern: capture (1) the part before the date (experiment_id), and (2) the date
    
    pattern = r"([A-Za-z0-9\-]+)_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})"

    match = re.search(pattern, file_path)

    if match:
        experiment_id = match.group(1)
        print("Experiment ID:", experiment_id)
        date_input = match.group(2)
        print("Date extracted:", date_input)
    else:
        print("Pattern not found")
   
   
   
   
    # We then read the first line of the CSV to get the parameters of the experiment
    
    csv_file_path = f'{file_path}/{csv_name}'
    # Reading the CSV file
    with open(csv_file_path, mode='r') as file:
        reader = csv.reader(file)
        row = next(reader)  # Read only the first line
            # Parse the row as a dictionary
        camera_info = ast.literal_eval(row[0])
        tracking_info = ast.literal_eval(row[1])
        test_info = ast.literal_eval(row[2])
        light_info = ast.literal_eval(row[3])
        odors_info = ast.literal_eval(row[4])
        # Assign data to respective dictionary based on keys found
        camera_par = camera_info
        tracking_par = tracking_info
        exp_protocol = test_info
        light_info = light_info
        odor = odors_info
    return camera_par, tracking_par, exp_protocol, light_info, odor, date_input, experiment_id