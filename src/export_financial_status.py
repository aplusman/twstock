# -*- coding: utf-8 -*-

import pandas as pd
import time # sleep
from extract_yahoo_stocks import StockDataFetcher

input_stock_twsw_info_path = './data/twse_equities.csv'
output_stock_status_path = "./data/stock_closing_trade_info.csv"
output_my_interested_stocks = "./data/interesting_stocks.csv"

def get_stock_id_list():
    idx_type_column_name = 'type'
    idx_column_name = 'code'
    stock_name_column_name = 'name'
    df = pd.read_csv(input_stock_twsw_info_path)
    stock_list_temp = df[df[idx_type_column_name] == '股票']
    stockIDs = stock_list_temp[idx_column_name].to_numpy()
    stockNames = stock_list_temp[stock_name_column_name].to_numpy()
    return stockIDs, stockNames

def extract_interesting_stocks(stock_csv_path): 
    df = pd.read_csv(stock_csv_path)
    # My Equation
    # (1) volume > 100
    # (2) revenue_month_new > revenue_month_previous
    # (3) pe_ratio < 30
    # (4) eps_quater_new > 1.2 * eps_quater_previous > 0
    # (5) eps_quater_new + eps_quater_previous > 1.2 or eps_quater_new > 0.75
    filtered_df = df[df['volume'] > 100]
    filtered_df = filtered_df[filtered_df['pe_ratio'] < 30]
    filtered_df = filtered_df[filtered_df['revenue_newest'] > filtered_df['revenue_previous']]
    filtered_df = filtered_df[filtered_df['EPS_quater_previous'] > 0]
    filtered_df = filtered_df[filtered_df['EPS_quater_newest'] > 1.2 * filtered_df['EPS_quater_previous']]
    eps_condition = (filtered_df['EPS_quater_newest'] + filtered_df['EPS_quater_previous'] > 1.20) | (filtered_df['EPS_quater_newest'] > 0.75)
    filtered_df = filtered_df[eps_condition]
    filtered_df = filtered_df.sort_values('pe_ratio')
    filtered_df.to_csv(output_my_interested_stocks, index=False)
    print(f"Output data (*.csv) is saved to {output_my_interested_stocks}.")

def export_finantial_today_info():
    stockIDs, stockNames = get_stock_id_list()
    # Instantiate the StockDataFetcher and fetch data
    fetcher = StockDataFetcher(stockIDs, stockNames)
    fetcher.fetch_all_data()

    # Save the data to a CSV file
    fetcher.save_to_csv(output_stock_status_path)
    time.sleep(2)
    extract_interesting_stocks(output_stock_status_path)

# if __name__ == "__main__":
#     export_finantial_today_info()
    