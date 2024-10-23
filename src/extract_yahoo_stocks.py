# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import pandas as pd

class StockDataFetcher:
    def __init__(self, stock_ids, names):
        """
        Initialize the StockDataFetcher with a list of stock IDs.
        
        :param stock_ids: List of stock IDs provided by the user.
        """
        self.stocks = {stock_id: [stock_id] for stock_id in stock_ids}  
        self.stock_names = [name for name in names]
        self.stock_names_to_baught = []
        self.url_eps = "https://tw.stock.yahoo.com/quote/{}/eps"
        self.url_revenue = "https://tw.stock.yahoo.com/quote/{}/revenue"
        self.session = requests.Session()  
        self.target_column_names = ["stockID", "EPS_quater_previous", "EPS_quater_newest", \
                        "pe_ratio", "volume", "revenue_previous", "revenue_newest"]

    def fetch_data(self):
        """Fetch EPS and revenue data for all stocks sequentially."""
        count_stocks = 0
        for stock_id in self.stocks.keys():
            eps_data = self.fetch_eps(stock_id)
            if eps_data:
                self.stock_names_to_baught.append(self.stock_names[count_stocks])
                self.stocks[stock_id].extend(eps_data)
            self.fetch_revenue(stock_id)
            count_stocks += 1
            if count_stocks % 10 == 0: 
                print("fetching data ... ", count_stocks, " / ", len(self.stocks.keys()))
            # if count_stocks > 3:
            #     break

    def fetch_eps(self, stock_id):
        """Fetch EPS data for a given stock ID."""
        url = self.url_eps.format(stock_id)
        eps_data = 0
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            eps_data = self.extract_eps_data(soup)
            # self.stocks[stock_id].extend(eps_data)

        except requests.RequestException as e:
            print(f"Error fetching EPS data for {stock_id}: {e}")

        return eps_data

    def extract_eps_data(self, soup):
        """Extract EPS data from the soup object."""
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
            print(f"No EPS data found.")

        return stock_data

    def get_pe_ratio(self, soup):
        """Extract the PE ratio from the soup object."""
        try:
            span = soup.find("div", id="main-0-QuoteHeader-Proxy").find("div", class_="D(f) Fld(c) Ai(c) Fw(b) Px(8px) Bdendc($bd-primary-divider) Bdends(s) Bdendw(1px)").find("span", class_="Fz(16px) C($c-link-text) Mb(4px)")
            return float(span.getText().split(' ')[0]) if span else None
        except Exception as e:
            print(f"Error extracting the PE ratio: {e}")
            return None

    def get_volume(self, soup):
        """Extract the volume from the soup object."""
        try:
            span = soup.find("div", id="main-0-QuoteHeader-Proxy").find("div", class_="D(f) Fld(c) Ai(c) Fw(b) Pend(8px) Bdendc($bd-primary-divider) Bdends(s) Bdendw(1px)").find("span", class_="Fz(16px) C($c-link-text) Mb(4px)")
            return float(span.getText().replace(',', '')) if span else 0
        except Exception as e:
            print(f"Error extracting the volume: {e}")
            return 0

    def fetch_revenue(self, stock_id):
        """Fetch revenue data for a given stock ID."""
        url = self.url_revenue.format(stock_id)
        try:
            response = self.session.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            revenue_data = self.extract_revenue_data(soup)
            self.stocks[stock_id].extend(revenue_data)

        except requests.RequestException as e:
            print(f"Error fetching revenue data for {stock_id}: {e}")

    def extract_revenue_data(self, soup):
        """Extract revenue data from the soup object."""
        revenue_data = []
        section = soup.find("section", id="qsp-revenue-table")
        if section:
            try: 
                for itm in section.find_all("span", class_="")[0:5:4]:
                    revenue_str = itm.getText().replace(",", "")
                    revenue_data.insert(0, int(revenue_str))
            except requests.RequestException as e:
                print(f"Error fetching revenue data: {e}")
            except ValueError as e:
                print(f"ValueError encountered: {e}")
        else:
            print(f"No revenue data found.")

        return revenue_data

    def save_to_csv(self, filename):
        """
        Save the collected stock data to a CSV file.
        
        :param filename: The name of the file to save the data.
        """
        df = pd.DataFrame(self.stocks.values(), columns=self.target_column_names)
        df['name'] = pd.Series(self.stock_names_to_baught)
        df = df.iloc[:,[0,7,1,2,3,4,5,6]]
        # df.to_csv(filename, mode='a', header=not pd.io.common.file_exists(filename), index=False)
        df.to_csv(filename, index=False)
        print(f"Data has been saved to {filename}")
