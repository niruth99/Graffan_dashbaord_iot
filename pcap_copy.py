import shutil
import time
import os
import random

# Randomly selects a pcap file to copy to dest

# Specify the folder path
folder_path = '/path/to/folder'
dest_path = '/path/to/dest'

# List all files in the folder

# Copy the file

files = os.listdir(folder_path)
i = 0

while True:
    f = random.randint(len(files))
    f = files[f]
    source_file = os.path.join(folder_path, f)
    dest_name = os.path.join(dest_path, f'{i}.pcap')
    shutil.copy(source_file, dest_name)
    i += 1
    time.sleep(3)
