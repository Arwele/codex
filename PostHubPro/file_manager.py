import os
from typing import List, Dict


def posts_folder() -> str:
    """Return default Fusion 360 posts folder or current directory."""
    default = os.path.expanduser('~/Autodesk/Fusion 360/CAM/Posts')
    return default if os.path.isdir(default) else os.getcwd()


def list_cps_files() -> List[Dict[str, str]]:
    """Return metadata for .cps files."""
    folder = posts_folder()
    files = []
    try:
        for name in os.listdir(folder):
            if name.lower().endswith('.cps'):
                path = os.path.join(folder, name)
                meta = {
                    'path': path,
                    'name': name,
                    'modified': os.path.getmtime(path)
                }
                files.append(meta)
    except Exception:
        pass
    return files
