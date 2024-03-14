import json
import numpy  

def get_db_keys(db):
    keys = set()
    for signature_name in db:
        temp_signature = db[signature_name]
        temp_keys = set(temp_signature.keys())
        keys = keys.union(temp_keys)
    
    keys = list(keys)
    return keys

def create_stats(db,keys):
    stats = {}
    for attr in keys:
        counter = {'null':0}
    
        attr_counter = []
        for signature_name in db:
            temp_signature = db[signature_name]
            if attr in temp_signature:
                attr_counter.append(temp_signature[attr])
            else:
                counter['null'] += 1
        for item in attr_counter:
            if item and isinstance(item[0],list):
                for i in item:
                    if str(i) in counter.keys():
                         counter[str(i)] += 1
                    else:
                        counter[str(i)] = 1
            if item and not isinstance(item[0],list):
                if str(item) in counter.keys():
                    counter[str(item)] += 1
                else:
                    counter[str(item)] = 1

        for key in counter:
            counter[key] = counter[key] / len(db)
        stats[attr] = counter
    
    return stats 

# def create_stats(db,keys):
#     stats = {}
#     for attr in keys:
#         counter = {'null':0}

#         attr_counter = []
#         for signature_name in db:
#             temp_signature = db[signature_name]
#             if attr in temp_signature:
#                 attr_counter.append(temp_signature[attr])
#             else:
#                 counter['null'] += 1
        
#         for item in attr_counter:
#             if str(item) in counter.keys():
#                 counter[str(item)] += 1
#             else:
#                 counter[str(item)] = 1

#         for key in counter:
#             counter[key] = counter[key] / len(db)
#         stats[attr] = counter
    
#     return stats

def calculate_attr_stats(files):
    if isinstance(files,list):
        json_object = []
        for json_file in files:
            with open(json_file, "r") as f:
                json_object.append(json.load(f))

        database = {}
        for sig in json_object:
            for key in sig:
                database[key] = sig[key]

    if isinstance(files,str):
        with open(files ,'r') as input_file:
            database = json.load(input_file)
        
    keys = get_db_keys(database)
    stats = create_stats(database,keys)

    return stats
    
    
