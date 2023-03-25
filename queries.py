from db_connection import db, sqlite3
import pandas as pd

dateadd_dict = {
    '1M': '-1 months', '3M': '-3 months', '6M': '-6 months', '1Y': '-1 years', '5Y': '-5 years'
}


def query_price(ticker_, period):
    conn_price = sqlite3.connect(db)
    if period != 'MAX':
        date_condition = """
        AND Date >= DATE((SELECT MAX(Date) FROM stock_history), {})
        """.format('\'' + dateadd_dict[period] + '\'')
    else:
        date_condition = ''
    query = """
    SELECT Date, [Adj Close]
    FROM stock_history
    WHERE Ticker={}
    {}
    ORDER BY Date ASC
    """.format('\''+ticker_+'\'', date_condition)
    df_ = pd.read_sql(query, conn_price)
    conn_price.close()
    return df_


def query_fin(ticker_, period='Quarter'):
    conn_fin = sqlite3.connect(db)
    if period == 'Quarter':
        target_table = 'income_statement_qtr'
    elif period == 'Year':
        target_table = 'income_statement_year'
    query = """
    SELECT
    SUBSTR(endDate,1,4) || '/' || SUBSTR(endDate,6,2) AS 'Period', 
    totalRevenue AS 'Revenue', 
    netIncome AS 'Earnings'
    FROM {}
    WHERE Ticker = {}
    ORDER BY endDate ASC
    """.format(target_table, '\'' + ticker_ + '\'')
    df_ = pd.read_sql(query, conn_fin)
    conn_fin.close()
    return df_


def query_info(ticker_):
    conn_info = sqlite3.connect(db)
    query = """
    SELECT 
    sq.[Previous Close],
    sq.[52 Week Range], 
    sq.[Earnings Date], 
    sq.[Ex-Dividend Date],
    sf.*
    FROM stock_info_quote_table sq JOIN stock_features sf ON sq.Ticker = sf.Ticker
    WHERE sq.Ticker = {}
    """.format('\'' + ticker_ + '\'')
    df_ = pd.read_sql(query, conn_info)
    conn_info.close()
    return df_


def query_description(ticker_):
    conn_desc = sqlite3.connect(db)
    query = """
    select longBusinessSummary from master_data
    WHERE Ticker = {}
    """.format('\'' + ticker_ + '\'')
    df_ = pd.read_sql(query, conn_desc)
    conn_desc.close()
    return df_['longBusinessSummary'][0]
