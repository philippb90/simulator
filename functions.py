from backend import DB_PATH, Backend
import pandas as pd
import sqlite3 as sql

def filter_universe(ticker, filter_name="Turnover", filter_field = "30_day_average_turnover_at_time", threshold=100000000):
    backend = Backend(DB_PATH)

    if isinstance(ticker, str): ticker = (ticker,"")
    if isinstance(ticker, list): ticker = tuple(ticker)

    current_rates = pd.read_sql(
        con=sql.connect(DB_PATH),
        sql=f"""
            with current_rates as (
                SELECT MAX(date) as max_date ,quote_currency, px_last FROM Currency_Rates_View
                GROUP BY ticker)
            
            SELECT max_date, Securities.ticker, current_rates.quote_currency, px_last
            FROM Securities 
            INNER JOIN current_rates
             on Securities.currency = current_rates.quote_currency
            WHERE Securities.asset_class != 'Index' AND ticker IN {ticker}
            """
    )

    current_rates.set_index("ticker", inplace=True, drop=False)

    filter_values = backend.bdp(
        tickers=current_rates.index.values,
        flds=filter_field
    )

    current_rates = current_rates.join(filter_values, how="inner")
    current_rates[filter_name] = current_rates[filter_field] / current_rates[
        "px_last"]

    ticker = current_rates.loc[current_rates[filter_field] > threshold, ["ticker",filter_name]]
    return ticker