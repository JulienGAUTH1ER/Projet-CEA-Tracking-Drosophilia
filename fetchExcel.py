import csv
import ast
import re
import os
import shutil

'''
Used in main.py to get information on the experiment before doing the analysis part.
'''

def FethExcel(data_path, f_path):
    #file_path = f'{data_path}/{name_path}'
    file_path = f'{data_path}{f_path}'
    for csvs in os.listdir(file_path):
        if csvs.endswith(".csv"):
            csv_name =  csvs

    # Pattern: capture (1) the part before the date (experiment_id), and (2) the date
    pattern = r"([A-Za-z0-9\-]+)_(\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2})"

    match = re.search(pattern, file_path)

    if match:
        experiment_id = match.group(1)
        date_input = match.group(2)
        print("Experiment ID:", experiment_id)
        print("Date extracted:", date_input)
    else:
        print("Pattern not found")

    # if match:
    #     experiment_id = match.group(1)
    #     date_input = match.group(2)

    # else:
    #     date_input = None
    #     experiment_id = None

   

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
        #if experiment_id == 'EmptysSplit':
            #experiment_id = 'EmptySSplit'
        #experiment_id = 'EmptySSplit'
        #Exp_ID = str(odors_info['Odor1'] + '_' + odors_info['Concentration1'] + '_' + odors_info['Odor2'] + '_' +odors_info['Concentration2'] + '_' 
		    #+ light_info['Light'] + '_' + light_info['Intensity'] + '_' + light_info['Duration'] + '_' + odors_info['Pairing'] +  '_' 
		    #+ odors_info['Passage'] + '_' + experiment_id + '_' + date_input) #+ '_' + str(odors_info['Seed'])
    #os.rename(f'{file_path}/{name_path}__raw.csv',f'{file_path}/{Exp_ID}__raw.csv')
    #os.rename(f'{file_path}/{name_path}__draw',f'{file_path}/{Exp_ID}__draw')
    #os.rename(f'{file_path}/{name_path}__Video',f'{file_path}/{Exp_ID}__Video')
    #os.rename(f'{file_path}',f'{data_path}{Exp_ID}')
    return camera_par, tracking_par, exp_protocol, light_info, odor, date_input, experiment_id


'''
i = 0
data_path = 'Data/'
for file_path in os.listdir(data_path):
    i+=1
    FethExcel(data_path,file_path)
    #.make_archive(f'Data/{file_path}','zip',f'{data_path}{file_path}')
'''