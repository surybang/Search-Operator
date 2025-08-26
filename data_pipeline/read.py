"""This script aims to read a csv from a local directory"""
from pathlib import Path

import pandas as pd
from loguru import logger

from decorators import timed


@timed("Read CSV")
def read_csv_local(
        path: str | Path,
        encodings: list[str] = ["utf-8", "ISO-8859-1"],
        separators: list[str] = [",", ";"],
        sample_rows: int = 50
        ) -> pd.DataFrame:
    """
    Try to read a CSV file by testing multiple encoding and separator combinations.

    The function attempts to read the CSV file using each candidate pair of
    (encoding, separator) until one succeeds. If none of the combinations
    work, a RuntimeError is raised.

    Args:
        path (str | Path): Path to the CSV file.

        encodings (list[str]): Candidate text encodings to try
            (e.g., "utf-8", "ISO-8859-1"). Defaults to ["utf-8", "ISO-8859-1"].

        separators (list[str]): Candidate field separators to try
                (e.g., ",", ";"). Defaults to [",", ";"].

        sample_rows (int): Number of rows to initially test when
                validating a combination. Defaults to 50.

    Returns:
        pd.DataFrame: The DataFrame loaded with the first successful
        (encoding, separator) combination.

    Raises:
        RuntimeError: If no encoding/separator combination can successfully read the file.
    """
    for encoding, separator in zip(encodings, separators):
        try:
            logger.info(f"Test reading DataFrame with (sep='{separator}', encoding='{encoding}')")
            # first, we try with a sample
            pd.read_csv(path, sep=separator, encoding=encoding, nrows=sample_rows)
            # if its ok we assign df
            df = pd.read_csv(path, sep=separator, encoding=encoding)
            logger.success(f"Success with (sep='{separator}', encoding='{encoding}')")
            return df

        except UnicodeDecodeError:
            logger.warning(f"UnicodeDecodeError with (sep='{separator}', encoding='{encoding}')")

        except pd.errors.ParserError:
            logger.warning(f"ParserError with (sep='{separator}', encoding='{encoding}')")

    raise RuntimeError("Can't read CSV file with the specified config")
