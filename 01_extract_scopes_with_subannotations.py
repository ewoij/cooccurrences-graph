import logging
import time
import glob
import pickle
import tqdm
import os
import json
import xmihelper
import multiprocessing
import uuid
import arguments as args

os.makedirs('logs', exist_ok=True)
logging.basicConfig(level=logging.WARN, handlers=[
    logging.StreamHandler(),
    logging.FileHandler(filename=os.path.join('logs', '_'.join([time.strftime('%Y%m%d-%H%M'), 'extract_scopes_with_subannotations', multiprocessing.current_process().name]) + '.log'))
])

def save_as_json(dir_, file_name, suffix, data):
    os.makedirs(dir_, exist_ok = True)
    file_name = '.'.join([file_name, suffix, 'json'])
    with open(os.path.join(dir_, file_name), mode='w', encoding='utf-8') as f:
        json.dump(data, f)

def work(file_):
    try:
        types = {type_: {'name': name} for type_, name  in [args.scope_annotation] + args.sub_annotations}
        x = xmihelper.Xmi(file_)
        annos = x.get_annotations(types)
        scope_annos = annos[args.scope_annotation[1]]
        sub_annos = [a for _, name in args.sub_annotations for a in annos[name]]
        xmihelper.add_sub(scope_annos, sub_annos)
        xmihelper.make_sub_pos_relative(scope_annos)
        xmihelper.add_text(scope_annos, x)
        output_file_name = str(uuid.uuid4())
        save_as_json(args.scopes_dir, output_file_name, 'scopes', scope_annos)
        save_as_json(args.scopes_dir, output_file_name, 'metadatas', {'original_file_name': file_})
    except:
        logging.exception(f'Failed to process {file_}')

def get_files_recursive(xmi_dir, extension):
    return [os.path.join(d, f) for d, _, fl in os.walk(xmi_dir) for f in fl if os.path.splitext(f)[1].lower() == extension]

if __name__ == '__main__':
    p = multiprocessing.Pool()
    files = get_files_recursive(args.xmi_dir, '.xmi')
    res = list(tqdm.tqdm(p.imap_unordered(work, files), total=len(files)))
