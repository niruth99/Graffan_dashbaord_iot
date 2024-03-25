import sys
import traceback
import scapy.all as sc
import os

import argparse
import time
from generate_data import _init, predict_signatures
from multiprocessing import Pipe, Pool, Process, connection
from iotsignature import Signature

def ignore(*args, **kwargs):
    pass

print = ignore

def work(pipe:connection.Connection):
    i = _init()
    sql = i['sql']
    verification_base = i['verification_base']
    sorter = i['sorter']
    features = i['features']

    while True:
        try:
            signatures = pipe.recv()
            
            predict_signatures(
                sql,
                verification_base,
                signatures, 
                sorter,
                features,
            )
        except:
            traceback.print_exc()
        # sys.stdout.flush()

def read_pcap(folder:str) -> list[Signature]:
    # onlyfiles = [os.path.join(folder, f) for f in os.listdir(folder) if os.path.isfile(f)]
    signature_list = []

    onlyfiles = [folder]

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

    print("Init pipes")
    for x in range(threads):
        r, w = Pipe()
        read_pipes.append(r)
        write_pipes.append(w)
    print('Pipes inited')

    processes = [Process(target = work, args = [p]) for p in read_pipes]
    print('Created all processes')
    [p.start() for p in processes]
    print('All processes started')
    # with Pool(threads) as pool:
    #     pool.map(work, read_pipes)
    print('Finished loading')
    read_files = set()
    while True:
        print(f'start while {time.time() - last_read:.4f}')

        unread = [os.path.join(folder, f) for f in os.listdir(folder)]
        x = []

        print(f'iterate files {time.time() - last_read:.4f}')

        for u in unread:
            for f in os.listdir(u):
                print(f)
                if f.endswith('pcap'):
                    x.append(os.path.join(u, f))
        print(f'end_iterate {time.time() - last_read:.4f}')


        res = []

        for f in x:
            if f in read_files: continue
            read_files.add(f)
            print(f)

            r = read_pcap(f)
            print(f'{len(r)=} {time.time() - last_read:.4f}')
            
            res.extend(r)
            os.remove(f)
        print(f'end read pcap {time.time() - last_read:.4f}')
        
        # Split into threads
        for x in range(threads):
            wp = write_pipes[x]
            wp.send(res[x::threads])
        print(f'send pipes {time.time() - last_read:.4f}')
        
        last_read = time.time()
        print(interval-(time.time() - last_read), time.time()-last_read)
        sys.stdout.flush()
        time.sleep(interval-(time.time() - last_read))
    
    # while True:
    #     unread = [os.path.join(folder, f) for f in os.listdir(folder)]
    #     x = []

    #     for u in unread:
    #         for f in os.listdir(u):
    #             print(f)
    #             if f.endswith('pcap'):
    #                 x.append(os.path.join(u, f))

    #     res = []

    #     for f in x:
    #         print(f)
    #         res.extend(read_pcap(f))
    #         os.remove(f)
        
    #     i = _init()
    #     sql = i['sql']
    #     verification_base = i['verification_base']
    #     sorter = i['sorter']
    #     features = i['features']

    #     predict_signatures(
    #         sql,
    #         verification_base,
    #         res, 
    #         sorter,
    #         features,
    #     )
    #     # Split into threads
    #     # for x in range(threads):
    #     #     wp = write_pipes[x]
    #     #     wp.put(res[x::threads])
        
    #     last_read = time.time()
    #     time.sleep(interval-(time.time() - last_read))


if __name__ == '__main__':
    argument_parser = argparse.ArgumentParser(description="Read live data from specific folder")
    argument_parser.add_argument('-s', '--source', type=str, required=True ,help="Source folder")
    argument_parser.add_argument('-i', '--interval',type=float, required=False ,help="How often to read source folder", default = 1)
    argument_parser.add_argument('-t', '--threads',type=float, required=False ,help="Number of threads", default = 10)

    args = argument_parser.parse_args()
    main(args.source, args.interval, args.threads)