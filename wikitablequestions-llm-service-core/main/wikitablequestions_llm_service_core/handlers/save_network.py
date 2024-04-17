from llama_index.core.query_pipeline import QueryPipeline
from pyvis.network import Network


def save_query_pipeline_network(query_pipeline: QueryPipeline):
    net = Network(notebook=True, cdn_resources="in_line", directed=True)
    net.from_nx(query_pipeline.dag)
    net.write_html("./handlers/query_pipeline_dag.html")
