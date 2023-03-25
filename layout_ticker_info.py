import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from ticker_info_support import default_ticker, periods, default_period, fin_modes, default_mode, ticker_dict, \
    ticker_info_fields
from layout_functions import ticker_info_card

period_buttons_dict = {
    x: 'period-' + 'button-' + x for x in periods
}

# datalist for ticket input auto fill
ticker_datalist = html.Datalist(
    id='ticker-datalist',
    hidden=False,
    children=[
        html.Option(value=x) for x in list(ticker_dict.values())
    ]
)

# ticker input field with button
ticker_input_container = html.Div(
    id='ticker_input_container',
    className='ticker_input_container',
    children=[
        dcc.Input(
            id='ticker-input',
            className='ticker-input',
            placeholder='Type Ticker here',
            list='ticker-datalist'
        ),
        dbc.Button(
            children='OK',
            id='ticker-input-button',
            className='ticker-input-button',
            color='primary',
            n_clicks=0
        )
    ]
)

ticker_modal = html.Div(
    children=[
        dbc.Button(
            id='open-modal',
            className='ticker-modal-button',
            n_clicks=0,
            color='light'
        ),
        dbc.Modal(
            id="ticker-modal",
            scrollable=True,
            is_open=False,
            children=[
                dbc.ModalHeader(id='modal-header'),
                dbc.ModalBody(id='modal-text'),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close",
                        id="close-modal",
                        className="ml-auto",
                        n_clicks=0,
                    )
                ),
            ]
        )
    ]
)

# header with selected ticker name and company name
ticker_header_container = html.Div(
    id='ticker-header-container',
    className='ticker-header-container',
    children=[
        dcc.Store(
            id='ticker-info-store'
        ),
        ticker_modal,
        html.H4(
            id='ticker-header',
            className='ticker-header'
        ),
        html.H4(
            id='ticker-price',
            className='ticker-price',
            style={
                'color': '#007bff'
            }
        ),
        html.H6(
            id='ticker-price-change',
            className='ticker-price-change'
        )
    ]
)

# DIV with buttons for price histiory period selection
period_buttons = dbc.ButtonGroup(
    id='period-buttons',
    className='period-buttons',
    children=[
        dbc.Button(
            x,
            id=period_buttons_dict[x],
            className='period-button',
            color='primary' if x == default_period else 'secondary'
        ) for x in periods
    ]
)

# DIV for price history and period buttons
price_graph_container = html.Div(
    id='price-graph-container',
    className='price-graph-container',
    children=[
        period_buttons,
        html.Div(id='period', children=default_period, hidden=True),
        dcc.Graph(id='price-chart', className='price-chart')
    ]
)

# DIV with buttons for price history period selection
fin_mode_buttons = dbc.ButtonGroup(
    id='fin-mode-buttons',
    className='fin-mode-buttons',
    children=[
        dbc.Button(
            children=x,
            id=x,
            className='fin-mode-button',
            color='primary' if x == default_mode else 'secondary'
        ) for x in fin_modes
    ]
)

fin_barchart_container = html.Div(
    id='fin-barchart-container',
    className='fin-barchart-container',
    children=[
        fin_mode_buttons,
        html.Div(id='fin-mode', children=default_mode, hidden=True),
        dcc.Graph(id='fin-barchart', className='fin-barchart')
    ]
)

# container for ticker price chart, profit/revenue chart and descriptions
ticker_charts_container = html.Div(
    id='ticker-charts-container',
    className='ticker-charts-container',
    children=[
        price_graph_container,
        fin_barchart_container
    ]
)


# container for additional information about a Ticker
# opacity = '30%'


# function to convert hex color to rgb for card-background color styling
# def hex_to_rgba(color, opacity_):
#     def hex_to_rgb(value):
#         value = value.lstrip('#')
#         lv = len(value)
#         return ','.join(map(str, list(int(value[i:i+lv//3], 16) for i in range(0, lv, lv//3))))
#     rgb = hex_to_rgb(color)
#     return 'rgba({},{})'.format(rgb, opacity_)

ticker_info_container = html.Div(
    id='ticker-info-container',
    className='ticker-info-container',
    children=[
        ticker_info_card(g) for g in ticker_info_fields.Group.unique()
    ]
)

ticker_info_layout = html.Div(
    [
        ticker_datalist,
        ticker_input_container,
        ticker_header_container,
        ticker_charts_container,
        ticker_info_container
    ]
)
