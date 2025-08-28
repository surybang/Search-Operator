from datetime import datetime
from pathlib import Path
import hashlib

from loguru import logger
import s3fs

from data_pipeline.exceptions import UploadError
from decorators import timed


def file_hash(path: Path) -> str:
    """Compute hash of a local file."""

    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def s3_file_hash(fs: s3fs.S3FileSystem, s3_uri: str) -> str:
    """Compute hash of a remote file in s3"""

    h = hashlib.md5()
    with fs.open(s3_uri, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def get_latest_remote_file(
        fs: s3fs.S3FileSystem,
        remote_path: str,
        stem: str = "MAJNUM"
        ) -> str | None:
    """
    Retrieve the latest file in MinIO matching a naming pattern.

    The function looks for objects under the given remote path with names of the form
    `{stem}_YYYYMMDD.csv`. It returns the lexicographically greatest match, which corresponds
    to the most recent file if the date is encoded as YYYYMMDD in the filename.

    Args:
        fs (s3fs.S3FileSystem): Initialized S3/MinIO filesystem.
        remote_path (str): Base S3 path (e.g. "s3://arcep/raw").
        stem (str): File stem (e.g. "MAJNUM").

    Returns:
        str | None: The S3 URI of the most recent file or None if no match is found.
    """

    pattern = f"{remote_path.rstrip('/')}/{stem}_*.csv"
    matches = fs.glob(pattern)
    return max(matches) if matches else None


@timed("Upload if new")
def upload_if_new(
        fs: s3fs.S3FileSystem,
        bucket: str,
        key: str,
        local_path: Path,
        stem: str = "MAJNUM"
        ) -> bool:
    """
    Upload a local file to MinIO only if its content differs from the last version stored.

    The function computes the MD5 hash of the local file, retrieves the most recent file
    in the given bucket/prefix (based on the stem and timestamp in the filename),
    and compares their hashes. If the content is identical, the upload is skipped.
    Otherwise, the file is uploaded under a new name suffixed with the current date.

    Args:
        fs (s3fs.S3FileSystem): An initialized s3fs filesystem connected to MinIO.
        bucket (str): The target bucket name (e.g., "s3://arcep").
        key (str): The prefix (directory) inside the bucket where the file will be stored.
        local_path (Path): Path to the local file to check and potentially upload.
        stem (str, optional): Base name used for the uploaded file. Defaults to "MAJNUM".

    Returns:
        bool:
            - True if a new file was uploaded.
            - False if the latest remote file already had identical content.
    """

    try:
        remote_path = f"{bucket}{key}"
        logger.info(f"Remote path : {bucket}{key}")

        last_uri = get_latest_remote_file(fs, remote_path, stem)
        logger.info(f"Last_uri: {last_uri}")

        local_hash = file_hash(local_path)
        logger.info(f"Local hash: {local_hash}")

        if last_uri:
            remote_hash = s3_file_hash(fs, last_uri)
            logger.info(f"Remote hash: {remote_hash} @ {last_uri}")

            if remote_hash == local_hash:
                logger.info("This is the same file")
                return False

        ts = datetime.now().strftime("%Y%m%d")
        s3_uri = f"{remote_path.rstrip('/')}/{stem}_{ts}.csv"
        logger.info(f"Upload to {s3_uri}")

        fs.put(str(local_path), s3_uri)

        return True

    except Exception as e:
        raise UploadError(f"Failed to upload {s3_uri}") from e
