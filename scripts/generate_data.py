import time

import pandas as pd
from SQLInterface import SQLInterface
import random

import environ
import os
import iotsignature as iots
import attr_stats

n_devices = 10

devices = [f'Device {x}' for x in range(n_devices)]
max_count_per_device = 7

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
        order_dict = {name:id for id, name in zip(order_df['id'], order_df['clean_name'])}
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

def float_close(f1, f2, d = 0.0001):
    return (f1 - f2) < d 

def proccess_upload(sql:SQLInterface, df:pd.DataFrame, features:'list[str]'):
    """
        Given a dataframe of results and list of features,
        upload dataframe to SQL server
    """
    data_features = [
        'detected_on',
        'device',
        'score',
        'best_device',
        'site_id',
        's_db'
    ]
    rows, cols = df.shape
    data_features = df[data_features]
    # sql.insert_pd(data_features, 'data')

    # dt = df['detected_on'][0].isoformat()

    probe_ids = sql.insert_return_id(data_features, 'data').to_list()
    # print(probe_id_df)

    # probe_ids = []
    # n_scores = len(df['score'][0])
    # counted = [False for x in range(rows)]

    # for x in range(rows):
    #     for y in range(rows):
    #         if counted[y]: continue
    #         for z in range(n_scores):
    #             if not float_close(df['score'][x][z], probe_id_df['score'][y][z]):
    #                 break
    #         if z == (n_scores - 1):
    #             probe_ids.append(probe_id_df['probe_id'][y])
    #             counted[y] = True
    #             break
            

    # probe_ids = df['probe_id'].to_list()

    score_breakdown = ['probe_id']
    [score_breakdown.extend([f'{f}_weight', f'{f}_match']) for f in features]
    print(probe_ids)

    d = {
        'probe_id': [],
        'is_match': [],
        'feature': [],
        'values': [],
    }
    for feat in features:
        d['probe_id'] += probe_ids
        d['is_match'] += [True]*rows
        d['feature'] += [feat]*rows
        d['values'] += df[f'{feat}_match'].to_list()

        d['probe_id'] += probe_ids
        d['is_match'] += [False]*rows
        d['feature'] += [feat]*rows
        d['values'] += df[f'{feat}_weight'].to_list()
    
    df = pd.DataFrame(d)
    sql.insert_pd(df, 'score_breakdown')

def predict_signatures(sql:SQLInterface,
                       ver_base:iots.SignatureBase,
                       probes:'list[iots.Signature]',
                       sorter: ResultSorter,
                       features:'list[str]',
                       site_id:int
                       ) -> int:
    """
        Key function to predict then commit results to db
        See `real_fake_data()` for `sorter`, `sql`, and `features` init
    """
    res = []
    t = time.time()
    for p in probes:
        r = predict_sort(ver_base, p, sorter, features)
        r['device'] = p.name
        r['detected_on'] = t
        r['s_db'] = p.strength
        r['site_id'] = site_id
        res.append(r)
    if len(res) > 0:
        df = pd.DataFrame(res)
        df['detected_on'] = pd.to_datetime(df['detected_on'], unit='s')
        proccess_upload(sql, df, features)
    return

def _init():
    sql = SQLInterface()

    # Grab device map to ensure that results array are in correct order
    order_df = sql.execute_pd('select * from device_map order by id')
    # Grab available features for easier iteration, even when feature is not present in probe
    features = sql.execute_pd('select * from available_features')['feature_name'].to_list()
    # Get highest unused probe_id
    data_max = sql.execute_pd('select max(probe_id) from data;')

    files = [
        './db/validation_sigs.json',
        './db/filterd_weighted_sig.json',
        './db/signed_db_pcap.json',
        './db/signed_data.json'
    ] # can ignre signed_db_pcap.json

    stats = attr_stats.calculate_attr_stats(files)
    verification_base = iots.SignatureBase(stats, path = r'./db/validation_sigs.json', path2=r'./db/validation_sigs_weighted.json')
    verification_base.load()

    sorter = ResultSorter()
    sorter.add_base(verification_base, order_df)

    res = {
        'sql':sql,
        'verification_base': verification_base,
        'sorter': sorter,
        'features': features
    }

    return res


def real_fake_data():
    """
        Randomly sample from signed_data.json
    """
    sql = SQLInterface()

    # Grab device map to ensure that results array are in correct order
    order_df = sql.execute_pd('select * from device_map order by id')
    # Grab available features for easier iteration, even when feature is not present in probe
    features = sql.execute_pd('select * from available_features')['feature_name'].to_list()
    # Get highest unused probe_id
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

    while True:
        k = random.randint(0, n_devices)
        probes = random.choices(exp_base.signatures, k = k)
        predict_signatures(sql, verification_base, probes, sorter, features)
        # time.sleep(1)


if __name__ == '__main__':
    real_fake_data()