# -*- coding: utf-8 -*-

import sys  # Import sys to handle command-line arguments

from extract_yahoo_stocks import StockDataFetcher

output_eps_path = "./data/eps_example.csv"

if __name__ == "__main__":

    # Check for command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python stock_data_fetcher.py <stock_id>")
        sys.exit(1)

    # Get the stock ID from the command-line argument
    stock_ids = sys.argv[1:]  # Get all arguments after the script name

    # Instantiate the StockDataFetcher and fetch data
    fetcher = StockDataFetcher(stock_ids)
    fetcher.fetch_data()

    # Save the data to a CSV file
    fetcher.save_to_csv(output_eps_path)