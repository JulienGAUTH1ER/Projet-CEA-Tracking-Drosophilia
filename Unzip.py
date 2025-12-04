import zipfile
import os

'''
This code was made by Timothé Petitjean, it could be useful but I don't think it is used right now.
'''

def unzip_file(Raw_Data_path, Data_path, data):
    # Check if the file exists and is a zip file
    zip_path = f'{Raw_Data_path}{data}'
    output_path = f'{Data_path}{data}'
    if not zip_path.endswith('.zip'):
        print("Provided file is not a zip file.")
        return

    if not os.path.exists(zip_path):
        print("The file does not exist.")
        return
    
    # Define the directory where to extract
    directory_to_extract_to = os.path.splitext(output_path)[0]
    
    # Create the directory if it does not exist
    if  os.path.exists(directory_to_extract_to):
        print(f'{data} ALREADY EXTRACTED')
        return

    os.makedirs(directory_to_extract_to)
    print(f'EXTRACTION OF {data}...')
    # Create a ZipFile object
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extract all the contents into the directory
        zip_ref.extractall(directory_to_extract_to)
        print("Files extracted to:", directory_to_extract_to)

# Usage example
Raw_Data_path = 'Raw/'
Data_path = 'Data/'

#zip_file_path = f'Data/2024-04-20_15-08@EmptySSplit'  # Specify the path to your zip file
for data in os.listdir(Raw_Data_path):
    unzip_file(f'{Raw_Data_path}',f'{Data_path}', f'{data}')

