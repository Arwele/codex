import json
import os
import zipfile
from typing import List

from .tag_manager import load_tags, save_tags


def export_zip(files: List[str], zip_path: str) -> bool:
    try:
        with zipfile.ZipFile(zip_path, 'w') as zf:
            tags = load_tags()
            for path in files:
                if os.path.isfile(path):
                    zf.write(path, os.path.basename(path))
                    hist = os.path.join(os.path.dirname(path), 'history')
                    if os.path.isdir(hist):
                        for h in os.listdir(hist):
                            if h.startswith(os.path.basename(path)):
                                zf.write(os.path.join(hist, h), os.path.join('history', h))
            zf.writestr('tags.json', json.dumps(tags))
        return True
    except Exception:
        return False


def import_zip(zip_path: str, dest: str) -> bool:
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(dest)
            data = json.loads(zf.read('tags.json').decode('utf-8'))
        tags = load_tags()
        tags.update(data)
        save_tags(tags)
        return True
    except Exception:
        return False
