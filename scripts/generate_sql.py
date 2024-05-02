import json
import sys
import os

files = sys.argv[1:]

devices = {}
features = {}

# python3 ./scripts/generate_sql.py ./scripts/db/validation_sigs.json

for x in files:
    with open(x, 'r') as x:
        x = json.load(x)
        devices.update(x)
        for _, dev in x.items():
            features.update(dev)

features:'list[str]' = features.keys()
devices = devices.keys()

# print(features)

def device_name_map(dev_name:str):
    dev_name = dev_name.strip()
    map = {
        'iphone': 'iPhone',
        'ipad': 'iPad',
        'Xr': 'XR',
        'Xs': 'XS',
        '3Rd': '3rd',
    }
    dev_name = ' '.join([x.title() for x in dev_name.split(' ')])

    for k, v in map.items():
        dev_name = dev_name.replace(k.title(), v)

    return dev_name

def device_mapping():
    d_names = [device_name_map(d) for d in devices]

    s = '\n'.join(['\t'.join([str(ix + 1), x, x.split(' ')[0], o.lower().replace(' ', '_')]) for ix, (x, o) in enumerate(zip(d_names, devices))])
    return f"""CREATE TABLE device_map (
    id smallint primary key,
    device_name varchar(128),
    manufacturer varchar(128),
    clean_name varchar(128)
);
create unique index mapping_id on device_map(id);
COPY device_map (id, device_name, manufacturer, clean_name) FROM stdin;
{s}
\.
"""

def addi_features():
    additional_sql = []

    for f in features:
        f = f.replace(' ', '_').lower()
        additional_sql.append(f'{f}_match real[]')
        additional_sql.append(f'{f}_weight real[]')
    return ',\n    '.join(additional_sql)

def available_features():
    s = []

    for f in features:
        f = f.replace(' ', '_').lower()
        s.append(f"{f}")
    s = '\n'.join(s)
    return f"""CREATE TABLE available_features (
    feature_name varchar(256)
);
COPY available_features (feature_name) FROM stdin;
{s}
\.
"""

final_sql = f"""
{device_mapping()}

create TABLE site_map (
    id smallint primary key GENERATED ALWAYS AS IDENTITY,
    name character varying(256),
    lon numeric(12, 9),
    lat numeric(12, 9)
);

CREATE TABLE public.data (
    probe_id bigint primary key GENERATED ALWAYS AS IDENTITY,
    detected_on timestamp without time zone,
    device character varying(256),
    score real[],
    best_device smallint references device_map(id),
    site_id smallint references site_map(id),
    s_db real
);

CREATE TABLE score_breakdown (
    probe_id bigint references public.data(probe_id),
    is_match bool,
    feature character varying(256),
    values real[]
);

create unique index data_idx on public.data(probe_id);
create index detected_on_idx on public.data(detected_on);


{available_features()}
"""

# print(devices.keys(), len(devices))
print(final_sql)