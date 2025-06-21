import hashlib
from typing import Optional


def file_hash(path: str) -> Optional[str]:
    """Return SHA256 hash of a file."""
    try:
        with open(path, 'rb') as fh:
            sha = hashlib.sha256()
            for block in iter(lambda: fh.read(65536), b''):
                sha.update(block)
        return sha.hexdigest()
    except Exception:
        return None


def compare_hash(file1: str, file2: str) -> bool:
    """Compare hashes of two files."""
    h1 = file_hash(file1)
    h2 = file_hash(file2)
    return h1 is not None and h1 == h2
