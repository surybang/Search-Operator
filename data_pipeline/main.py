"Main entry for data_pipeline module"

import os
from datetime import datetime

from loguru import logger
import s3fs

from data_pipeline import (
    download_to_local,
    read_csv_local,
    upload_if_new,
    delete_local_file,
)


def main() -> None:
    logger.info(f"Start pipeline at {datetime.now().isoformat(timespec='seconds')}")

    # 1) Download
    local_path = download_to_local(
        url="https://extranet.arcep.fr/uploads/MAJNUM.csv",
        output_dir="data/raw",
        filename="MAJNUM.csv",
    )

    # 2) Lecture CSV locale
    df = read_csv_local(local_path)

    # 3) Aperçu
    logger.info(f"Overview of the DataFrame : \n {df.head()}")

    # 4) On check si le fichier est nouveau
    # 4bis) On doit d'abord initialiser un client MinIO
    fs = s3fs.S3FileSystem(
        client_kwargs={"endpoint_url": "https://" + "minio.lab.sspcloud.fr"},
        key=os.environ["AWS_ACCESS_KEY_ID"],
        secret=os.environ["AWS_SECRET_ACCESS_KEY"],
        token=os.environ["AWS_SESSION_TOKEN"],
    )
    bucket = "s3://fabienhos/arcep/"
    key = "raw"
    is_new = upload_if_new(fs, bucket, key, local_path)

    if is_new is True:
        logger.success(f"Succeeded upload to {bucket}{key}")
    else:
        delete_local_file(local_path)

    logger.info(
        f"End of the pipeline at {datetime.now().isoformat(timespec='seconds')}"
    )


if __name__ == "__main__":
    main()
