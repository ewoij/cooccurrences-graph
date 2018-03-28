import os
import pickle
import pandas as pd
import json
import tqdm
import glob
import shutil
import networkx as nx
import arguments as args

cooc_file = os.path.join(args.cooc_dir, 'coocurrences.selected.csv')
cooc_scopeids_file = os.path.join(args.cooc_dir, 'coocurences.scope_ids.pkl')

# read cooc + scope ids
df = pd.read_csv(cooc_file, index_col=0)
df = df[df.selected]
cooc_scopeids = pd.read_pickle(cooc_scopeids_file)
cooc_scopeids = {k: cooc_scopeids[k] for k in zip(df.item_left, df.item_right)}

def format_annotation(annotation, item_type, event_type):
    types = {
        item_type: 'item',
        event_type: 'event'
    }
    return {
        'begin': annotation['properties']['begin'],
        'end': annotation['properties']['end'],
        'type': types[annotation['type']]
    }

def format_scope(scope, item_type, event_type):
    return {
        'text': scope['text'],
        'annotations': [format_annotation(i, item_type, event_type) for i in scope['sub'] if i['type'] in [item_type, event_type]]
    }

def create_data_scopes(scopes_dir, cooc_scopeids, item_type, event_type):
    doc_id_to_scopes = {}
    for doc_id, scope_id in [i for l in cooc_scopeids.values() for i in l]:
        doc_id_to_scopes.setdefault(doc_id, []).append(scope_id)
    data = {}
    for doc_id, scope_ids in tqdm.tqdm(doc_id_to_scopes.items()):
        scopes_file = os.path.join(scopes_dir, '{}.scopes.json'.format(doc_id))
        with open(scopes_file, encoding='utf-8') as f:
            scopes = json.load(f)
        data[doc_id] = {i: format_scope(scopes[i], item_type, event_type) for i in scope_ids}
    return data

def save_data_js_file(dir_, suffix, varname, data):
    os.makedirs(dir_, exist_ok=True)
    file = os.path.join(dir_, 'data_{}.js'.format(suffix))
    with open(file, encoding='utf-8', mode='w') as f:
        f.write('var {} = '.format(varname))
        json.dump(data, f)
        f.write(';')

def create_data_documents_metadata(scopes_dir, document_ids):
    data = {}
    for doc_id in document_ids:
        metadata_file = os.path.join(scopes_dir, '{}.metadatas.json'.format(doc_id))
        with open(metadata_file, encoding='utf-8') as f:
            j = json.load(f)
        data[doc_id] = {'file_name': j['original_file_name']}
    return data

def create_data_graph(cooc_scopeids):
    graph = nx.DiGraph()
    for a, b in cooc_scopeids.keys():
        graph.add_edge(a, b)
    pos = nx.drawing.layout.fruchterman_reingold_layout(graph, scale=1.1, iterations=200)
    node_ids = {n: i for i, n in enumerate(graph.nodes())}
    return {
        'edges': [{
            'id': i,
            'source': node_ids[source],
            'target': node_ids[target],
            'scope_ids': [[doc_id, str(scope_id)] for doc_id, scope_id in cooc_scopeids[(source, target)]]
        } for i, (source, target) in enumerate(graph.edges())],
        'nodes': [{
            'id': node_ids[n],
            'label': n,
            'x': pos[n][0],
            'y': pos[n][1]
        } for n in graph.nodes()]
    }

def create_data_scopes_file():
    data = create_data_scopes(args.scopes_dir, cooc_scopeids, args.item_type, args.event_type)
    save_data_js_file(args.graph_dir, 'scopes', 'scopes', data)


def create_data_documents_metadata_file():
    document_ids = set(doc_id for l in cooc_scopeids.values() for doc_id, _ in l)
    data = create_data_documents_metadata(args.scopes_dir, document_ids)
    save_data_js_file(args.graph_dir, 'doc_metadatas', 'docMetadatas', data)

def create_data_graph_file():
    data = create_data_graph(cooc_scopeids)
    save_data_js_file(args.graph_dir, 'graph', 'graph', data)

def copy_template_files():
    template_files = [os.path.join(d, f) for d, dl, fl in os.walk(args.graph_template_dir) for f in fl]
    for f in template_files:
        shutil.copy2(f, args.graph_dir)
