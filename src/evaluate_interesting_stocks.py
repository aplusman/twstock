# -*- coding: utf-8 -*-
import pandas as pd
import os
import traceback
from analytics import *
from stock import *

# Parameters
EPS_MIN_THRESHOLD = 2.0
DATA_DIR = './data'
INPUT_FILE = os.path.join(DATA_DIR, 'interesting_stocks.csv')
OUTPUT_FILE = os.path.join(DATA_DIR, 'outputToBuy.csv')

stockID_column_name = 'stockID'

def create_data_directory():
    """Create the data directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)

def load_data(file_path): 
    return pd.read_csv(file_path)

def get_stock_id_list(pandas_data):
    stock_list = pandas_data[stockID_column_name].to_numpy()
    return stock_list

def analyze_stocks(filtered_stocks, stock_set):
    """Analyze stocks and determine which ones to buy."""
    output_data = []
    buy_list = []
    
    for stock_idx in filtered_stocks: 
        try:
            stock = Stock(str(stock_idx))
            bfp = BestFourPoint(stock)
            buy_signal = bfp.best_four_point_to_buy()
            
            if buy_signal:
                current_stock_info = stock_set[stock_set[stockID_column_name] == stock_idx]
                print(f"You can buy the stock #{stock_idx} (closing price {stock.price[-1]} on {stock.date[-1]}) because {buy_signal}.")

                buy_list.append(int(stock_idx))
                output_data.append([stock_idx, current_stock_info.iloc[0]['name'], stock.price[-1], stock.date[-1], buy_signal, \
                        current_stock_info.iloc[0]['volume'], \
                        current_stock_info.iloc[0]['EPS_quater_newest'], \
                        current_stock_info.iloc[0]['pe_ratio']])
        
        except Exception as e:
            print(f'Error occurs for the stock #{stock_idx}')
            print(e)
            traceback.print_exc()

    return buy_list, output_data

def save_output(output_data):
    """Save the analysis results to a CSV file."""
    df_output = pd.DataFrame(output_data, columns=['idx', 'name', 'price', 'date', 'reason', 'volume', 'eps', 'pe_ratio'])
    df_output = df_output.sort_values('volume', ascending=False)

    if len(df_output) > 20: 
        df_output = df_output.head(20) # Get the top 20 rows

    df_output = df_output.sort_values('pe_ratio', ascending=True)
    
    df_output.to_csv(OUTPUT_FILE, index=False)
    print(f"Output data (*.csv) is saved to {OUTPUT_FILE}.")

def evaluate_potential_stocks():
    create_data_directory()
    stock_set = load_data(INPUT_FILE)
    filtered_stocks = get_stock_id_list(stock_set)
    buy_list, output_data = analyze_stocks(filtered_stocks, stock_set)
    print('buy_list: ', buy_list)
    save_output(output_data)

# if __name__ == "__main__":
#     evaluate_potential_stocks()