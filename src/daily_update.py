# -*- coding: utf-8 -*-

# Import Python module
import time

# Import packages
from fetch import __update_codes
from compute_eps_csv import main as compute_eps_and_output_csv

if __name__ == "__main__":
    print("Start to update the database")
    __update_codes()
    time.sleep(5)
    print("Done!")

    compute_eps_and_output_csv()