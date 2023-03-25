from db_connection import df
import pandas as pd
from table_formats import specifiers_dict
from si_prefix import si_format

default_ticker = 'MOMO'
# price button variants
periods = ['1M', '3M', '6M', '1Y', '5Y', 'MAX']
default_period = '1Y'
period_buttons_dict = {
    x: 'period-' + 'button-' + x for x in periods
}
fin_modes = ['Quarter', 'Year']
default_mode = 'Quarter'

ticker_dict = {
    t[0]: t[0] + ': ' + t[1] for t in list(zip(df.Ticker.tolist(), df.Name.tolist()))
}

# reading data on what fields to display in bottom cards and how to color the cards' background
ticker_info_fields = pd.read_csv('ticker_info_fields.csv', sep=';')
ticker_info_fields['field_id'] = ticker_info_fields['Field'].apply(lambda x: x.replace('.', '') + '-card-item')

# dictionary to name the blocks IDs for corresponding info
cards_id_dict = ticker_info_fields[['Field', 'field_id']].set_index('Field').transpose().iloc[0].to_dict()


# format values in Cards according to specifiers from specifiers_dict
def format_value(key_, val):
    if pd.isna(val):
        return ''
    else:
        specifier = specifiers_dict[key_] if key_ in specifiers_dict else ''
        if specifier != '' and 's' not in specifier:
            # return '{s}'.format(s=specifier)
            return ('{' + ':{}'.format(specifier) + '}').format(val)
            # return '{:{s}}'.format(val, s=specifier)
        elif 's' in specifier:
            return si_format(val, precision=2).replace(' ', '')
        else:
            return val
