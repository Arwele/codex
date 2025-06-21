import os
import shutil
from datetime import datetime
from typing import Optional


def history_folder(base_path: str) -> str:
    folder = os.path.join(os.path.dirname(base_path), 'history')
    os.makedirs(folder, exist_ok=True)
    return folder


def backup_file(path: str) -> Optional[str]:
    try:
        folder = history_folder(path)
        stamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        target = os.path.join(folder, f"{os.path.basename(path)}_{stamp}")
        shutil.copy2(path, target)
        return target
    except Exception:
        return None


def restore_latest(path: str) -> bool:
    try:
        folder = history_folder(path)
        backups = [f for f in os.listdir(folder) if f.startswith(os.path.basename(path))]
        if not backups:
            return False
        latest = max(backups)
        src = os.path.join(folder, latest)
        shutil.copy2(src, path)
        return True
    except Exception:
        return False
