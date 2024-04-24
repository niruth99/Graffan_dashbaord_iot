import sys
import traceback
import pandas as pd
import scapy.all as sc
import os

import argparse
import time
from generate_data import _init, predict_signatures
from multiprocessing import Pipe, Pool, Process, Queue, connection
from iotsignature import Signature
from SQLInterface import SQLInterface

def ignore(*args, **kwargs):
    pass

# print = ignore

def work(unread_queue:Queue, read_queue:Queue, site_id:int):
    i = _init()
    sql = i['sql']
    verification_base = i['verification_base']
    sorter = i['sorter']
    features = i['features']

    while True:
        try:
            unread:list[str] = unread_queue.get()
            for u in unread:
                signatures = read_pcap(u)
            
                predict_signatures(
                    sql,
                    verification_base,
                    signatures, 
                    sorter,
                    features,
                    site_id
                )
                read_queue.put(u)
        except:
            traceback.print_exc()
        # sys.stdout.flush()

def read_pcap(folder:str) -> 'list[Signature]':
    # onlyfiles = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(f)]
    signature_list = []

    onlyfiles = [folder]

    for f in onlyfiles:
        cap = sc.rdpcap(f)
        for frame in cap:
            if (frame.haslayer(sc.Dot11Elt) and frame[sc.Dot11Elt].ID == 0 and frame[sc.Dot11Elt].info == b''):
                mac = frame.addr2
                signature = Signature(name = mac)
                signing_status = signature.sign(frame)
                # Add signal strength
                signature.strength = frame.dBm_AntSignal
                if signing_status:
                    signature_list.append(signature)
    return signature_list

def main(folder:str, interval:float, threads:float, lon:float, lat:float, sitename):
    last_read = time.time()
    
    unread_queue = Queue()
    read_queue = Queue()

    sql = SQLInterface()
    acc = 0.000001 # Equal to x decimal points, 5dp -> ~1m error
    r = sql.execute_pd(f'select * from site_map where abs(lon - {lon}) < {acc} and abs(lat - {lat}) < {acc}')
    rows, _ = r.shape
    if rows == 0:
        print('Not found in site_map, creating new site')
        df = pd.DataFrame([{'lon':lon, 'lat':lat}])
        r = sql.insert_return_id(df, 'site_map', returning='id')
        if sitename == None:
            sitename = f'Site {r[0]}'
        sql.execute(f'update site_map set name = \'{sitename}\' where id = {r[0]}')
        print(f'Create new site: id = {r[0]} ({sitename})')
    else:
        print(f'Reusing siteid: {r["id"][0]}, {r["name"][0]}')
        r = r['id']
    sql.commit()
    sql.close()

    site_id = r[0]

    processes = [Process(target = work, args = [unread_queue, read_queue, site_id]) for p in range(threads)]
    [p.start() for p in processes]
    # with Pool(threads) as pool:
    #     pool.map(work, read_pipes)
    read_files = set()
    while True:

        unread = []
        
        # Iterate through folder to find pcaps
        for sub_f in os.listdir(folder):
            sub_f = os.path.join(folder, sub_f)
            # for sub_sub_f in os.listdir(sub_f):
            #     sub_sub_f = os.path.join(sub_f, sub_sub_f)
            for file in os.listdir(sub_f):
                file = os.path.join(sub_f, file)
                if file.endswith('pcap') and (file not in read_files):
                    unread.append(file)
                    read_files.add(file)
        
        # Evenly spread load to threads
        # for x in range(threads):
        #     unread_queue.put(unread[x::threads])

        # One pcap file per loop
        for u in unread:
            print(u)
            unread_queue.put([u])
        
        while not read_queue.empty():
            r = read_queue.get_nowait()
            read_files.add(r)
            os.remove(r)

        for ix, p in enumerate(processes):
            if not p.is_alive():
                processes[ix] = Process(target = work, args = [unread_queue, read_queue])
        
        last_read = time.time()
        sys.stdout.flush()
        time.sleep(interval-(time.time() - last_read))


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(description="Read live data from specific folder")
    argument_parser.add_argument('-s', '--source', type=str, required=True ,help="Source folder")
    argument_parser.add_argument('-i', '--interval',type=float, required=False ,help="How often to read source folder", default = 0.1)
    argument_parser.add_argument('-t', '--threads',type=float, required=False ,help="Number of threads", default = os.cpu_count() - 1)
    argument_parser.add_argument('-lon', '--longitude',type=float, required=False ,help="Latitude of site", default = 0)
    argument_parser.add_argument('-lat', '--latitude',type=float, required=False ,help="Longitude of site", default = 0)
    argument_parser.add_argument('-n', '--sitename',type=float, required=False ,help="Name of site", default = None)


    args = argument_parser.parse_args()
    main(args.source, args.interval, args.threads, args.longitude, args.latitude, args.sitename)