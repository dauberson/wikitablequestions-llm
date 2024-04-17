from llama_index.core import PromptTemplate
from llama_index.core.indices.struct_store.sql_retriever import SQLRetriever
from llama_index.core.objects import ObjectRetriever
from llama_index.core.query_pipeline import QueryPipeline, InputComponent, FnComponent
from llama_index.llms.openai import OpenAI


def get_query_pipeline(
    obj_retriever: ObjectRetriever,
    table_parser_component: FnComponent,
    text2sql_prompt: PromptTemplate,
    llm: OpenAI,
    sql_parser_component: FnComponent,
    sql_retriever: SQLRetriever,
    response_synthesis_prompt: PromptTemplate,
) -> QueryPipeline:

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

    return query_pipeline
