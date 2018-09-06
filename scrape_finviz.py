import requests as req
from lxml import html
from bs4 import BeautifulSoup as bs
import pandas as pd

from fake_useragent import UserAgent

ua = UserAgent(fallback='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36')

sector_data_url = 'https://finviz.com/groups.ashx?g=sector&v=152&o=name&c=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26'
industry_data_url = 'https://finviz.com/groups.ashx?g=industry&v=152&o=name&c=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26'


def get_group_df(url):
    """
    gets info from 'group tables', e.g. industry from finviz.com
    """
    res = req.get(url, headers={'user-agent': ua.random})
    # xpath not working for some reason... : /html/body/table[3]/tbody/tr[5]/td/table
    # tree = html.fromstring(res.content)
    # table = tree.xpath('//table')
    soup = bs(res.content, 'lxml')
    tables = soup.findAll('table')
    # 7th table for now
    data_table = tables[6]
    rows = data_table.findAll('tr')
    # labels = rows[0].text.split('\n')[1:-1]  # first and last are empty
    labels = [t.text for t in rows[0].findAll('td')]
    datadict = {}
    for r in rows[1:]:
        data = [t.text for t in r.findAll('td')]
        link = r.findAll('td')[1].find('a').attrs['href']
        datadict.setdefault('link', []).append('https://finviz.com/' + link)
        for l, d in zip(labels, data):
            datadict.setdefault(l, []).append(d)

    df = pd.DataFrame(datadict)

    abbrev_cols = ['Avg Volume', 'Market Cap', 'Volume']
    pct_cols = ['Change',
                'Dividend',
                'EPS next 5Y',
                'EPS past 5Y',
                'Float Short',
                'Perf Half',
                'Perf Month',
                'Perf Quart',
                'Perf Week',
                'Perf YTD',
                'Perf Year',
                'Sales past 5Y']
    numeric_cols = ['Fwd P/E',
                    'P/B',
                    'P/C',
                    'P/E',
                    'P/FCF',
                    'P/S',
                    'PEG',
                    'Recom',
                    'Rel Volume']
    df[abbrev_cols] = df[abbrev_cols].applymap(clean_abbreviations)
    df[pct_cols] = df[pct_cols].applymap(clean_pcts)
    df[numeric_cols] = df[numeric_cols].astype('float')
    df['Stocks'] = df['Stocks'].astype('int')
    df.drop('No.', inplace=True, axis=1)

    return df


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


sector_df = get_group_df(sector_data_url)
industry_df = get_group_df(industry_data_url)


stocks_url = 'https://finviz.com/screener.ashx?v=152&f=sec_basicmaterials&r=1&c=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70'
stocks_url = 'https://finviz.com/screener.ashx?v=152&r={}&c=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70'

# the way it works is: 20 stocks are displayed per page, and the r= paramater in the url tells where to start listing with the stocks
res = req.get(stocks_url.format('1'), headers={'user-agent': ua.random})
soup = bs(res.content, 'lxml')
# get last page number to get pages that need to be iterated through
last_page_num = int(soup.findAll('a', {'class': 'screener-pages'})[-1].text)
# the last page should be the (last page number - 1) * 20 + 1
last_r = (last_page_num - 1) * 20 + 1
for p in range


# for examining page
with open('test.html', 'wb') as f:
    f.writelines(res)
