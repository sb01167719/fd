"""
test nse_spot.py
"""
''' --------------------------------------------------------------------------------------- '''

import os
from datetime import datetime, timedelta
import pygeneric.datetime_utils as datetime_utils
import fin_data.nse_pv.nse_spot as nse_spot
from fin_data.common import nse_config
from fin_data.nse_pv import get_hpv, get_dr, process_dr, nse_spot

LOG_DIR = os.path.join(os.getenv('LOG_ROOT'), '01_fin_data/01_nse_pv')

''' --------------------------------------------------------------------------------------- '''
def test_all():
    import fin_data.nse_pv.get_hpv as get_hpv

    ''' ----------------------------------------------------------------------------------- '''
    print('\nTesting NseSpotPVData basics ...')
    symbols = ['ASIANPAINT', 'BRITANNIA', 'HDFC', 'ICICIBANK', 'IRCON', 'IRCTC',
               'JUBLFOOD', 'TATASTEEL', 'ZYDUSLIFE']
    nse_spot_obj = nse_spot.NseSpotPVData(verbose=False)

    def check_data(symbol_list, dates):
        print('Checking for dates', dates, '...')
        for symbol in symbol_list:
            print(f'  {symbol} ...', end=' ')

            df1 = nse_spot_obj.get_pv_data(symbol, series='EQ', from_to=dates)
            df2 = get_hpv.get_pv_data(symbol, from_to=dates)
            df1.to_csv(os.path.join(LOG_DIR, 'nse_spot_df1.csv'), index=False)
            df2.to_csv(os.path.join(LOG_DIR, 'nse_spot_df2.csv'), index=False)
            assert abs(df1.shape[0] - df2.shape[0]) <= 5, "%d / %d" % (df1.shape[0], df2.shape[0])

            if df1.shape[0] != df2.shape[0]:
                common_dates = list(set(df1['Date']) & set(df2['Date']))
                df1 = df1.loc[df1['Date'].isin(common_dates)].reset_index(drop=True)
                df2 = df2.loc[df2['Date'].isin(common_dates)].reset_index(drop=True)
            for c in ['Open', 'High', 'Low', 'Close', 'Prev Close',
                      'Volume', 'Delivery Volume', 'No Of Trades']:
                assert (~(abs(df1[c] - df2[c]) < 0.5)).sum() == 0, \
                    'Column: %s: %d' % (c, (~(abs(df1[c] - df2[c]) < 0.5)).sum())

            for c in ['Traded Value']:
                assert (~(abs(df1[c] - df2[c]) < 100)).sum() <= 1, \
                    'Column: %s: %d' % (c, (~(abs(df1[c] - df2[c]) < 100)).sum())

            print('OK')
        return

    end_date = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
    check_data(symbols, ['2018-01-01', '2018-12-31'])
    check_data(symbols, ['2019-01-01', '2019-12-31'])
    check_data(symbols, ['2020-01-01', '2020-12-31'])
    check_data(symbols, ['2021-01-01', '2021-12-31'])
    check_data(symbols, ['2022-01-01', '2022-12-31'])
    check_data(symbols, ['2023-01-01', end_date])
    check_data(symbols, ['2018-01-01', end_date])

    ''' ----------------------------------------------------------------------------------- '''
    print('\nTesting NseSpotPVData().get_pv_data (for multiple symbols) ...')
    """ To do: Verify 52_Wk_H/L"""
    multi_df = nse_spot_obj.get_pv_data(symbols, from_to=['2018-01-01', end_date])
    for symbol in symbols:
        print(f'  {symbol} ...', end=' ')
        df1 = multi_df.loc[multi_df['Symbol'] == symbol].reset_index(drop=True)
        df2 = get_hpv.get_pv_data(symbol, from_to=['2018-01-01', end_date])

        assert abs(df1.shape[0] - df2.shape[0]) <= 5, "%d / %d" % (df1.shape[0], df2.shape[0])

        if df1.shape[0] != df2.shape[0]:
            common_dates = list(set(df1['Date']) & set(df2['Date']))
            df1 = df1.loc[df1['Date'].isin(common_dates)].reset_index(drop=True)
            df2 = df2.loc[df2['Date'].isin(common_dates)].reset_index(drop=True)

        for c in ['Open', 'High', 'Low', 'Close', 'Prev Close',
                  'Volume', 'Delivery Volume', 'No Of Trades']:
            assert (~(abs(df1[c] - df2[c]) < 0.5)).sum() == 0, \
                'Column: %s: %d' % (c, (~(abs(df1[c] - df2[c]) < 0.5)).sum())

        for c in ['Traded Value']:
            assert (~(abs(df1[c] - df2[c]) < 100)).sum() <= 1, \
                'Column: %s: %d' % (c, (~(abs(df1[c] - df2[c]) < 100)).sum())

        print('OK')

    ''' ----------------------------------------------------------------------------------- '''
    print('\nTesting get_index_pv_data ... ', end='')
    pv_data = nse_spot_obj.get_index_pv_data('NIFTY 50', ['2023-04-01', '2023-05-02'])
    assert pv_data.shape[0] == 18 and pv_data.shape[1] == 13
    pv_data = nse_spot_obj.get_index_pv_data('NIFTY 50', ['2023-04-01', None])
    assert pv_data.shape[0] > 0 and pv_data.shape[1] == 13
    pv_data = nse_spot_obj.get_index_pv_data(['NIFTY 50', 'NIFTY MIDCAP 150', 'NIFTY IT'],
                                             ['2023-04-01', '2023-05-02'])
    assert pv_data.shape[0] == 54 and pv_data.shape[1] == 13
    pv_data = nse_spot_obj.get_index_pv_data('NIFTY 50', ['2010-01-01', '2019-12-31'])
    assert pv_data.shape[0] == 2443 and pv_data.shape[1] == 13
    print('OK')

    ''' ----------------------------------------------------------------------------------- '''
    print('\nTesting get_etf_pv_data ... ', end='')
    pv_data = nse_spot_obj.get_etf_pv_data('NIFTYBEES', ['2023-04-01', '2023-05-02'])
    assert pv_data.shape[0] == 18 and pv_data.shape[1] == 17, pv_data.shape
    pv_data = nse_spot_obj.get_etf_pv_data('NIFTYBEES', ['2023-04-01', None])
    assert pv_data.shape[0] > 0 and pv_data.shape[1] == 17, pv_data.shape
    pv_data = nse_spot_obj.get_etf_pv_data(['NIFTYBEES', 'ITBEES', 'CPSEETF'],
                                           ['2023-04-01', '2023-05-02'])
    assert pv_data.shape[0] == 54 and pv_data.shape[1] == 17, pv_data.shape
    print('OK')

    ''' ----------------------------------------------------------------------------------- '''
    print('\nTesting get_spot_quote ... ', end='')
    keys  = ['Symbol', 'Date', 'Open', 'High', 'Low', 'Close', 'previousClose', 'lastPrice', 'pChange']
    assert list(nse_spot.get_spot_quote('ASIANPAINT').keys()) == keys
    assert list(nse_spot.get_spot_quote('NIFTY 50', index=True).keys()) == keys
    res = nse_spot.get_spot_quote(['NIFTY IT', 'NIFTY MIDCAP 150', 'NIFTY AUTO'], index=True)
    assert type(res) == list and len(res) == 3 and list(res[2].keys()) == keys
    print('OK')

    ''' ----------------------------------------------------------------------------------- '''
    print('\nTesting for partly paid symbol ...', end=' ')
    df_pp = nse_spot_obj.get_pv_data('AIRTELPP', series='E1', from_to=['2022-10-01', '2022-10-10'])
    assert df_pp.shape[0] == 5, 'partly paid Not OK'
    df_pp = nse_spot_obj.get_pv_data(['BHARTIARTL', 'AIRTELPP'], from_to=['2022-10-01', '2022-10-10'])
    assert df_pp.shape[0] == 5, 'partly paid Not OK'
    df_pp = nse_spot_obj.get_pv_data(['BRITANNIA'], from_to=['2022-10-01', '2022-10-10'])
    assert df_pp.shape[0] == 5, 'partly paid Not OK'
    print('OK')

    ''' ----------------------------------------------------------------------------------- '''
    ''' Include after performance problem is fixed '''
    print('\nTesting for NseSpotPVData().get_pv_data (for large # of multiple symbols) ...')
    datetime_utils.time_since_last(0)
    import fin_data.common.nse_symbols as nse_symbols
    symbols = nse_symbols.get_symbols(['ind_nifty50list', 'ind_niftynext50list'])
    # symbols = nse_symbols.get_symbols(['ind_nifty500list', 'ind_niftymicrocap250_list'])
    df = nse_spot_obj.get_pv_data(symbols, from_to=['2019-01-01', None], verbose=True)
    print('Done. time check:', datetime_utils.time_since_last(0), 'seconds\n')

    return True

''' --------------------------------------------------------------------------------------- '''
if __name__ == '__main__':
    """
    Doing / To do: move everything to NseSpotPVData
    - live quote --> get all in one get and don't refresh if last get > 1 min old
    """
    test_all()