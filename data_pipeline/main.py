"Main entry for data_pipeline module"

from datetime import datetime

from loguru import logger

from data_pipeline.download import download_to_local
from data_pipeline.read import read_csv_local


def main() -> None:
    logger.info(f"Début du pipeline à {datetime.now().isoformat(timespec='seconds')}")

    # 1) Download
    local_path = download_to_local(
        url="https://extranet.arcep.fr/uploads/MAJNUM.csv",
        output_dir="data/raw",
        filename="MAJNUM.csv",
    )

    # 2) Lecture CSV locale
    df = read_csv_local(local_path)

    # 3) Aperçu
    logger.info(f"Aperçu du DataFrame : \n {df.head()}")
    logger.info(f"Fin du pipeline à {datetime.now().isoformat(timespec='seconds')}")


if __name__ == "__main__":
    main()
