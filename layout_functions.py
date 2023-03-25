import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from table_formats import group_colors
from ticker_info_support import ticker_info_fields, cards_id_dict


def apply_button(id_):
    return dbc.DropdownMenuItem(
        className='apply-button',
        children='APPLY FILTER',
        id=id_,
        n_clicks=0,
        active=True)


def select_all_button(id_):
    return dbc.DropdownMenuItem(
        className='select-all-button',
        children='SELECT ALL',
        id=id_,
        toggle=False,
        n_clicks=0)


def clean_all_button(id_):
    return dbc.DropdownMenuItem(
        className='clean-all-button',
        children='CLEAN SELECTION',
        id=id_,
        toggle=False,
        n_clicks=0)


def dropdown_checklist(id_, items_):
    return dbc.FormGroup(
        className='checklist-formgroup',
        children=[dcc.Checklist(
            options=[{'label': x, 'value': x} for x in items_],
            id=id_,
            className='filter-checklist',
            inputClassName='checklist-input',
            labelClassName='checklist-label')])


def get_dropdown(id_, label_, children_, class_='dropdown-filter', color_='secondary'):
    return dbc.DropdownMenu(
        className=class_,
        id=id_,
        toggleClassName='dropdown-button',
        label=label_,
        children=children_,
        color=color_,
        toggle_style={
            'color': '#FFF' if color_.upper() != '#FFF' else '#000',
            'border-color': color_ if color_.upper() != '#FFF' else '#6c757d'
        }
    )


# func to create dropdowns for table filtering
def filter_dropdowns(columns, dataframe):
    res = []
    for col in columns:
        select_all = select_all_button(id_=col + '-select-all-button')
        clean_all = clean_all_button(id_=col + '-clean-all-button')
        items = sorted(dataframe[col].unique().tolist())
        checklist = dropdown_checklist(id_=col + '-checklist', items_=items),
        apply = apply_button(id_=col + '-apply-button')
        dropdown = get_dropdown(
            id_=col + '-dropdown',
            label_=col,
            children_=[
                select_all,
                clean_all,
                dbc.DropdownMenuItem(divider=True),
                dbc.Form(checklist),
                dbc.DropdownMenuItem(divider=True),
                apply])
        res.append(dropdown)
    return res


# DROPDOWNS for selecting X, Y, Size and Color Features
def bubble_dropdown(id_, label, features_list, default_value):
    return html.Div(
        className='dropdown_box',
        children=[
            html.Label(label, className='dropdown_label'),
            dcc.Dropdown(
                id=id_,
                options=[{'label': x, 'value': x} for x in features_list],
                value=default_value)
        ])


# function to create Card for a specific group of indicators
def ticker_info_card(group_):
    return dbc.Card(
        id=group_ + '-card',
        className='ticker-info-card',
        style={'color': 'black'},
        children=[
            dbc.CardHeader(
                group_,
                className='ticker-info-card-header',
                style={
                    'background-color': group_colors[group_],
                    'color': 'white',
                }),
            dbc.CardBody(
                className='ticker-info-card-body',
                children=[
                    html.P(
                        className='ticker-info-card-p',
                        children=[
                            key + ': ',
                            html.B(id=cards_id_dict[key])
                        ]
                    ) for key in ticker_info_fields[ticker_info_fields.Group == group_].Field.tolist()
                ]
            )
        ]
    )
