import threading
import subprocess
import time
import os
import random
import argparse
from datetime import datetime
import shutil


def list_of_strings(arg):
    return arg.split(',')

argument_parser = argparse.ArgumentParser(description="Packet sniffer")
argument_parser.add_argument('-i', '--iface', type=list_of_strings, required=False, help="Interfaces to use. default=wlan1,wlan2,wlan3")
argument_parser.add_argument('-f', '--file', type=str, required=False, help="Filter captured packets (only capture probe request). default= capture all")
argument_parser.add_argument('-a', '--duration', type=int, required=False, default=300, help="capture time in seconds. default=300 (5 minutes)")

args = argument_parser.parse_args()

IFACE_list = args.iface or ["wlan1", "wlan2", "wlan3"]
folder_location = args.file or os.getcwd()
CAPTURE_TIME = args.duration or 300  

print('Packet capture time: {} seconds'.format(CAPTURE_TIME))

terminate = False
data_log = []

def change_mode(mode, iface):
    if mode == "monitor":
        print("[+] Changing {} interface to monitor mode".format(iface))
        subprocess.call(f"sudo airmon-ng start {iface}", shell=True)
        print("[++] Successfully changed {} to monitor mode".format(iface))
    elif mode == "managed":
        print("[+] Changing {} interface to managed mode".format(iface))
        subprocess.call(f"sudo airmon-ng stop {iface}mon", shell=True)
        print("[+] Successfully changed {} to managed mode".format(iface))


def channel_hopper(iface):
    all_channels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
    num_interfaces = len(IFACE_list)
    channels_per_interface = len(all_channels) // num_interfaces
    channel_seq = []

    if num_interfaces == 1:
        channel_seq = all_channels
    else:
        interface_index = IFACE_list.index(iface)
        start_channel = interface_index * channels_per_interface
        end_channel = start_channel + channels_per_interface
        if interface_index == num_interfaces - 1:
            channel_seq = all_channels[start_channel:]
        else:
            channel_seq = all_channels[start_channel:end_channel]

    while not terminate:
        for c in channel_seq:
            subprocess.call(f"iwconfig {iface}mon channel {c}", shell=True)
            print(f'[+] {iface} Collecting data on channel -> {c}')
            time.sleep(2)
            if terminate:
                break

def sniff_packets(iface):
    global data_log

    hopper_thread = threading.Thread(target=channel_hopper, args=(iface,))
    hopper_thread.start()

    t1 = datetime.now()
    counter = 0

    while not terminate:
        random_sequence = ''.join(map(str, random.sample(range(1, 1000), k=4)))

        filename = os.path.join(folder_location, f"{iface}_capture_{counter}.pcap")
        command = f"tshark -i {iface}mon -a duration:2 -w {filename} -f 'type mgt subtype probe-req'"

       
        try:
            subprocess.run(command, shell=True)
            print(f'[+] Packet capture complete for {iface}. File: {filename}')

            os.chmod(filename, 0o777)  
            print(f'[+] Changed permissions for {filename} to 777')
            shutil.copy(filename, f'/home/ragnar/dashboard_tech_summit/wild_data/demo/{f"{iface}_capture_{counter}.pcap"}')



            t2 = datetime.now()
            data_log.append((str(t1), str(t2)))

        except subprocess.CalledProcessError as e:
            print(f"Error capturing packets on {iface}: {e}")

        counter += 1
        time.sleep(1)  

    hopper_thread.join()

def main():
    global terminate
    global folder_location

    folder_location = os.path.join(folder_location, datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(folder_location, exist_ok=True)
    os.chmod(folder_location, 0o777)


    print('[+] Writing data to {}'.format(folder_location))
    print('[+] Interfaces in use {}'.format(IFACE_list))

    for iface in IFACE_list:
        change_mode('monitor', iface)

    try:
        sniffing_threads = []
        for iface in IFACE_list:
            sniffing_thread = threading.Thread(target=sniff_packets, args=(iface,))
            sniffing_threads.append(sniffing_thread)
            sniffing_thread.start()

        for thread in sniffing_threads:
            thread.join()

    except KeyboardInterrupt:
        print("\n[!] Termination command detected!!!")
        print('[!] Terminating packet capture')

        terminate = True

        print("[+] Writing LOG file to {}".format(folder_location))
        with open(os.path.join(folder_location, "data_log.txt"), 'w') as log_file:
            for entry in data_log:
                log_file.write(f"{entry[0]} - {entry[1]}\n")

        for iface in IFACE_list:
            change_mode('managed', iface)

if __name__ == "__main__":
    main()
