import pandas as pd
import numpy as np

import scrape_finviz as sf

FILEPATH = '/home/nate/Dropbox/data/finviz/'


def clean_pcts(x):
    """
    the 'Chg. %' column and others have entries like +1.24%
    """
    # if not enough data, will be '-' with investing.com
    if x == '-' or pd.isnull(x):
        return np.nan
    elif x == 'unch':
        return float(0)
    elif type(x) == float:
        return x

    new_x = x.replace('+', '')
    new_x = new_x.replace('%', '')
    new_x = float(new_x) / 100
    return new_x


def clean_abbreviations(x):
    """
    replaces K with 000, M with 000000, B with 000000000
    """
    # a few entries in Revenue were nan
    if pd.isnull(x):
        return np.nan
    elif 'K' in x:
        return int(float(x[:-1]) * 1e3)
    elif 'M' in x:
        return int(float(x[:-1]) * 1e6)
    elif 'B' in x:
        return int(float(x[:-1]) * 1e9)
    else:
        return int(x)


def load_group_df(group):
    """
    group should be one of ['sector', 'industry', 'country', 'capitalization']
    """
    pct_cols = ['Change',
                'Dividend Yield',
                'EPS growth next 5 years',
                'EPS growth past 5 years',
                'Float Short',
                'Performance (Half Year)',
                'Performance (Month)',
                'Performance (Quarter)',
                'Performance (Week)',
                'Performance (Year To Date)',
                'Performance (Year)',
                'Sales growth past 5 years']

    group = 'industry'
    latest_date = sf.get_latest_dl_date().strftime('%Y-%m-%d')
    filename = FILEPATH + latest_date + '_finviz_' + group + '.csv'
    df = pd.read_csv(filename)
    df[pct_cols] = df[pct_cols].applymap(clean_pcts)
    df.drop('No.', inplace=True, axis=1)

    return df
