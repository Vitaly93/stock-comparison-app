import pandas as pd

df = pd.read_csv('col_dict.csv', sep=';')
groups = df.group.unique().tolist()

# colors for group headers and dropdown-filters
group_colors = df[['group', 'group_color_hex']].drop_duplicates().set_index('group').transpose().iloc[0].to_dict()

# count of subgroups in group to define milti header levels
subgroup_count = df.groupby('group')['subgroup'].nunique().to_dict()

format_list = []
for x in list(zip(df.column, df.deletable, df.type, df.specifier_full, df.group, df.subgroup)):
    if subgroup_count[x[4]] == 1:
        d = {'name': ["", x[4], x[0]], 'id': x[0]}
    else:
        d = {'name': [x[4], x[5], x[0]], 'id': x[0]}
    if x[1] == 1: d['deletable'] = True
    if x[2] == 'numeric': d['type'] = 'numeric'
    if not pd.isna(x[3]): d['format'] = {'specifier': x[3]}
    format_list.append(d)

header_format = []
for x in list(zip(df.column, df.group, df.group_color_hex)):
    d_ = {'if': {
        'column_id': x[0],
        'header_index': 2
    }, 'backgroundColor': x[2], 'color': '#FFF' if x[2] != '#FFF' else '#000'}
    header_format.append(d_)

cell_style = []
for col in df.column.tolist():
    name_length = len(col)
    pixel_for_char = 9
    pixel = 10 + name_length * pixel_for_char
    pixel = str(pixel) + "px"
    cell_style.append({'if': {'column_id': col}, 'minWidth': pixel})

data_style = []
for col in df[df['sign.Positive'] == '+'].column.tolist():
    d1 = {
        'if': {
            'column_id': col,
            'filter_query': '{{{}}} < 0'.format(col)
        },
        'color': '#FF0000'
    }
    d2 = {
        'if': {
            'column_id': col,
            'filter_query': '{{{}}} > 0'.format(col)
        },
        'color': '#008000'
    }
    data_style += [d1, d2]

default_cols = df[df.default == True].column.tolist()

# dicts to check which subgroups, columns and checklist-names correspond to a group
group_dict = {}
subgroup_dict = {}
for g in df.group.unique():
    sgs = df[df.group == g].subgroup.unique().tolist()
    group_dict[g] = {
        'subgroups': sgs,
        'select-button': 'select-all-' + g + '-cols',
        'clean-button': 'clean-all-' + g + '-cols',
        'apply-button': 'apply-' + g + '-cols'
    }
    for sg in sgs:
        subgroup_dict[sg] = {
            'cols': df[(df.group == g) & (df.subgroup == sg)].column.tolist(),
            'checklist-name': g + '-' + sg + '-cols-checklist',
        }

specifiers_dict = df[['column', 'specifier_full']].set_index('column').dropna().transpose().iloc[0].to_dict()