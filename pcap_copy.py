import shutil
import time
import os
import random

# Specify the folder path
folder_path = '/path/to/folder'

# List all files in the folder

# Copy the file

files = os.listdir(folder_path)
i = 0

while True:
    f = random.randint(len(files))
    f = files[f]
    source_file = os.path.join(folder_path, f)
    shutil.copy(source_file, f'{i}.pcap')
    i += 1
    time.sleep(3)
