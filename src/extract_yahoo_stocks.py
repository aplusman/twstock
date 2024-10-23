# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

class StockDataFetcher:
    def __init__(self, stock_ids, names):
        self.stocks = {stock_id: [stock_id] for stock_id in stock_ids}
        self.stock_names = names
        self.url_eps = "https://tw.stock.yahoo.com/quote/{}/eps"
        self.url_revenue = "https://tw.stock.yahoo.com/quote/{}/revenue"
        self.session = requests.Session()
        self.target_column_names = ["stockID", "EPS_quater_previous", "EPS_quater_newest", 
                                    "pe_ratio", "volume", "revenue_previous", "revenue_newest"]

    def fetch_all_data(self):
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {executor.submit(self.fetch_data, stock_id): stock_id for stock_id in self.stocks.keys()}
            for count, future in enumerate(as_completed(futures), start=1):
                stock_id = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logging.error(f"Error fetching data for {stock_id}: {e}")
                if count % 10 == 0:
                    logging.info(f"Fetching data ... {count} / {len(self.stocks)}")

    def fetch_data(self, stock_id):
        eps_data = self.fetch_eps(stock_id)
        if eps_data:
            self.stocks[stock_id].extend(eps_data)
        revenue_data = self.fetch_revenue(stock_id)
        if revenue_data:
            self.stocks[stock_id].extend(revenue_data)

    def fetch_eps(self, stock_id):
        url = self.url_eps.format(stock_id)
        eps_data = []
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            eps_data = self.extract_eps_data(soup)
        except requests.RequestException as e:
            logging.error(f"Error fetching EPS data for {stock_id}: {e}")
        return eps_data

    def extract_eps_data(self, soup):
        stock_data = []
        section = soup.find("section", id="qsp-eps-table")
        if section:
            for itm in section.find_all("span", class_="")[1:5:2]:
                stock_data.insert(0, itm.getText())
            value = self.get_pe_ratio(soup)
            if value is not None:
                stock_data.append(value)
            value = self.get_volume(soup)
            if value is not None:
                stock_data.append(value)
        else:
            logging.warning(f"No EPS data found for {soup.title.string if soup.title else ''}.")
        return stock_data

    def get_pe_ratio(self, soup):
        try:
            span = soup.find("div", id="main-0-QuoteHeader-Proxy").find("div", class_="D(f) Fld(c) Ai(c) Fw(b) Px(8px) Bdendc($bd-primary-divider) Bdends(s) Bdendw(1px)").find("span", class_="Fz(16px) C($c-link-text) Mb(4px)")
            return float(span.getText().split(' ')[0]) if span else None
        except Exception as e:
            logging.error(f"Error extracting the PE ratio: {e}")
            return None

    def get_volume(self, soup):
        try:
            span = soup.find("div", id="main-0-QuoteHeader-Proxy").find("div", class_="D(f) Fld(c) Ai(c) Fw(b) Pend(8px) Bdendc($bd-primary-divider) Bdends(s) Bdendw(1px)").find("span", class_="Fz(16px) C($c-link-text) Mb(4px)")
            return float(span.getText().replace(',', '')) if span else 0
        except Exception as e:
            logging.error(f"Error extracting the volume: {e}")
            return 0

    def fetch_revenue(self, stock_id):
        url = self.url_revenue.format(stock_id)
        revenue_data = []
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            revenue_data = self.extract_revenue_data(soup)
        except requests.RequestException as e:
            logging.error(f"Error fetching revenue data for {stock_id}: {e}")
        return revenue_data

    def extract_revenue_data(self, soup):
        revenue_data = []
        section = soup.find("section", id="qsp-revenue-table")
        if section:
            try:
                for itm in section.find_all("span", class_="")[0:5:4]:
                    revenue_str = itm.getText().replace(",", "")
                    revenue_data.insert(0, int(revenue_str))
            except ValueError as e:
                logging.error(f"ValueError encountered: {e}")
        else:
            logging.warning(f"No revenue data found for {soup.title.string if soup.title else ''}.")
        return revenue_data

    def save_to_csv(self, filename):
        df = pd.DataFrame(self.stocks.values(), columns=self.target_column_names)
        df['name'] = pd.Series(self.stock_names)
        df = df.iloc[:,[0,7,1,2,3,4,5,6]]
        df.to_csv(filename, index=False)
        print(f"Data has been saved to {filename}")

# Example usage
# stock_ids = ['AAPL', 'GOOGL', 'MSFT']
# names = ['Apple', 'Google', 'Microsoft']
# fetcher = StockDataFetcher(stock_ids, names)
# fetcher.fetch_all_data()
# fetcher.save_to_csv('stock_data.csv')
