# -*- coding: utf-8 -*-

import pandas as pd
import realtime
from analytics import BestFourPoint
from stock import Stock, DATATUPLE

# Constants for input and output CSV file names
INPUT_CSV_NAME = './data/outputToBuy.csv'
OUTPUT_CSV_NAME = './data/outputToRealTimeBuy.csv'
IDX_COLUMN_NAME = 'idx'

def load_interested_stocks(input_csv_name):
    """Load the list of interested stocks from the CSV file."""
    df = pd.read_csv(input_csv_name)
    return df[IDX_COLUMN_NAME].to_numpy()  # Convert 'Idx' column to a 1-D array

def fetch_stock_data(stock_idx):
    """Fetch real-time stock data and return the stock object."""
    realtime_stock_info_set = realtime.get(str(stock_idx))
    realtime_stock_info = realtime_stock_info_set['info']
    realtime_stock = realtime_stock_info_set['realtime']
    stock = Stock(str(stock_idx))
    return stock, realtime_stock_info, realtime_stock

def create_new_data_entry(stock, realtime_stock):
    """Create a new data entry for the stock with the current price."""
    last_data_entry = stock.data[-1]
    new_data_entry = DATATUPLE(
        date=last_data_entry.date,
        capacity=last_data_entry.capacity,
        turnover=last_data_entry.turnover,
        open=float(realtime_stock['open']),
        high=float(realtime_stock['high']),
        low=float(realtime_stock['low']),
        close=float(realtime_stock['latest_trade_price']),  # Use the new close value
        change=last_data_entry.change,
        transaction=last_data_entry.transaction,
    )
    stock.data.append(new_data_entry)
    return stock

def analyze_stock(stock):
    """Analyze the stock and return buy recommendations if applicable."""
    bfp = BestFourPoint(stock)
    return bfp.best_four_point_to_buy()

def save_output(output_data):
    """Save the analysis results to a CSV file."""
    df_output = pd.DataFrame(output_data, columns=['idx', 'name', 'price', 'date', 'reason'])
    df_output.to_csv(OUTPUT_CSV_NAME, index=False)
    print(f"Output data (*.csv) is saved to {OUTPUT_CSV_NAME}.")

def main():
    """Main function to parse stock data and generate buy recommendations."""
    interested_stocks = load_interested_stocks(INPUT_CSV_NAME)
    buy_list = []
    output_data = []

    for stock_idx in interested_stocks:
        try:
            stock, realtime_stock_info, realtime_stock = fetch_stock_data(stock_idx)
            stock = create_new_data_entry(stock, realtime_stock)

            buy_signal = analyze_stock(stock)

            if buy_signal:
                print(f"#{stock_idx} {realtime_stock_info['name']} (real-time price {stock.price[-1]}) "
                      f"is recommended because {buy_signal}.")
                buy_list.append(int(stock_idx))
                output_data.append([stock_idx, realtime_stock_info['name'], stock.price[-1], stock.date[-1], buy_signal])

        except Exception as e:
            print(f'Error occurs for the stock #{stock_idx}: {e}')

    print('Buy list:', buy_list)
    save_output(output_data)

if __name__ == '__main__':
    main()