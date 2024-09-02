import os

# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# List of folders to create
folders = ['detect', 'output_folder', 'recut', 'stitch', 'video']

# Create folders if they don't exist
for folder in folders:
    folder_path = os.path.join(current_directory, folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)