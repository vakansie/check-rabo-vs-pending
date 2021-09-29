from collections import defaultdict
from operator import itemgetter
import csv
import os
import time
import glob

SQL_file_path = 'Z://downloads'

def get_SQL_file(SQL_file_path):
        possible_files = glob.glob(SQL_file_path+'\\sales_order*.csv')
        try:
            SQL_file = max(possible_files, key=os.path.getctime)
        except ValueError: 
            print('\nrun check_rabo_vs_pending.py, paste sql.txt text in phpMyAdmin, export as csv')
            input("\nFile not found. Download file and press enter.\n")
            SQL_file = get_SQL_file(SQL_file_path)
        print(f'\nSQL file used: {SQL_file}  {time.ctime(os.path.getmtime(SQL_file))}\n')
        return SQL_file

def tally_products(SQL_file):
    product_tally = defaultdict(int) # dictionary where a product's tally starts at 0
    with open (SQL_file, 'rt', encoding = "utf-8") as file:
        reader = csv.reader(file)
        for row in reader:
            order_as_list = list(row)
            try:
                product = order_as_list[8]
                product_type = order_as_list[14]
                qty = int(float(order_as_list[10]))
                if product_type == 'simple':
                    product_tally[product] += qty
            except ValueError: pass
        sorted_tally = dict(sorted(product_tally.items(), key=itemgetter(1), reverse=True))
        return sorted_tally

if __name__=='__main__':
    SQL_file = get_SQL_file(SQL_file_path)
    product_tally = tally_products(SQL_file)
    for product, qty in product_tally.items():
        print(f'{qty : ^5}{product}')
    print()
    input('press enter to exit')