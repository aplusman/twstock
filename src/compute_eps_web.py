

# https://gist.github.com/gary136/20970376b341f4199979a4570db5a113

import requests
import pandas as pd
from io import StringIO
from datetime import datetime, timedelta

def revr(data, nmbr):
    cols = data.columns.tolist()
    cols = cols[nmbr:] + cols[:nmbr]
    data = data[cols]
    return data
    
def siiPrice(str_date):
    url = f'https://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date={str_date}&type=ALL'
    print(url)
    r = requests.get(url)
    if r.text=='':
        return None
    
    df = pd.read_csv(StringIO(r.text.replace("=", "")), 
                header=["證券代號" in l for l in r.text.split("\n")].index(True)-1)
    df.drop(['Unnamed: 16','最後揭示買價', '最後揭示買量', '最後揭示賣價', '最後揭示賣量'], axis=1, inplace=True)
    for i in ['成交股數', '成交筆數', '成交金額', '開盤價', '最高價', '最低價', '收盤價', '漲跌價差', '本益比']:
        df[i] = df[i].apply(lambda x: pd.to_numeric(x.replace(",", ""), errors='coerce') if type(x)!=float else x)
    df['股價日期'] = datetime(int(str_date[:4]),int(str_date[4:6]),int(str_date[6:]),0,0,0)
    df = revr(df,-1)
    return df

def otcPrice(str_date):
    url = f'https://www.tpex.org.tw/web/stock/aftertrading/otc_quotes_no1430/stk_wn1430_result.php?l=zh-tw&o=htm&d={str_date}&se=AL&s=0,asc,0'
    r = requests.get(url)
    if r.text=='':
        return None

    df = pd.read_html(StringIO(r.text))[0]
    df.columns = df.columns.get_level_values(1)
    df.drop(['次日漲停價','次日跌停價'], axis=1, inplace=True)
    spl = str_date.split('/')
    df['股價日期'] = datetime(int(spl[0])+1911,int(spl[1]),int(spl[2]),0,0,0)
    df = revr(df,-1)
    return df

def TwPrice(dt, mkt):

    mkt_mapping = {'上市':'sii','上櫃':'otc'}
    dt_mapping = {}
    if '/' not in dt:
        dt_mapping['sii_date']=dt
        dt_mapping['otc_date']=f'{int(dt[:-4])-1911}/{dt[-4:-2]}/{dt[-2:]}'
    else:
        dt_mapping['sii_date']=f'{int(dt[:-6])+1911}{dt[-5:-3]}{dt[-2:]}'
        dt_mapping['otc_date']=dt
    
    mkt = mkt_mapping[mkt]
    dt = dt_mapping[f'{mkt}_date']
    # example of sii_date: 20241011
    # example of otc_date: 113/10/11 (assuming dt is in the format of YYYYMMDD).
    price = siiPrice(dt) if mkt=='sii' else otcPrice(dt)
    return price
price1 = TwPrice("20241011", "上市")
# price1 = TwPrice("20241011", "上櫃")
print(price1['本益比'][3])