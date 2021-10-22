from backend import Backend, DB_PATH
import pandas as pd
import numpy as np
import sqlite3 as sql

def init_db():
    from __init_config__ import INDEX_TICKERS, STATIC_SECURITY_FIELDS

    backend = Backend(db_path=DB_PATH)
    connection = sql.connect(DB_PATH)

    #Static security data
    known_index_tickers = pd.read_sql(
        sql="SELECT ticker FROM Securities WHERE asset_class = 'Index'",
        con=connection
    )

    for ticker in known_index_tickers["ticker"]:
        if ticker in INDEX_TICKERS:
            INDEX_TICKERS.remove(ticker)

    if INDEX_TICKERS:
        INDEX_MEMBER = backend.get_index_member(
            tickers=INDEX_TICKERS
            )["Member Ticker and Exchange Code"].unique()

        INDEX_MEMBER_TICKER = [f"{index_member} Equity" for index_member in INDEX_MEMBER]

        data = backend.bdp(
            tickers=[*INDEX_TICKERS, *INDEX_MEMBER_TICKER],
            flds=STATIC_SECURITY_FIELDS.keys()
        )

        data.rename(
            columns=STATIC_SECURITY_FIELDS,
            inplace=True
        )
        data.reset_index(inplace=True)
        data.rename(
            columns={"index" : "ticker"},
            inplace=True
        )

        backend.insert(
            table_name="Securities",
            df=data
        )

        #Static currency data
        currencies = data["currency"].unique()
        currency_ticker = [f"EUR{currency} Curncy" for currency in currencies]


        currency_entries = pd.DataFrame(
            {"id" : np.repeat(np.nan,len(currencies)),
             "ticker" : currency_ticker,
             "base_currency" : np.repeat("EUR", len(currencies)),
             "quote_currency" : currency
             }
        )
        backend.insert(table_name="Currencies",
                       df=currency_entries)


    currency_ticker = pd.read_sql(
        sql="SELECT ticker FROM Currencies",
        con=connection
    )

    currency_rates = (
        backend.bdh(
            tickers=currency_ticker["ticker"],
            flds="px_last",
            start_date="1990-01-01"
        )
        .droplevel(axis=1, level=1)
        .melt(ignore_index=False)
        .reset_index()
        .rename(columns={"index" : "date", "variable" : "ticker", "value" : "px_last"})
        .dropna(how="any")
        )

    for ticker in currency_ticker["ticker"]:
        ticker_id = backend.get_id(
            table_name="Currencies",
            ticker=ticker)

        currency_rates.loc[currency_rates.ticker == ticker, "ticker"] = int(ticker_id[ticker])
    
    currency_rates.rename(columns={"ticker" : "currency_id"}, inplace = True)
    backend.insert(
        table_name="Currency_Rates",
        df=currency_rates)
    
if __name__ == '__main__':
    #init_db()

