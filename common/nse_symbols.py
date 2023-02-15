"""
Symbols for NSE indices & historic symbol changes
"""

''' --------------------------------------------------------------------------------------- '''
import os
import sys
import pandas as pd

CONFIG_ROOT = os.getenv('CONFIG_ROOT')
PATH_1 = os.path.join(os.getenv('CONFIG_ROOT'), '01_nse_symbols')
PATH_2 = os.path.join(os.getenv('CONFIG_ROOT'), '02_nse_indices')

''' --------------------------------------------------------------------------------------- '''
def get_symbols(file_list, series=None):
    symbols = pd.DataFrame()
    for f in file_list:
        df = pd.read_csv(os.path.join(PATH_2, f'{f}.csv'))
        if 'Group' in df.columns:
            df.rename(columns={'Group':'Series'}, inplace=True)
        symbols = pd.concat([symbols, df[['Series', 'Symbol']]])
    if series is not None:
        symbols = symbols.loc[symbols.Series == series].reset_index(drop=True)
    return symbols['Symbol'].unique()

def get_symbol_changes(cutoff_date='2018-01-01'):
    df = pd.read_csv(os.path.join(PATH_1, f'symbolchange.csv'))
    df['Date of Change'] = pd.to_datetime(df['Date of Change'])
    df['Date of Change'] = pd.to_datetime(df['Date of Change'], format="%Y-%m-%d")
    df = df.loc[df['Date of Change'] >= cutoff_date].reset_index(drop=True)
    df = df.sort_values(by='Date of Change').reset_index(drop=True)
    return df[['Date of Change', 'Old Symbol', 'New Symbol']]

def get_older_symbols(symbol):
    df = get_symbol_changes()
    df = df.loc[df['New Symbol'] == symbol].reset_index(drop=True)
    return list(df['Old Symbol'].unique())

def get_isin(symbol):
    df = pd.read_csv(os.path.join(PATH_1, f'EQUITY_L.csv'))
    df = df.loc[df['Symbol'] == symbol].reset_index(drop=True)
    assert df.shape[0] == 1
    return df['ISIN'].values[0]

# ----------------------------------------------------------------------------------------------
if __name__ == '__main__':
    print('Testing nse_config ... ', end='')

    assert len(get_symbols(['ind_nifty50list'])) == 50
    assert len(get_symbols(['ind_nifty100list'])) == 100
    assert len(get_symbols(['ind_nifty50list', 'ind_nifty100list'])) == 100

    sc_df = get_symbol_changes()
    sc_df = sc_df.loc[sc_df['Old Symbol'].isin(['CADILAHC', 'LTI'])]
    print(sc_df)
    assert [d.astype(str)[0:10] for d in sc_df['Date of Change'].values] == \
           ['2022-03-07', '2022-12-05']

    assert get_older_symbols('ZYDUSLIFE') == ['CADILAHC']
    assert get_older_symbols('LTIM') == ['LTI']

    assert get_isin('ZYDUSLIFE') == 'INE010B01027'
    print('All OK')