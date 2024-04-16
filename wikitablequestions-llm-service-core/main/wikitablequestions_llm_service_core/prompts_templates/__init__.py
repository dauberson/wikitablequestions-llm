table_prompt_template_str = """\
Give me a Summary and Table Name of the table below with the following JSON format

- The table name must be unique to the table and describe it while being concise.
- Do NOT output a generic table name (e.g. table, my_table).
- Do NOT make the table name one of the following: {exclude_table_name_list}

Table:
{table_str}\
"""
