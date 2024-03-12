import time

import pandas as pd
import environ
from SQLInterface import SQLInterface
import random

n_devices = 2

devices = [f'Device {x}' for x in range(n_devices)]
max_count_per_device = 7

def main():
    sql = SQLInterface()
    data_max = sql.execute_pd('select max(probe_id) from data;')
    print(data_max.shape, len(data_max))
    print(data_max)
    if data_max['max'][0] is None:
        ind = 0
    else:
        ind = data_max['max'][0] + 1

    while True:
        counts = [random.randint(0, max_count_per_device) for x in range(n_devices)]
        inds = list(range(ind, ind + sum(counts)))

        df_dev_name = []

        for d, c in zip(devices, counts):
            df_dev_name += [d]*c

        # times = [time.time() - random.random() for x in range(sum(counts))]
        times = [time.time() for x in range(sum(counts))]

        df = pd.DataFrame({'device':df_dev_name, 'detected_on':times, 'probe_id': inds})
        df['detected_on'] = pd.to_datetime(df['detected_on'], unit='s')
        # print(df.to_dict('split'))
        
        sql.insert_pd(df, 'data')

        ind += sum(counts)

        time.sleep(1)

def summary():
    sql = SQLInterface()
    while True:
        counts = [random.randint(0, max_count_per_device) for x in range(n_devices)]

        # times = [time.time() - random.random() for x in range(sum(counts))]
        times = [time.time() for x in range(n_devices)]

        df = pd.DataFrame({'device':devices, 'detected_on':times, 'count': counts})
        df['detected_on'] = pd.to_datetime(df['detected_on'], unit='s')
        # print(df.to_dict('split'))
        
        sql.insert_pd(df, 'timeseries')

        time.sleep(1)

if __name__ == '__main__':
    main()