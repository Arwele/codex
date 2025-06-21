import json
import os
import shutil
from typing import Dict, List

from .hash_utils import file_hash

CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'posthub_config.json')


def load_config() -> Dict:
    try:
        with open(CONFIG_FILE, 'r') as fh:
            return json.load(fh)
    except Exception:
        return {}


def save_config(data: Dict) -> None:
    with open(CONFIG_FILE, 'w') as fh:
        json.dump(data, fh, indent=2)


def get_sync_folder() -> str:
    return load_config().get('sync_folder', '')


def set_sync_folder(path: str) -> None:
    cfg = load_config()
    cfg['sync_folder'] = path
    save_config(cfg)


def file_status(path: str) -> str:
    sync_folder = get_sync_folder()
    if not sync_folder:
        return 'NoSync'
    remote = os.path.join(sync_folder, os.path.basename(path))
    if not os.path.isfile(remote):
        return 'Missing'
    local_hash = file_hash(path)
    remote_hash = file_hash(remote)
    if local_hash == remote_hash:
        return 'Synced'
    if os.path.getmtime(path) > os.path.getmtime(remote):
        return 'Modified'
    if os.path.getmtime(remote) > os.path.getmtime(path):
        return 'Conflict'
    return 'Unknown'


def sync_file(path: str) -> str:
    sync_folder = get_sync_folder()
    if not sync_folder:
        return 'NoSync'
    os.makedirs(sync_folder, exist_ok=True)
    remote = os.path.join(sync_folder, os.path.basename(path))
    local_hash = file_hash(path)
    remote_hash = file_hash(remote) if os.path.isfile(remote) else None
    if remote_hash == local_hash:
        return 'Synced'
    if remote_hash is None or os.path.getmtime(path) >= os.path.getmtime(remote):
        shutil.copy2(path, remote)
        return 'UpdatedRemote'
    if os.path.getmtime(remote) > os.path.getmtime(path):
        shutil.copy2(remote, path + '_conflict')
        return 'Conflict'
    return 'Unknown'


def sync_all(files: List[str]) -> Dict[str, str]:
    results = {}
    sync_folder = get_sync_folder()
    if not sync_folder:
        for f in files:
            results[f] = 'NoSync'
        return results
    for f in files:
        results[f] = sync_file(f)
    return results
