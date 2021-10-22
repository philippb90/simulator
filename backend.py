import pandas as pd
from xbbg import blp
import sqlite3 as sql

DB_PATH = "C:/ProgramData/Anaconda2/Working_dir/simulator.db"

class Backend():
    def __init__(self, db_path=DB_PATH):
        self.connection = sql.connect(db_path)
        self.cursor = self.connection.cursor()

    def get_index_member(self, tickers):
        return self.bdp(tickers=tickers, flds="INDX_MEMBERS", raw=True)

    def get_id(self, ticker, table_name="Securities",dict_like=True):
        id = pd.read_sql(
            con=self.connection,
            sql=f"SELECT id FROM {table_name} WHERE ticker = '{ticker}'"
        )["id"][0]

        if dict_like:
            return {ticker : id}
        else:
            return id

    def bdp(self, tickers, flds, **kwargs):
        data = blp.bdp(
            tickers=tickers,
            flds=flds,
            **kwargs)

        if kwargs.get('raw', True):
            return data
        else:
            data = add_missing_columns(
                df=data,
                column_names=flds)
            return data


    def bdh(self, tickers, flds, start_date="1990-01-01",end_date="today", adjust="all", **kwargs):
        return blp.bdh(tickers=tickers,
                flds=flds,
                start_date=start_date,
                end_date=end_date,
                adjust=adjust)

    def insert(self, table_name, df, if_exists='append', index=False):
        df.to_sql(
            name=table_name,
            con=self.connection,
            if_exists=if_exists,
            index=index)


def add_missing_columns(df, column_names):
    import numpy as np

    lower_columns = [column.lower() for column in df.columns]
    for column in column_names:
        if column.lower() not in lower_columns:
            df[column.lower()] = np.nan

    return df




if __name__ == "__main__":
    print("Hello")