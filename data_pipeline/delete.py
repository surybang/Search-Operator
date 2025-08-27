from pathlib import Path


def delete_local_file(path: Path) -> bool:
    """Delete local file. Returns True if deleted, False if missing."""
    try:
        path.unlink()
        return True
    except FileNotFoundError:
        return False
