"""This script aims to download raw data 'MAJNUM.csv' from ARCEP"""

from pathlib import Path
from datetime import datetime

import requests
from loguru import logger

from data_pipeline import DownloadError
from decorators import timed


@timed("Download")
def download_to_local(url: str, output_dir: str, filename: str) -> Path:
    """
    Download from the URL and save it to a directory.

    The function tries to download from a specified URL and save the content into a directory.

    Args:
        url (str): The URL where to file is located.
        output_dir (str): The location of the directory.
        filename (str): The name of the file.

    Returns:
        Path: Path of the file in his directory.
    """

    outdir = Path(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    if filename is None:
        filename = Path(url).name

    timestamp = datetime.now().strftime("%Y%m%d")
    filaname_timed = f"{Path(filename).stem}{timestamp}{Path(filename).suffix}"
    outpath = outdir / filaname_timed

    try:
        r = requests.get(url, timeout=60)
        r.raise_for_status()
        outpath.write_bytes(r.content)
    except Exception as e:
        raise DownloadError(f"Couldn't download from {url}") from e

    logger.info(f"Download {filename} at {outpath} ({outpath.stat().st_size} bytes)")

    return outpath
