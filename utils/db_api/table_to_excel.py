import logging
import sqlite3
import pandas as pd
import openpyxl


def table_to_xlsx(table_name='Users'):
    success = False
    try:
        conn = sqlite3.connect('data/database.db')
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        df.to_excel('data/Users.xlsx', index=False)
        success = True
    except Exception as err:
        logging.error(err)
    return success
