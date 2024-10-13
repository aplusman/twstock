# -*- coding: utf-8 -*-
import pandas as pd
import os
import traceback
from analytics import *
from stock import *

# Parameters
EPS_MIN_THRESHOLD = 3
DATA_DIR = './data'
INPUT_FILE = os.path.join(DATA_DIR, 'StockList1011.csv')
OUTPUT_FILE = os.path.join(DATA_DIR, 'outputToBuy.csv')

def create_data_directory():
    """Create the data directory if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)

def load_data(file_path):
    """Load stock data from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        required_columns = ['EPS(元) ▼', '代號', '名稱', '財報季度']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Missing required columns in the input data")
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        traceback.print_exc()
        raise

def filter_stocks(df):
    """Filter stocks based on EPS threshold."""
    interested_column_name = 'EPS(元) ▼'
    filtered_stocks = df[df[interested_column_name] >= EPS_MIN_THRESHOLD]
    return filtered_stocks

def analyze_stocks(filtered_stocks):
    """Analyze stocks and determine which ones to buy."""
    output_data = []
    buy_list = []
    idx_column = '代號'
    name_column = '名稱'
    quarter_column = '財報季度'
    eps_column = 'EPS(元) ▼'
    
    for index, row in filtered_stocks.iterrows():
        stock_idx = row[idx_column][2:-1]  # Remove leading '="' and trailing '"'
        
        try:
            stock = Stock(stock_idx)
            bfp = BestFourPoint(stock)
            buy_signal = bfp.best_four_point_to_buy()
            
            if buy_signal:
                stock_eps = row[eps_column]
                quarter_current = row[quarter_column]
                stock_name = row[name_column]
                print(f"You can buy the stock #{stock_idx} (closing price {stock.price[-1]} on {stock.date[-1]}) because {buy_signal}.")
                
                buy_list.append(int(stock_idx))
                output_data.append([stock_idx, stock_name, stock.price[-1], stock.date[-1], buy_signal, stock_eps, quarter_current])
        
        except Exception as e:
            print(f'Error occurs for the stock #{stock_idx}')
            print(e)
            traceback.print_exc()

    return buy_list, output_data

def save_output(output_data):
    """Save the analysis results to a CSV file."""
    df_output = pd.DataFrame(output_data, columns=['idx', 'name', 'price', 'date', 'reason', 'eps', 'eps_quarter'])
    df_output['pe_ratio'] = round(df_output['price'] / df_output['eps'], 2)
    df_output = df_output.sort_values('pe_ratio')
    
    df_output.to_csv(OUTPUT_FILE, index=False)
    print(f"Output data (*.csv) is saved to {OUTPUT_FILE}.")

def main():
    create_data_directory()
    df = load_data(INPUT_FILE)
    filtered_stocks = filter_stocks(df)
    buy_list, output_data = analyze_stocks(filtered_stocks)
    print('buy_list: ', buy_list)
    save_output(output_data)

# if __name__ == "__main__":
#     main()