import json
import os
from typing import Dict, List

TAGS_FILE = os.path.join(os.path.dirname(__file__), 'posthub_tags.json')


def load_tags() -> Dict[str, List[str]]:
    try:
        with open(TAGS_FILE, 'r') as fh:
            return json.load(fh)
    except Exception:
        return {}


def save_tags(tags: Dict[str, List[str]]) -> bool:
    try:
        with open(TAGS_FILE, 'w') as fh:
            json.dump(tags, fh, indent=2)
        return True
    except Exception:
        return False


def update_tags_for_file(path: str, tags: List[str]) -> None:
    data = load_tags()
    data[path] = tags
    save_tags(data)


def get_tags_for_file(path: str) -> List[str]:
    return load_tags().get(path, [])
