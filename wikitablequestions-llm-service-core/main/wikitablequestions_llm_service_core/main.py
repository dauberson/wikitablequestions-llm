from loguru import logger
import sys
import os

import phoenix as px
import llama_index

from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core import Settings, set_global_handler
from llama_index.llms.openai import OpenAI

from wikitablequestions_llm_service_core.create_sql_tables import (
    create_table_from_dataframe,
)
from wikitablequestions_llm_service_core.dataframes import get_dataframes
from wikitablequestions_llm_service_core.entities.table_info import TableInfo
from wikitablequestions_llm_service_core.extract_wikitables_infos import (
    extract_wikitables_infos,
    get_wiketable_info_by_idx,
)
from wikitablequestions_llm_service_core.models_handlers.embed_model_handler import (
    get_embed_model,
)
from wikitablequestions_llm_service_core.prompts_templates import (
    table_prompt_template_str,
)

from sqlalchemy import create_engine, MetaData

from wikitablequestions_llm_service_core.table_retriever import table_retrieval

px.launch_app()
set_global_handler("arize_phoenix")

if __name__ == "__main__":
    dataframes = get_dataframes(csv_id=200)
    if not dataframes:
        logger.warning("No data to process")

    # Settings.llm = get_llm()
    Settings.embed_model = get_embed_model()

    llm_text_completion_program = LLMTextCompletionProgram.from_defaults(
        output_cls=TableInfo,  # output_parser=PydanticOutputParser(output_cls=TableInfo),
        prompt_template_str=table_prompt_template_str,
        llm=OpenAI(model="gpt-3.5-turbo"),
        verbose=True,
    )

    extract_wikitables_infos(
        dataframes=dataframes,
        llm_text_completion_program=llm_text_completion_program,
    )

    engine = create_engine("sqlite:///:memory:")
    metadata_obj = MetaData()
    table_infos = []
    for idx, dataframe in enumerate(dataframes):
        table_info = get_wiketable_info_by_idx(idx)
        table_infos.append(table_info)
        logger.info(f"Creating table: {table_info.table_name}")
        create_table_from_dataframe(
            dataframe=dataframe,
            table_name=table_info.table_name,
            engine=engine,
            metadata_obj=metadata_obj,
        )

    table_retrieval(engine=engine, table_infos=table_infos)
