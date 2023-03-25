import dash_html_components as html
import dash_bootstrap_components as dbc
from layout_table import table_layout
from layout_bubble_plot import bubble_plot_layout
from layout_ticker_info import ticker_info_layout
from db_connection import df
# import pandas as pd
from layout_functions import filter_dropdowns

# COLUMNS FOR FILTERING AND DROPDOWNS
# columns to be used in checklists or dropdowns for table filtering
filter_drops = ['Sector', 'Industry', 'Country', 'Market', 'Currency']

layout = html.Div(
    children=[
        dbc.Tabs(
            [
                dbc.Tab(
                    label='Table',
                    tab_id='table-tab',
                    children=[
                        html.Div(
                            className='filter-header',
                            children=filter_dropdowns(filter_drops, df)),
                        html.Div(id='tickers', hidden=True, children=df.Ticker.tolist()),
                        html.Div(table_layout),
                        html.Div(id='tickers-table', hidden=True)
                    ]
                ),
                dbc.Tab(
                    label='BubblePlot',
                    tab_id='plot-tab',
                    children=bubble_plot_layout
                ),
                dbc.Tab(
                    label='TickerInfo',
                    tab_id='ticker-info-tab',
                    children=ticker_info_layout
                )
            ]
        )
    ])