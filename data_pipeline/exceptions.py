class DownloadError(Exception):
    """Raised when a file cannot be downloaded from source."""


class UploadError(Exception):
    """Raised when a file cannot be uploaded to MinIO."""
