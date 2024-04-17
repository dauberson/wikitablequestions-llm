from llama_index.core.indices.struct_store.sql_retriever import SQLRetriever
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
from llama_index.core.query_pipeline import FnComponent, QueryPipeline, InputComponent
from loguru import logger

import phoenix as px

from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core import Settings, set_global_handler, PromptTemplate
from llama_index.llms.openai import OpenAI

from wikitablequestions_llm_service_core.handlers.create_sql_tables import (
    create_table_from_dataframe,
)
from wikitablequestions_llm_service_core.entities.table_info import TableInfo
from wikitablequestions_llm_service_core.handlers.dataframes import get_dataframes
from wikitablequestions_llm_service_core.handlers.extract_wikitables_infos import extract_wikitables_infos, \
    get_wiketable_info_by_idx
from wikitablequestions_llm_service_core.handlers.response_pqrser_to_sql import parse_response_to_sql
from wikitablequestions_llm_service_core.handlers.sql_retriever import get_table_context_str
from wikitablequestions_llm_service_core.models_handlers.embed_model_handler import (
    get_embed_model,
)
from wikitablequestions_llm_service_core.prompts_templates import (
    table_prompt_template_str,
)

from sqlalchemy import create_engine, MetaData

from wikitablequestions_llm_service_core.handlers.table_retriever import table_retrieval

px.launch_app()
set_global_handler("arize_phoenix")

if __name__ == "__main__":
    dataframes = get_dataframes(csv_id=200)
    if not dataframes:
        logger.warning("No data to process")

    # Settings.llm = get_llm()
    # Settings.embed_model = get_embed_model()

    llm = OpenAI(model="gpt-3.5-turbo")
    llm_text_completion_program = LLMTextCompletionProgram.from_defaults(
        output_cls=TableInfo,  # output_parser=PydanticOutputParser(output_cls=TableInfo),
        prompt_template_str=table_prompt_template_str,
        llm=llm,
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

    sql_database, obj_retriever, table_schema_objs = table_retrieval(engine=engine, table_infos=table_infos)
    sql_retriever = SQLRetriever(sql_database)
    table_parser_component = FnComponent(fn=get_table_context_str)
    sql_parser_component = FnComponent(fn=parse_response_to_sql)
    text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(
        dialect=engine.dialect.name
    )

    response_synthesis_prompt_str = (
        "Given an input question, synthesize a response from the query results.\n"
        "Query: {query_str}\n"
        "SQL: {sql_query}\n"
        "SQL Response: {context_str}\n"
        "Response: "
    )
    response_synthesis_prompt = PromptTemplate(
        response_synthesis_prompt_str,
    )

    query_pipeline = QueryPipeline(
        modules={
            "input": InputComponent(),
            "table_retriever": obj_retriever,
            "table_output_parser": table_parser_component,
            "text2sql_prompt": text2sql_prompt,
            "text2sql_llm": llm,
            "sql_output_parser": sql_parser_component,
            "sql_retriever": sql_retriever,
            "response_synthesis_prompt": response_synthesis_prompt,
            "response_synthesis_llm": llm,
        },
        verbose=True,
    )

    query_pipeline.add_chain(["input", "table_retriever", "table_output_parser"])
    query_pipeline.add_link("input", "text2sql_prompt", dest_key="query_str")
    query_pipeline.add_link("table_output_parser", "text2sql_prompt", dest_key="schema")
    query_pipeline.add_chain(
        ["text2sql_prompt", "text2sql_llm", "sql_output_parser", "sql_retriever"]
    )
    query_pipeline.add_link(
        "sql_output_parser", "response_synthesis_prompt", dest_key="sql_query"
    )
    query_pipeline.add_link(
        "sql_retriever", "response_synthesis_prompt", dest_key="context_str"
    )
    query_pipeline.add_link("input", "response_synthesis_prompt", dest_key="query_str")
    query_pipeline.add_link("response_synthesis_prompt", "response_synthesis_llm")

    response = query_pipeline.run(
        query="What was the year that The Notorious B.I.G was signed to Bad Boy?"
    )
    print(str(response))
