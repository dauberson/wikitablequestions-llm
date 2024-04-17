table_prompt_template_str = """\
Give me a Summary and Table Name of the table below with the following JSON format

- The table name must be unique to the table and describe it while being concise.
- Do NOT output a generic table name (e.g. table, my_table).
- Do NOT make the table name one of the following: {exclude_table_name_list}

Table:
{table_str}\
"""

response_synthesis_prompt_template_str = (
    "Given an input question, synthesize a response from the query results.\n"
    "Query: {query_str}\n"
    "SQL: {sql_query}\n"
    "SQL Response: {context_str}\n"
    "Response: "
)
