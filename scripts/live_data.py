import os

import argparse
import time
from generate_data import _init, predict_signatures
from multiprocessing import Pipe, Pool, connection
from iotsignature import Signature
import scapy as sc

def work(pipe:connection.Connection):
    i = _init()
    sql = i['sql']
    verification_base = i['verification_base']
    sorter = i['sorter']
    feature = i['feature']

    while True:
        json = pipe.recv()
        signatures = []

        for k, v in json.keys():
            sig = Signature(**v)
            sig.name = k
        
        predict_signatures(
            sql,
            verification_base,
            signatures, 
            sorter,
            feature,
        )

def read_pcap(folder:str) -> list[Signature]:
    onlyfiles = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(f)]
    signature_list = []

    for f in onlyfiles:
        cap = sc.rdpcap(f)
        for index, frame in enumerate(cap):
            if (frame.haslayer(sc.Dot11Elt) and frame[sc.Dot11Elt].ID == 0 and frame[sc.Dot11Elt].info == b''):
                mac = frame.addr2
                signature = Signature(name = mac)
                signing_status = signature.sign(frame)
                if signing_status:
                    signature_list.append(signature)
    return signature_list

def main(folder:str, interval:float, threads:float):
    last_read = time.time()
    write_pipes, read_pipes = [], []

    for x in threads:
        r, w = Pipe()
        read_pipes.append(r)
        write_pipes.append(w)

    with Pool(threads) as pool:
        pool.map(work, read_pipes)
        while True:
            unread = os.listdir(folder)

            res = []

            for f in unread:
                res.extend(read_pcap(f))
            
            # Split into threads
            for x in range(threads):
                wp = write_pipes[x]
                wp.put(res[x::threads])
            
            last_read = time.time()
            time.sleep(interval-(time.time() - last_read))


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(description="Read live data from specific folder")
    argument_parser.add_argument('-s', '--source', type=str, required=True ,help="Source folder")
    argument_parser.add_argument('-i', '--interval',type=float, required=False ,help="How often to read source folder", default = 5)
    argument_parser.add_argument('-t', '--threads',type=float, required=False ,help="Number of threads", default = 1)

    args = argument_parser.parse_args()
    main(args.source, args.interval, args.threads)