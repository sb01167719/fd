"""
Scrape Corporate filings from NSE website.
Currently only FR filings implemented.
Usage: year
"""
''' --------------------------------------------------------------------------------------- '''

from fin_data.env import *
import os
import sys
from datetime import datetime
import pandas as pd
import pygeneric.http_utils as pyg_html_utils

OUTPUT_FOLDER = os.path.join(DATA_ROOT, '02_ind_cf/01_nse_fr_filings')

''' --------------------------------------------------------------------------------------- '''
def get_nse_fr_filings(year):
    date_now = datetime.now()
    assert int(year) <= date_now.year, 'Invalid Year %s' % year

    if int(year) == date_now.year:
        day_str   = ('%d' % date_now.day).zfill(2)
        month_str = ('%d' % date_now.month).zfill(2)
        from_to   = ['01-01-%d' % int(year),'%s-%s-%d' % (day_str, month_str, int(year))]
    else:
        from_to = ['01-01-%d' % int(year), '31-12-%d' % int(year)]

    print('Year %d between dates: %s ...' % (year, from_to))

    url_base = 'https://www.nseindia.com/api/corporates-financial-results?index=equities' + \
               '&from_date=%s&to_date=%s' % (from_to[0], from_to[1])

    res_df = pd.DataFrame()
    http_obj = pyg_html_utils.HttpDownloads(website='nse')
    for period in ['', 'HalfYearly', 'Annual', 'Others']:
        print('  [%s]: ' % period, end='')
        url = url_base + '&period=%s' % period
        cf_fr_json = http_obj.http_get_json(url)
        if len(cf_fr_json) == 0:
            print('no data, ignoring')
        else:
            df = pd.DataFrame(cf_fr_json)
            print('done, shape:', df.shape)
            res_df = pd.concat([res_df, df])

    if res_df.shape[0] == 0:
        print(f'  {year}: no fr filings found for the year')
        return

    res_df.reset_index(drop=True, inplace=True)
    n_unique_xbrls = len(res_df['xbrl'].unique())
    print('Final cf_fr_df shape: %s, Unique XBRLs: %d' % (res_df.shape, n_unique_xbrls))
    res_df.to_csv(os.path.join(OUTPUT_FOLDER, 'CF_FR_%s.csv' % year), index=False)
    return

''' --------------------------------------------------------------------------------------- '''
if __name__ == '__main__':
    year = datetime.now().year if len(sys.argv) == 1 else int(sys.argv[1])
    get_nse_fr_filings(year)