import os

from loguru import logger
from pathlib import Path
from typing import Optional, List

import pandas as pd

path = os.path.realpath(__file__)
root_dir = os.path.dirname(path)
wikitablequestions_infos_dir = f"{Path(root_dir).parent}/data/WikiTableQuestions"


def get_dataframes(csv_id: int) -> Optional[List[pd.DataFrame]]:
    data_dir = Path(f"{wikitablequestions_infos_dir}/csv/{csv_id}-csv")
    csv_files = sorted([i for i in data_dir.glob("*.csv")])
    dataframes_list = []
    for csv_file in csv_files:
        logger.info(f"processing file: {csv_file}")
        try:
            df = pd.read_csv(csv_file)
            dataframes_list.append(df)
        except Exception as e:
            logger.error(f"Error parsing {csv_file}: {e}")
            continue
    return dataframes_list
