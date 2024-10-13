# -*- coding: utf-8 -*-
import pandas as pd

from analytics import *
from stock import *

# download link
# https://goodinfo.tw/tw2/StockList.asp?MARKET_CAT=%E7%86%B1%E9%96%80%E6%8E%92%E8%A1%8C&INDUSTRY_CAT=%E5%B9%B4%E5%BA%A6EPS%E6%9C%80%E9%AB%98%40%40%E6%AF%8F%E8%82%A1%E7%A8%85%E5%BE%8C%E7%9B%88%E9%A4%98+%28EPS%29%40%40%E5%B9%B4%E5%BA%A6EPS%E6%9C%80%E9%AB%98&SHEET=%E5%B9%B4%E7%8D%B2%E5%88%A9%E8%83%BD%E5%8A%9B&SHEET2=%E7%8D%B2%E5%88%A9%E8%83%BD%E5%8A%9B
df = pd.read_csv('./data/StockList1011.csv')
quarter_current_in_utf8_chinese='財報季度'
quarter_current = df.iloc[0][quarter_current_in_utf8_chinese]
print('\nStock List generally recorded in {}\n'.format(quarter_current))
print(df.head(3))

###############
interested_column_name='EPS(元) ▼'
idx_in_utf8_chinese='代號'
stock_name_in_utf8_chinese='名稱'
eps_min_threshold=3
# roe_min_threshold=0
result_threshold = df[df[interested_column_name] >= eps_min_threshold]

#########
# Initialize a list to hold the data
OutputData = []
buy_list = []
for index, row in result_threshold.iterrows():
        
    stock_idx_str = None
    stock_idx_str = row[idx_in_utf8_chinese]

    # Remove the leading '="' and trailing '"'
    stock_idx_str = [stock_idx_str[2:-1]] # stored in an array
    
    try: 
        bfp = BestFourPoint(Stock(stock_idx_str[0]))
        buy = bfp.best_four_point_to_buy()
        if buy:
            s = Stock(stock_idx_str[0])
            stock_current_eps = row[interested_column_name]
            eps_quarter_current = row[quarter_current_in_utf8_chinese]
            stock_name_str = row[stock_name_in_utf8_chinese]
            print("You can buy the stock #{} (closing price {} on {}) because {}.".format(stock_idx_str[0], \
                                        s.price[-1], \
                                        s.date[-1], \
                                        buy))

            buy_list.append(int(stock_idx_str[0]))
            OutputData.append([stock_idx_str[0], stock_name_str, \
                            s.price[-1], s.date[-1], buy, \
                            stock_current_eps, eps_quarter_current])

    except Exception as e:
        print('Error occurs for the stock #', stock_idx_str)
        print(e)
        
print('buy_list: ', buy_list)

# Create a DataFrame from the collected data
dfOutput = pd.DataFrame(OutputData, columns=['idx', 'name', 'price', 'date', 'reason', 'eps', 'eps_quarter'])
df_temp = dfOutput[['eps']].copy()
df_temp.columns = df_temp.columns.str.replace('eps', 'pe_ratio')
dfOutput.loc[:, 'pe_ratio'] = df_temp.loc[:, 'pe_ratio']
for stock_ith in range(len(dfOutput)):
    stock_pe_ratio = float(dfOutput.loc[stock_ith, 'price']) / float(dfOutput.loc[stock_ith, 'eps'])
    dfOutput.at[stock_ith, 'pe_ratio'] = round(stock_pe_ratio, 2)
dfOutput = dfOutput.sort_values('pe_ratio')
# Save the DataFrame to a CSV file
dfOutput.to_csv('./data/outputToBuy.csv', index=False)

print("Output data (*.csv) is saved.")
