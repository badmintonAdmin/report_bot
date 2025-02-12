import os
from db.db import database
import pandas as pd


def where_tokens(tokens: dict[str, tuple[str, ...]]):
    file_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "sql", "where_tokens.sql")
    )
    result = database.execute_query_get(file_path, tokens)
    database.close_connection()
    if result is None:
        return None
    return result
