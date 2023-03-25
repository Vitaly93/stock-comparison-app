import plotly.graph_objects as go

stock_info_plot_height = 280
stock_info_margin_top = 10
stock_info_margin_bottom = 10


# price history graph
def create_time_series(dff):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(x=dff.Date, y=dff['Adj Close'], line={'color': '#007bff'})
    )
    fig.update_layout(
        yaxis_title='Adj Close',
        plot_bgcolor="white",
        height=stock_info_plot_height,
        margin=dict(
            r=10,
            t=stock_info_margin_top,
            b=stock_info_margin_bottom
        )
    )
    return fig


def create_fin_barchart(dff):
    fig = go.Figure()
    width = 0.25

    fig.add_trace(
        go.Bar(
            x=dff.Period,
            y=dff.Revenue,
            base=0,
            name='Revenue',
            marker_color='#6c757d',
            width=width
        )
    )

    fig.add_trace(
        go.Bar(
            x=dff.Period,
            y=dff.Earnings,
            base=0,
            name='Earnings',
            marker_color='rgb(26, 118, 255)',
            width=width
        )
    )

    fig.update_layout(
        yaxis={'title': 'USD'},
        height=stock_info_plot_height,
        legend={
            'x': 0.9,
            'y': 1.0,
        },
        margin=dict(
            t=stock_info_margin_top,
            b=stock_info_margin_bottom
        ),
        plot_bgcolor='white',
        barmode='group',
        bargap=0.3,  # gap between bars of adjacent location coordinates.
        bargroupgap=0.05  # gap between bars of the same location coordinate.
    )
    return fig

