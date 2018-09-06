import pandas as pd
import numpy as np

import scrape_finviz as sf

FILEPATH = '/home/nate/Dropbox/data/finviz/'


def load_group_df(group):
    """
    group should be one of ['sector', 'industry', 'country', 'capitalization']
    """
    latest_date = sf.get_latest_dl_date().strftime('%Y-%m-%d')
    filename = FILEPATH + latest_date + '_finviz_' + group + '.csv'
    df = pd.read_csv(filename)
    return df


def load_stockdata():

    datetime_cols = ['Earnings Date',
                    'IPO Date']
    latest_date = sf.get_latest_dl_date().strftime('%Y-%m-%d')
    filename = FILEPATH + latest_date + '_finviz_stockdata.csv'
    df = pd.read_csv(filename, parse_dates=datetime_cols, infer_datetime_format=True)
    # df[datetime_cols] = df[datetime_cols].applymap(pd.to_datetime)
