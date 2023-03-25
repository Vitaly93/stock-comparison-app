from app import app
from dash.dependencies import Input, Output, State
from layout_common import filter_drops
from db_connection import df
import plotly.express as px
import numpy as np
import pandas as pd
from dash.exceptions import PreventUpdate
from dash import callback_context
from layout_table import groups, group_dict, subgroup_dict
from table_formats import format_list
from layout_bubble_plot import radio_dict, roles, role_hidden_divs
import json
from queries import query_price, query_fin, query_info, query_description
from plots import create_time_series, create_fin_barchart
from ticker_info_support import ticker_dict, default_ticker, periods, period_buttons_dict, \
    fin_modes, cards_id_dict, format_value


# update hidden div with filtered tickers
@app.callback(Output('tickers', 'children'),
              [Input(x + '-apply-button', 'n_clicks') for x in filter_drops],
              [State(x + '-checklist', 'value') for x in filter_drops])
def tickers(*args):
    clicks = args[:len(filter_drops)]
    if sum(clicks) == 0:
        raise PreventUpdate
    else:
        cols = args[-len(filter_drops):]
        if sum(clicks) > 0:
            def get_tickers(dataframe, field, selection):
                if not selection:
                    names = dataframe[field].unique().tolist()
                else:
                    names = selection
                return set(dataframe[dataframe[field].isin(names)].Ticker)

            res = get_tickers(df, filter_drops[0], cols[0])
            for i, col in enumerate(cols[1:]):
                res = res.intersection(get_tickers(df, filter_drops[i + 1], col))
            return list(res)


# update filters' labels with tickers from hidden div
@app.callback([Output(x + '-checklist', 'options') for x in filter_drops],
              Input('tickers', 'children'), prevent_initial_call=True)
def update_dropdowns(t):
    def get_names(dataframe, field):
        names = dataframe[dataframe.Ticker.isin(t)][field].unique()
        return sorted(names)

    def get_options(arr):
        return [{'label': x, 'value': x} for x in arr]

    return [get_options(get_names(df, x)) for x in filter_drops]


# update tickers-table hidden Div with tickers from filtered table
@app.callback(
    Output('tickers-table', 'children'),
    Input('table', 'derived_virtual_data'), Input('tickers', 'children')
)
def update_tickers_by_table(rows, tickers_):
    if not rows:
        return tickers_
    else:
        return [x['Ticker'] for x in rows]


# update Dash Data Table records with filtered tickers
@app.callback(Output('table', 'data'), Input('tickers', 'children'))
def filter_table(t):
    return df[df.Ticker.isin(t)].to_dict('records')


for x in filter_drops:
    # change dropdown color if smth is selected in a checklist
    @app.callback(
        Output(x + '-dropdown', 'toggle_style'),
        Input(x + '-checklist', 'value')
    )
    def update_color(selection):
        if selection:
            return {'background-color': '#007bff', 'border-color': '#007bff'}

    # select all values in the current checklist
    @app.callback(
        Output(x + '-checklist', 'value'),
        [Input(x + '-select-all-button', 'n_clicks'),
         Input(x + '-clean-all-button', 'n_clicks'),
         Input(x + '-checklist', 'options')]
    )
    def update_all_options(select_clicks, clean_clicks, options):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if 'sel' in button_id:
                return [x['value'] for x in options]
            else:
                return []


# update hidden div with filtered columns
@app.callback(
    Output('columns', 'children'),
    [Input(group_dict[gr]['apply-button'], 'n_clicks') for gr in groups],
    [State(cl, 'value') for cl in [x['checklist-name'] for x in list(subgroup_dict.values())]]
)
def cols_update(*args):
    clicks = args[:len(groups)]
    if sum(clicks) == 0 or clicks == [None] * len(clicks):
        raise PreventUpdate
    else:
        res = []
        selections = args[len(groups):]
        for sel in selections:
            res += sel
        return res


@app.callback(
    Output('table', 'columns'),
    Input('columns', 'children')
)
def filter_cols(cols_):
    return [x for x in format_list if x['id'] in cols_]


# callback to select all/clean all options in column-selection dropdowns
for g in groups:
    sgs_ = group_dict[g]['subgroups']
    sg_checklists = [subgroup_dict[x]['checklist-name'] for x in sgs_]


    @app.callback(
        [Output(x, 'value') for x in sg_checklists],
        [Input(group_dict[g]['select-button'], 'n_clicks'),
         Input(group_dict[g]['clean-button'], 'n_clicks')],
        [State(x, 'options') for x in sg_checklists]
    )
    def select_calean_checklists(*args):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
            if 'sel' in button_id:
                return [[x['value'] for x in lst] for lst in args[2:]]
            else:
                return [[] for x in args[2:]]


# callback to clean radio items per new choice for Bubble plot
for r in roles:
    radios = radio_dict[r]['radio_ids']

    @app.callback(
        [Output(x, 'value') for x in radios],
        [Input(x, 'id') for x in radios] + [Input(x, 'value') for x in radios]
    )
    def clean_radios(*args):
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        else:
            ids = args[:int(len(args) / 2)]
            vals = args[int(len(args) / 2):]
            radio = ctx.triggered[0]['prop_id'].split('.')[0]
            selected_val = vals[ids.index(radio)]
            return [selected_val if x == radio else None for x in ids]


# update role hidden divs with selected values
for r in roles:
    radios = radio_dict[r]['radio_ids']

    @app.callback(
        Output(role_hidden_divs[r], 'children'),
        [Input(x, 'value') for x in radios]
    )
    def update_role_value(*args):
        for x in args:
            if x:
                return x


