"""This script aims to delete a local file"""

from pathlib import Path

from decorators import timed


@timed("Delete file")
def delete_local_file(path: Path) -> bool:
    """Delete local file. Returns True if deleted, False if missing."""
    try:
        path.unlink()
        return True
    except FileNotFoundError:
        return False
