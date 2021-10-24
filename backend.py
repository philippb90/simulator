import pandas as pd
from xbbg import blp
import sqlite3 as sql
import numpy as np

DB_PATH = "C:/ProgramData/Anaconda2/Working_dir/simulator.db"


class Backend():
    def __init__(self, db_path=DB_PATH):
        self.connection = sql.connect(db_path)
        self.cursor = self.connection.cursor()

    def get_index_member(self, tickers):
        return self.bdp(tickers=tickers, flds="INDX_MEMBERS", raw=True)

    def get_id(self, ticker, table_name="Securities", dict_like=True):
        id = pd.read_sql(
            con=self.connection,
            sql=f"SELECT id FROM {table_name} WHERE ticker = '{ticker}'"
        )["id"][0]

        if dict_like:
            return {ticker: id}
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

    def bdh(self, tickers, flds, start_date="1990-01-01", end_date="today", adjust="all", **kwargs):
        return blp.bdh(tickers=tickers,
                       flds=flds,
                       start_date=start_date,
                       end_date=end_date,
                       adjust=adjust)

    def insert(self, table_name, df, if_exists='append', index=False, uni_col_name="ticker"):
        try:
            df.to_sql(
                name=table_name,
                con=self.connection,
                if_exists=if_exists,
                index=index)

        except self.connection.IntegrityError as e:
            print(f"Initial failure to append: {e}\n")
            print("Attempting to rectify...")
            existing = pd.read_sql(sql=f"SELECT * FROM {table_name}",
                                   con=self.connection)
            to_insert = df.reset_index().rename(columns={"index":"id"})
            mask = ~to_insert.ticker.isin(existing.ticker)
            try:
                df.loc[mask].to_sql(
                    name=table_name,
                    con=self.connection,
                    index=False,
                    if_exists="append")
                print(f"Successfully inserted {df.loc[mask]} into database")

            except Exception as e2:
                "Could not rectify duplicate entries. \n{}".format(e2)
            return 'Success after dedupe'


    def _init_db_(self, init_from="config"):
        if init_from == "config":
            from __init_config__ import INDEX_TICKERS, STATIC_SECURITY_FIELDS
            self.INDEX_TICKERS = INDEX_TICKERS
            self.STATIC_SECURITY_FIELDS = STATIC_SECURITY_FIELDS

        self.INDEX_MEMBER = self.get_index_member(
            tickers=self.INDEX_TICKERS
        )["Member Ticker and Exchange Code"].unique()

        self.INDEX_MEMBER_TICKER = [f"{index_member} Equity" for index_member in self.INDEX_MEMBER]

        self.data = (
            self.bdp(
                tickers=[*self.INDEX_TICKERS, *self.INDEX_MEMBER_TICKER],
                flds=self.STATIC_SECURITY_FIELDS.keys())
                .rename(
                columns=self.STATIC_SECURITY_FIELDS,
                #inplace=True
                )
                .reset_index(#inplace=True
                )
                .rename(
                columns={"index": "ticker"},
                #inplace=True
                )
        )

        self.insert(
            table_name="Securities",
            df=self.data)


        # Static currency data
        self.currencies = self.data["currency"].unique()
        self.currency_ticker = [f"EUR{currency} Curncy" for currency in self.currencies]

        self.currency_entries = pd.DataFrame(
            {"id": np.repeat(np.nan, len(self.currencies)),
             "ticker": self.currency_ticker,
             "base_currency": np.repeat("EUR", len(self.currencies)),
             "quote_currency": self.currencies
             }
        )

        self.insert(table_name="Currencies",
                    df=self.currency_entries)

        self.currency_ticker = pd.read_sql(
            sql="SELECT ticker FROM Currencies",
            con=self.connection
        )

        self.currency_rates = (
            self.bdh(
                tickers=self.currency_ticker["ticker"],
                flds="px_last",
                start_date="1990-01-01")
                .droplevel(axis=1, level=1)
                .melt(ignore_index=False)
                .reset_index()
                .rename(columns={"index": "date", "variable": "ticker", "value": "px_last"})
                .dropna(how="any")
        )

        for ticker in self.currency_ticker["ticker"]:
            ticker_id = self.get_id(
                table_name="Currencies",
                ticker=ticker)

            self.currency_rates.loc[self.currency_rates.ticker == ticker, "ticker"] = int(ticker_id[ticker])

        self.currency_rates.rename(columns={"ticker": "currency_id"}, inplace=True)
        self.insert(
            table_name="Currency_Rates",
            df=self.currency_rates)


def add_missing_columns(df, column_names):
    import numpy as np

    lower_columns = [column.lower() for column in df.columns]
    for column in column_names:
        if column.lower() not in lower_columns:
            df[column.lower()] = np.nan

    return df


if __name__ == "__main__":
    print("Hello")
