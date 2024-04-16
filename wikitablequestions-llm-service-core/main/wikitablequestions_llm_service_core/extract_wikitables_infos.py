import json
from loguru import logger
from pathlib import Path
from typing import List, Optional

import pandas as pd
from llama_index.core.program import LLMTextCompletionProgram

from entities.table_info import TableInfo

wikitablequestions_infos_dir = "./data/WikiTableQuestions_Infos"


def get_wiketable_info_by_idx(idx: int) -> Optional[TableInfo]:
    results_gen = Path(wikitablequestions_infos_dir).glob(f"{idx}_*")
    results_list = list(results_gen)
    if len(results_list) == 0:
        return
    elif len(results_list) == 1:
        path = results_list[0]
        return TableInfo.parse_file(path)
    else:
        raise ValueError(f"More than one file matching index: {list(results_gen)}")


def extract_wikitables_infos(
    dataframes: List[pd.DataFrame],
    llm_text_completion_program: LLMTextCompletionProgram,
):
    table_names = set()
    table_infos = []
    for idx, df in enumerate(dataframes):
        table_info = get_wiketable_info_by_idx(idx)
        if table_info:
            table_infos.append(table_info)
        else:
            while True:
                df_str = df.head(10).to_csv()
                table_info = llm_text_completion_program(
                    table_str=df_str,
                    exclude_table_name_list=str(list(table_names)),
                )
                table_name = table_info.table_name
                logger.info(f"Processed table: {table_name}")
                if table_name not in table_names:
                    table_names.add(table_name)
                    break
                else:
                    logger.info(
                        f"Table name {table_name} already exists, trying again."
                    )
                    pass

            out_file = f"{wikitablequestions_infos_dir}/{idx}_{table_name}.json"
            json.dump(table_info.dict(), open(out_file, "w"))
        table_infos.append(table_info)
