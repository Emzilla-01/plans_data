import json
import tarfile

import requests
from pymongo.errors import DuplicateKeyError
import os
from os import environ as env
import env_secret
from db_conf import db
from data_conf import data_url_md5_dict

################################################################################

def download_file(itm):
    local_filename = local_filename = itm[1].get('url').split('/')[-1]
    with requests.get(itm[1].get("url"), stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=2**12):
                f.write(chunk)
    return local_filename

################################################################################

def setup_data(db, data_url_md5_dict):
    db_results=list()
    for itm in data_url_md5_dict.items():
        data_url_md5_dict[itm[0]].setdefault("archive", download_file(itm))
        with tarfile.open(data_url_md5_dict[itm[0]].get("archive")) as t_f:      
            data_url_md5_dict[itm[0]].setdefault("archive_fns", t_f.getnames())
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(t_f, ".")
        for unpacked_fn in data_url_md5_dict.get(itm[0]).get("archive_fns"):
            with open(unpacked_fn, "rt") as json_file:
                json_list = list(json_file)
            for json_str in json_list:
                doc = json.loads(json_str)
                try:
                    db_results.append(db[str(itm[0])].insert_one(doc))
                except DuplicateKeyError as e:
                    print(f'{itm[1].get("unique_ix")}: {doc.get(itm[1].get("unique_ix"))} already in db.{itm[0]}')

    assert all([r.acknowledged for r in db_results])
    return(data_url_md5_dict, db_results)
################################################################################

def setup_ixs(db, data_url_md5_dict):
    db_ix_results=list()
    for k in data_url_md5_dict:
        unique_field = data_url_md5_dict.get(k).get("unique_ix")
        db_ix_results.append(db[k].create_index([(unique_field, 1)], unique=True)) # ascending by given id

################################################################################

def teardown(db, data_url_md5_dict):
    print("tearing down local files")
    #local teardown
    rm_calls = list()
    db_calls = list()
    for itm in data_url_md5_dict.items():
        rm_tps = (itm[1].get("archive"), *itm[1].get("archive_fns"))
        print(rm_tps)
        for fn in rm_tps:
            try:
                rm_calls.append(os.remove(fn))
            except Exception as e:
                rm_calls.append(e)
        # db teardown
        print("tearing down db colls")
        # db_calls.append(db[itm[0]].delete_many({}))
        db_calls.append(db[itm[0]].drop())
    return (rm_calls, db_calls)


################################################################################

if __name__ == "__main__":
    data_url_md5_dict, db_results = setup_data(db, data_url_md5_dict)
    db_ixs_results = setup_ixs(db, data_url_md5_dict)
    print(f"docs in db.users: {db.users.count_documents({})}")
    print(f"docs in db.plans: {db.plans.count_documents({})}")
    # teardown(db, data_url_md5_dict)