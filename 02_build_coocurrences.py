import glob
import os
import json
import re
import tqdm
import pickle
import pandas as pd
import arguments as args

files = glob.glob(os.path.join(args.scopes_dir, '*.scopes.json'))
os.makedirs(args.cooc_dir, exist_ok=True)

def str_normalize(value):
    return re.sub(r'\s+', ' ', value).lower()

def get_item_string_by_coveredtext(scope, item):
    p = item['properties']
    begin, end = p['begin'], p['end']
    return str_normalize(scope['text'][begin:end])

def get_item_string(scope, item, prop):
    return item['properties'][prop] if prop else get_item_string_by_coveredtext(scope, item)

cooccurences = {}
for file in tqdm.tqdm(files):
    file_id = os.path.basename(file).split('.')[0]
    with open(file, encoding='utf-8') as f:
        data = json.load(f)
    scopes = [d for d in data if d['type'] == args.scope_type]
    for scope_id, scope in enumerate(scopes):
        if args.event_type and not any([a for a in scope.get('sub', []) if a['type'] == args.event_type]):
            continue
        items = sorted([a for a in scope.get('sub', []) if a['type'] == args.item_type], key=lambda a: a['properties']['begin'])
        cooccurences_ = set()
        for i in range(len(items) - 1):
            for j in range(i + 1, len(items)):
                cooc = tuple(get_item_string(scope, items[i_], args.item_property) for i_ in [i, j])
                cooccurences_.add(cooc)
        for cooc in cooccurences_:
            cooccurences.setdefault(cooc, []).append((file_id, scope_id))

# save coocurrences with scopes ids
with open(os.path.join(args.cooc_dir, 'coocurences.scope_ids.pkl'), mode='wb') as f:
    pickle.dump(cooccurences, f)

# build dataframe
processed = set()
data = []
for a, b in cooccurences:
    if (b, a) not in processed:
        forward_count = len(cooccurences[(a, b)])
        backward_count = len(cooccurences.get((b, a), []))
        total_count = forward_count + backward_count
        ratio = forward_count / total_count
        data.append((a, b, forward_count, backward_count, total_count, ratio))
        processed.add((a, b))

df = pd.DataFrame(data, columns=['item_left', 'item_right', 'forward_count', 'backward_count', 'total_count', 'ratio'])

df.to_csv(os.path.join(args.cooc_dir, 'coocurrences.csv'))
