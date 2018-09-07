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
    df.set_index('Ticker', inplace=True)
    return df


industry_df = load_group_df('industry')

stock_df = load_stockdata()

# TODO: check if SPY bullish

spy_qtr = stock_df.loc['SPY']['Performance (Quarter)']

# find stocks outperforming SPY by 4% -- assuming it means performance is + 0.04?

industries = industry_df[industry_df['Performance (Quarter)'] >= spy_qtr + 0.04]
industry_names = set(industries['Name'].tolist())
industries.loc[:, 'min P/E'] = industries[['P/E', 'Forward P/E']].min(axis=1)

# TODO: get bullish trend measure from industries

# get possible stocks
stocks = stock_df[stock_df['Industry'].isin(industry_names)]
stocks = stocks[stocks['Volume'] > 200000]
# check if stock is bullish with 40 day MA above 120 day MA
# use 50 and 200 day for now
stocks = stocks[stocks['50-Day Simple Moving Average'] > stocks['200-Day Simple Moving Average']]

# check if stock is at/above upper donchian channel (20-day rolling MA)

# calculate fair value and make sure there is a 20% gap
# 4x latest quarterly EPS * lowest P/E or fwd P/E from industry
# OR use ttm EPS -- seems like a better idea to me
# can only calc FV for positive earnings
stocks.loc[:, 'industry min P/E'] = stocks['Industry'].apply(lambda x: industries[industries['Name'] == x]['min P/E'].values[0])
stocks.loc[:, 'fair value'] = stocks['EPS (ttm)'] * stocks['industry min P/E']
# need to add a small amount in case fair value is 0
stocks.loc[:, 'fair value price pct diff'] = stocks.apply(lambda x: (x['fair value'] - x['Price']) / (x['Price'] + 0.001), axis=1)
stocks.loc[stocks['EPS (ttm)'] <= 0, ['fair value', 'fair value price pct diff']] = np.nan
top_fv_diffs = stocks[stocks['fair value price pct diff'] >= 0.2].sort_values(by='fair value price pct diff')
top_fv_diffs[top_fv_diffs['Performance (Month)'] > 0][['fair value price pct diff', 'EPS (ttm)', 'EPS growth this year',
       'EPS growth next year', 'EPS growth past 5 years',
       'EPS growth next 5 years', 'Sales growth past 5 years',
       'EPS growth quarter over quarter', 'Sales growth quarter over quarter',
       'Institutional Ownership', 'Float Short', 'Performance (Month)', 'Performance (Quarter)', 'Average True Range', '52-Week High', 'Target Price', 'Price']]

# use '50-Day Simple Moving Average',
    #    '200-Day Simple Moving Average'
    # to get if stock bullish or not

# risk is 1-3% of account -- assume 10k account to start, so risk at $100
# divide risk by 7x 20-day ATR
# stop loss at 7x 20-day ATR
