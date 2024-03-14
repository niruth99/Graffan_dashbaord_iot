import time

import pandas as pd
from SQLInterface import SQLInterface
import random

import environ
import os
import iotsignature as iots
import attr_stats

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

def match_wp(ver_sig:iots.Signature,
             ver_sig_wt:iots.Signature,
             test_sig:iots.Signature,
             lambda_:float = 2.1,
             key_match:str = 'union'
             ) -> dict:
    """
        (
            {
                'feature': (match, weight)   
            },
            `score`
        )
    """
    return ver_sig.match_wp(
    test_sig,
    lambda_ = lambda_,
    key_match = key_match,
    signatures_wt = ver_sig_wt,
    expand = True
)

def clean_str(s):
    return s.lower().replace(' ','_')

class ResultSorter:
    def __init__(self):
        self.order: dict[iots.SignatureBase: 'list[int]'] = {}

    def add_base(self, sig_base:iots.SignatureBase, order_df:pd.DataFrame):
        order = []
        order_dict = {name:id for id, name in zip(order_df['id'], order_df['device_name'])}
        for sig in sig_base.signatures:
            name = clean_str(sig.name)
            order.append(order_dict[name])
        self.order[sig_base] = order

    def sorter(self, sig_base:iots.SignatureBase):
        return self.order[sig_base]

def predict_sort(ver_base:iots.SignatureBase, exp_sig:iots.Signature, sorter: ResultSorter, features:'list[str]') -> dict:
    """
        Predicts `exp_sig` against all signatures in `ver_base` and orders them according to sorter
        gives dictionary with keys features, values list of floats
    """
    results = {'score': []}
    for f in features:
        results[f'{f}_match'] = []
        results[f'{f}_weight'] = []
    best_score, best_device = 0, 0

    for ix, ver_sig, ver_sig_wt in zip(range(len(ver_base.signatures)), ver_base.signatures, ver_base.signatures_wp):
        breakdown, score = match_wp(ver_sig, ver_sig_wt, test_sig = exp_sig)
        for f in features:
            m, w = None, None
            if f in breakdown:
                m, w = breakdown[f]
            results[f'{f}_match'].append(m)
            results[f'{f}_weight'].append(w)
        results['score'].append(score)
        if best_score < score:
            best_score = score
            best_device = ix
    

    order = sorter.sorter(ver_base)
    # print(order)

    for k, v in results.items():
        results[k] = [v[ind] for ind in order]

    results['best_device'] = order[best_device]
    
    return results


def real_fake_data():
    sql = SQLInterface()

    order_df = sql.execute_pd('select * from device_map order by id')
    features = sql.execute_pd('select * from available_features')['feature_name'].to_list()

    data_max = sql.execute_pd('select max(probe_id) from data;')
    print(f'Starting from ind: {data_max}')
    if data_max['max'][0] is None:
        ind = 0
    else:
        ind = data_max['max'][0] + 1

    files = [
        './db/validation_sigs.json',
        './db/filterd_weighted_sig.json',
        './db/signed_db_pcap.json',
        './db/signed_data.json'
    ] # can ignre signed_db_pcap.json

    stats = attr_stats.calculate_attr_stats(files)
    verification_base = iots.SignatureBase(stats, path = r'./db/validation_sigs.json', path2=r'./db/validation_sigs_weighted.json')
    verification_base.load()

    exp_base = iots.SignatureBase(stats, path = './db/signed_data.json')
    exp_base.load()

    sorter = ResultSorter()
    sorter.add_base(verification_base, order_df)

    # for index, signature in enumerate(exp_base.signatures):
    #     predictons = verification_base.predict(signature, probability_occ=True,verbose=True)
    while True:
        res = []
        k = random.randint(0, n_devices)
        probes = random.choices(exp_base.signatures, k = k)
        print(k, probes)
        for p in probes:
            r = predict_sort(verification_base, p, sorter, features)
            r['device'] = p.name
            r['probe_id'] = ind
            r['detected_on'] = time.time()
            res.append(r)
            ind += 1
        if k > 0:
            df = pd.DataFrame(res)
            print(res)
            print(df)
            df['detected_on'] = pd.to_datetime(df['detected_on'], unit='s')
            sql.insert_pd(df, 'data')
        time.sleep(1)


if __name__ == '__main__':
    real_fake_data()