from generate_data import predict_sort, ResultSorter
from SQLInterface import SQLInterface
import attr_stats
import iotsignature as iots
import environ
import pandas as pd

if __name__ == '__main__':
    sql = SQLInterface()

    # Grab device map to ensure that results array are in correct order
    order_df = pd.read_csv('../q1.csv')
    # Grab available features for easier iteration, even when feature is not present in probe
    features = pd.read_csv('../q2.csv')['feature_name'].to_list()
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
    exp_sig = exp_base.signatures[0]
    for exp_sig in exp_base.signatures:
        r = predict_sort(verification_base, exp_sig, sorter, features)
    print(r)
    