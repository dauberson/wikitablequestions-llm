import pandas as pd
from sqlalchemy import (
    Table,
    Column,
    String,
    Integer,
)
import re


def process_colunm_name(column_name):
    # Remove special characters and replace spaces with underscores
    return re.sub(r"\W+", "_", column_name)


# Function to create a table from a DataFrame using SQLAlchemy
def create_table_from_dataframe(
    dataframe: pd.DataFrame, table_name: str, engine, metadata_obj
):
    # Sanitize column names
    sanitized_columns = {
        col: process_colunm_name(column_name=col) for col in dataframe.columns
    }
    dataframe = dataframe.rename(columns=sanitized_columns)

    # Dynamically create columns based on DataFrame columns and data types
    columns = [
        Column(col, String if dtype == "object" else Integer)
        for col, dtype in zip(dataframe.columns, dataframe.dtypes)
    ]

    # Create a table with the defined columns
    table = Table(table_name, metadata_obj, *columns)

    # Create the table in the database
    metadata_obj.create_all(engine)

    # Insert data from DataFrame into the table
    with engine.connect() as conn:
        for _, row in dataframe.iterrows():
            insert_stmt = table.insert().values(**row.to_dict())
            conn.execute(insert_stmt)
        conn.commit()
