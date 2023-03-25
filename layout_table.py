import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from table_formats import format_list, header_format, cell_style, data_style, groups, group_dict, subgroup_dict, default_cols, \
    group_colors
from db_connection import df
from layout_functions import select_all_button, clean_all_button, apply_button, get_dropdown

cols = df.columns.tolist()


# func to create column dropdown-filters per given group
def column_dropdown_filter(group):
    apply = apply_button(id_=group_dict[group]['apply-button'])
    select_all = select_all_button(id_=group_dict[group]['select-button'])
    clean_all = clean_all_button(id_=group_dict[group]['clean-button'])
    sgs_ = group_dict[group]['subgroups']
    sg_items = []
    for sg_ in sgs_:
        cols_ = subgroup_dict[sg_]['cols']
        default_cols_ = [x for x in cols_ if x in default_cols]
        checklist = dbc.FormGroup(
            className='checklist-formgroup2',
            children=[dcc.Checklist(
                options=[{'label': x, 'value': x} for x in cols_],
                value=default_cols_,
                id=subgroup_dict[sg_]['checklist-name'],
                className='filter-checklist',
                inputClassName='checklist-input',
                labelClassName='checklist-label')])
        if len(sgs_) == 1:
            sg_items.append(checklist)
        else:
            sg_header = dbc.DropdownMenuItem(sg_, header=True)
            sg_items += [sg_header, checklist]
    if 'fin' in group.lower():
        dropdown_children = [select_all, clean_all] + \
                            [dbc.Form(
                                className='dropdown-form',
                                children=sg_items)] \
                            + [apply]
    else:
        dropdown_children = [select_all, clean_all] + sg_items + [apply]
    return get_dropdown(
        id_=group + '-cols-dropdown',
        label_=group,
        children_=dropdown_children,
        class_='dropdown-filter2',
        color_=group_colors[group]
    )


# DASH TABLE WITH TICKERS
data_table = dash_table.DataTable(
    id='table',
    columns=[x for x in format_list if x['id'] in default_cols],
    data=df.to_dict('records'),
    filter_action="native",
    sort_action="native",
    sort_mode="multi",
    row_selectable="single",
    fixed_rows={'headers': True},
    fixed_columns={'headers': True, 'data': 1},
    page_action='native',
    page_size=30,
    style_table={
        'minWidth': '100%',
        'overflowY': 'auto',
        'height': 550,
        'maxHeight': 550
    },
    style_header={
        'fontWeight': 'bold',
        'textAlign': 'center',
    },
    merge_duplicate_headers=True,
    style_header_conditional=header_format,
    style_cell_conditional=cell_style,
    style_data_conditional=data_style
)

table_layout = [
        html.Div(
            className='column-filters',
            children=[column_dropdown_filter(gr) for gr in groups]
        ),
        data_table,
        html.Div(id='columns', hidden=True, children=default_cols),
            ]
