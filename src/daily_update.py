# -*- coding: utf-8 -*-

# Import Python module
import time

# Import packages
from fetch import __update_codes
# from compute_eps_csv import main as compute_eps_and_output_csv

from export_financial_status import export_finantial_today_info
from evaluate_interesting_stocks import evaluate_potential_stocks

if __name__ == "__main__":
    print("Start to update the database")
    __update_codes()
    time.sleep(5)
    print("Done!")

    # compute_eps_and_output_csv()

    export_finantial_today_info()
    evaluate_potential_stocks()
