from fastapi import APIRouter
from llama_index.core import PromptTemplate
from llama_index.core.indices.struct_store.sql_retriever import SQLRetriever
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core.prompts.default_prompts import DEFAULT_TEXT_TO_SQL_PROMPT
from llama_index.core.query_pipeline import FnComponent
from llama_index.llms.openai import OpenAI
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import create_engine, MetaData

from wikitablequestions_llm_service.services.responses import responses
from wikitablequestions_llm_service_core.entities.table_info import TableInfo
from wikitablequestions_llm_service_core.handlers.create_sql_tables import (
    create_table_from_dataframe,
)
from wikitablequestions_llm_service_core.handlers.dataframes import get_dataframes
from wikitablequestions_llm_service_core.handlers.extract_wikitables_infos import (
    extract_wikitables_infos,
    get_wiketable_info_by_idx,
)
from wikitablequestions_llm_service_core.handlers.query_pipeline import (
    get_query_pipeline,
)
from wikitablequestions_llm_service_core.handlers.response_pqrser_to_sql import (
    parse_response_to_sql,
)
from wikitablequestions_llm_service_core.handlers.save_network import (
    save_query_pipeline_network,
)
from wikitablequestions_llm_service_core.handlers.sql_retriever import (
    get_table_context_str,
)
from wikitablequestions_llm_service_core.handlers.table_retriever import table_retrieval
from wikitablequestions_llm_service_core.prompts_templates import (
    table_prompt_template_str,
    response_synthesis_prompt_template_str,
)

wikitablequestions_llm_router = APIRouter(
    prefix="",
    tags=["wikitablequestions-lm-service"],
)

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

sql_database, obj_retriever, table_schema_objs = table_retrieval(
    engine=engine, table_infos=table_infos
)
sql_retriever = SQLRetriever(sql_database)
table_parser_component = FnComponent(fn=get_table_context_str)
sql_parser_component = FnComponent(fn=parse_response_to_sql)
text2sql_prompt = DEFAULT_TEXT_TO_SQL_PROMPT.partial_format(dialect=engine.dialect.name)
response_synthesis_prompt = PromptTemplate(
    response_synthesis_prompt_template_str,
)

query_pipeline = get_query_pipeline(
    obj_retriever=obj_retriever,
    table_parser_component=table_parser_component,
    text2sql_prompt=text2sql_prompt,
    llm=llm,
    sql_parser_component=sql_parser_component,
    sql_retriever=sql_retriever,
    response_synthesis_prompt=response_synthesis_prompt,
)


# save_query_pipeline_network(query_pipeline=query_pipeline)


class Query(BaseModel):
    question: str


@wikitablequestions_llm_router.post(path="", responses=responses)
async def get_awnser(query: Query):
    response = query_pipeline.run(query=query.question)

    return response
