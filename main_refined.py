from experiment_class_refined import Experiment 
import os
import fetchExcel_refined as fetch

'''
The part from 'first_path' to 'last_path' will be useful once we have a lot of different experiments that need to be classified into many
subfolders. To do a mock run (for example to try a new tracking method), create a Data_test with one experiment file and Results_test, then
all the Data and Results in experiment.py and main.py.
'''

data_path = 'Data/'
results_path = 'Results_refined/'
i = 0

for file_path in os.listdir(data_path):
    print(f'{data_path}{file_path}')
    camera_par, tracking_par, exp_protocol, red_light, odor, date_input, genotype = fetch.FethExcel(data_path, file_path)
    video_path = f'{data_path}{file_path}/Video/Video.avi'
    first_path = str(odor['Odor1'] + '_' + odor['Concentration1'] + '_' + odor['Odor2'] + '_' +odor['Concentration2'] + '_' 
		+ red_light['Light'] + '_' + red_light['Intensity'] + '_' + red_light['Duration'])
    pairing = str(f"{odor['Pairing']}_{odor['Passage']}")
    last_path = str(date_input + '_' + odor['Passage'] + '_' + genotype)
    full_path = (f'{results_path}{first_path}/{genotype}/{pairing}/{last_path}/')
    print(f'full path: {full_path}')
    # Build the two paths we care about
    raw_csv     = os.path.join(results_path, f"{file_path}_raw.csv")
    draw_folder = os.path.join(results_path, f"{file_path}_draw")

    if os.path.isfile(raw_csv) or os.path.isdir(draw_folder):
        print(f"Experiment {file_path} already processed. Skipping...")
        continue


    print(f"Processing file {file_path}...")
    My_experiment = Experiment(date_input, genotype, red_light, camera_par, tracking_par, odor, video_path, file_path)
    My_experiment.training(exp_protocol)
    






