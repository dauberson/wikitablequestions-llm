from loguru import logger
from pathlib import Path
from typing import Optional, List

import pandas as pd


def get_dataframes(csv_id: int) -> Optional[List[pd.DataFrame]]:
    data_dir = Path(f"./data/WikiTableQuestions/csv/{csv_id}-csv")
    csv_files = sorted([f for f in data_dir.glob("*.csv")])
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
