import os
import time
import shutil

folders = [
    '/home/g/Desktop/tshark_data_capture/09-34-41',
    '/home/g/Desktop/tshark_data_capture/09-23-59'
]       

files = []

for f in folders:
    for file in os.listdir(f):
        if file.endswith('pcap'):
            files.append(os.path.join(f, file))

ind = 0
while True:
    os.listdir
    for x in files:
        print(x)
        shutil.copy(x, f'./wild_data/09-23-59/{ind}.pcap')
        time.sleep(1)
        ind += 1
    # time.sleep(5)
