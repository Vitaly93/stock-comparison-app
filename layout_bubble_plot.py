import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from table_formats import group_dict, groups, subgroup_dict
from db_connection import df
from layout_functions import get_dropdown
from layout_functions import bubble_dropdown

# dictionaries for building dropdowns per role
roles = ['x', 'y', 'size', 'color']
radio_dict = {r: {'radio_ids': []} for r in roles}
for r in roles:
    grs_ = groups if r == 'color' else [x for x in groups if x != 'Descriptive']
    for g in grs_:
        for sg in group_dict[g]['subgroups']:
            radio_id = r + '-' + g + '-' + sg + '-radio'
            radio_dict[r]['radio_ids'].append(radio_id)
            radio_dict[r][sg] = {'radio-id': radio_id}

default_values = {
    'x': 'PE Ratio (TTM) Corrected',
    'y': '1y Target Est',
    'size': 'Market Cap',
    'color': 'Industry'
}


def bubble_role_dropdown(role):
    bubble_children = []
    groups_ = groups if role == 'color' else [x for x in groups if x != 'Descriptive']
    for g_ in groups_:
        g_header = dbc.DropdownMenuItem(g_, header=True)
        bubble_children.append(g_header)
        sgs_ = group_dict[g_]['subgroups']
        for sg_ in sgs_:
            cols_ = subgroup_dict[sg_]['cols']
            radiolist = dbc.FormGroup(
                className='checklist-formgroup2',
                children=[
                    dcc.RadioItems(
                        options=[{'label': x, 'value': x} for x in cols_],
                        id=radio_dict[role][sg_]['radio-id'],
                        value=default_values[role] if default_values[role] in cols_ else None,
                        className='filter-checklist',
                        inputClassName='checklist-input',
                        labelClassName='checklist-label'
                    )
                ])
            if len(group_dict[g_]['subgroups']) == 1:
                bubble_children.append(radiolist)
            else:
                sg_header = dbc.DropdownMenuItem(sg_, header=True)
                bubble_children += [sg_header, radiolist]
    return get_dropdown(
        id_=role + '-bubble-dropdown',
        label_=role,
        children_=dbc.Form(
            children=bubble_children,
            className='bubble-dropdown-form'
        ),
        class_='dropdown-bubble'
    )


role_hidden_divs = {
    r: r + '-hidden-div' for r in roles
}


def role_hidden_div(role):
    return html.Div(
        id=role_hidden_divs[role],
        hidden=True,
        children=default_values[role]
        )


bubble_plot_layout = [
    html.Div(
        children=[bubble_role_dropdown(role) for role in roles],
        className='bubble-roles-dropdown-container'
    ),
    html.Div([role_hidden_div(r) for r in roles]),
    dcc.Graph(id='bubble_plot'),
    html.Div(id='selected-ticker')
]