# update bubble-plot with selected roles
@app.callback(
    Output('bubble_plot', 'figure'),
    [Input(role_hidden_divs[r], 'children') for r in roles] + [Input('tickers-table', 'children')]
)
def update_plot(xaxis, yaxis, size, color, t):
    df_ = df.loc[df.Ticker.isin(t)].copy()
    df_[size + '_sqrt'] = np.sqrt(df_[size].fillna(1))
    fig = px.scatter(df_, x=xaxis, y=yaxis, color=color,
                     hover_name=df_['Ticker'] + ': ' + df_['Name'],
                     size=size + '_sqrt',
                     custom_data=['Ticker'])
    fig.update_layout(
        paper_bgcolor='rgb(243, 243, 243)',
        plot_bgcolor='rgb(243, 243, 243)'
    )
    return fig


# Upd. 07/07/2021: update Ticker hidden DIV with one of the following:
# - selection of a table row
# - click on a point of a bubble plot
# - entering a ticker in a ticker-input field
@app.callback(
    Output('open-modal', 'children'),
    [
        Input('ticker-input-button', 'n_clicks'),
        Input('bubble_plot', 'clickData'),
        Input('table', 'derived_virtual_selected_rows')
    ],
    State('table', 'derived_virtual_data'), State('ticker-input', 'value')
)
def update_ticker(clicks, clickdata, selected_row, rows, t):
    ctx = callback_context
    if not ctx.triggered:
        return default_ticker
    else:
        active_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if active_id == 'table':
            if not selected_row or selected_row is None:
                return default_ticker
            else:
                dff = pd.DataFrame(rows)
                return dff.iloc[selected_row[0]]['Ticker']
        elif active_id == 'ticker-input-button':
            return t[:t.find(':')]
        else:
            return clickdata['points'][0]['customdata'][0]


# callbacks for MODAL
@app.callback(
    Output("ticker-modal", "is_open"),
    [Input("open-modal", "n_clicks"), Input("close-modal", "n_clicks")],
    [State("ticker-modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


# callback to update data in modal on click
@app.callback(
    [Output('modal-header', 'children'), Output('modal-text', 'children')],
    [Input('open-modal', 'n_clicks'), State('open-modal', 'children'), State('ticker-info-store', 'data')]
)
def update_modal(n1, ticker_, data):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        return json.loads(data)['Name'], query_description(ticker_)


# callback to update Store with json'ified data with Ticker info
@app.callback(
    Output('ticker-info-store', 'data'),
    Input('open-modal', 'children')
)
def update_ticker_store(ticker_):
    return query_info(ticker_).loc[0].to_json()


# callback for title update
@app.callback(
    Output('ticker-header', 'children'),
    Input('ticker-info-store', 'data')
)
def update_title(data):
    return json.loads(data)['Name']


# callback to update Ticker price in header
@app.callback(
    Output('ticker-price', 'children'),
    Input('ticker-info-store', 'data')
)
def update_price(data):
    return '{:.2f}'.format(json.loads(data)['Quote Price'])


# callback to update price change in header
@app.callback(
    [Output('ticker-price-change', 'children'), Output('ticker-price-change', 'style')],
    Input('ticker-info-store', 'data')
)
def update_price_change(data):
    d_ = json.loads(data)
    diff = (d_['Quote Price'] - d_['Previous Close']) / d_['Previous Close']
    if diff > 0:
        style = {'color': '#28a745'}
    elif diff == 0:
        style = {'color': 'black'}
    else:
        style = {'color': '#dc3545'}
    return '(' + '{:+.2%}'.format(diff) + ')', style


# callback to update period hidden Div with clicked period button
@app.callback(
    Output('period', 'children'),
    [Input(period_buttons_dict[x], 'n_clicks') for x in periods]
)
def update_period(*args):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return list(period_buttons_dict.keys())[list(period_buttons_dict.values()).index(button_id)]


# callback to update color of the period buttons
@app.callback(
    [Output(period_buttons_dict[x], 'color') for x in periods],
    [Input(period_buttons_dict[x], 'n_clicks') for x in periods]
)
def update_color(*args):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return ['primary' if button_id == x else 'secondary' for x in list(period_buttons_dict.values())]


# callback for price chart
@app.callback(
    Output('price-chart', 'figure'),
    [Input('open-modal', 'children'), Input('period', 'children')]
)
def update_price_chart(ticker_, period_):
    dff = query_price(ticker_, period_)
    return create_time_series(dff)


# callback to update color of the fin mode buttoms
@app.callback(
    [Output(x, 'color') for x in fin_modes],
    [Input(x, 'n_clicks') for x in fin_modes]
)
def update_color(*args):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return ['primary' if button_id == x else 'secondary' for x in fin_modes]


# callback to update fin-mode hidden Div with clicked fin-mode
@app.callback(
    Output('fin-mode', 'children'),
    [Input(x, 'n_clicks') for x in fin_modes]
)
def update_period(*args):
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        return button_id


# callback to update financial barchart
@app.callback(
    Output('fin-barchart', 'figure'),
    [Input('open-modal', 'children'), Input('fin-mode', 'children')]
)
def update_fin_barchart(ticker_, mode_):
    dff = query_fin(ticker_, mode_)
    return create_fin_barchart(dff)


# callback to update Cards with ticker-info
@app.callback(
    [Output(cards_id_dict[x], 'children') for x in cards_id_dict],
    Input('ticker-info-store', 'data')
)
def update_cards(data):
    data = json.loads(data)
    return [format_value(key, data[key]) for key in cards_id_dict]
