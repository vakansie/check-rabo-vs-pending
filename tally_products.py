from collections import Counter, defaultdict
import csv
import os
import glob

SQL_file_path = 'C://Users\win 10\Desktop\mapmap\kosmic_python\kosmic running'# 'Z://downloads'

file_header_dict = {
                'product_name': 'name',
                'product_type': 'product_type',
                'manufacturer': 'manufacturer_value',
                'qty_ordered': 'qty_ordered',
                'customer_comment': "osc_order_comment",
                'order_number': "increment_id",
                'customer_firstname': 'customer_firstname',
                'customer_lastname': 'customer_lastname',
                'customer_email': "customer_email"}

manufacturers_dict = defaultdict(int)
manufacturer_tally = Counter()

def get_SQL_file(SQL_file_path):
        possible_files = glob.glob(SQL_file_path+'\\sales_order*.csv')
        try:
            SQL_file = max(possible_files, key=os.path.getctime)
        except ValueError: 
            print('\nERROR: no SQL file found. Run: Generate Databse Query.bat')
            input("\nFile not found. Download file and press enter.\n")
            SQL_file = get_SQL_file(SQL_file_path)
        return SQL_file

def tally_products(SQL_file):
    product_tally = Counter()
    global manufacturers_dict
    global manufacturer_tally
    with open (SQL_file, 'rt', encoding = "utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                product_name = row[file_header_dict['product_name']]
                product_type = row["product_type"]
                manufacturer = row["manufacturer_value"]
                qty_ordered = int(float(row['qty_ordered']))
                if product_type.lower() == 'simple':
                    product_tally.update({product_name: qty_ordered})
                    manufacturer_tally.update({manufacturer: qty_ordered})
                    manufacturers_dict[product_name] = manufacturer
            except KeyError as key: print(f'KeyError: something changed in the csv file headers. missing header: {key}')
        sorted_product_tally = dict(product_tally.most_common())
        manufacturer_tally = dict(manufacturer_tally.most_common())
        return sorted_product_tally

def sort_by_seller(product_tally):
    for manufacturer in manufacturer_tally:
        if manufacturer == 'NULL': continue
        print(f' {manufacturer}: {manufacturer_tally[manufacturer]}')
        for product, qty in product_tally.items():
            if manufacturers_dict[product] == manufacturer:
                print(f' {qty : ^5}{product}')
    print(f' Other: {manufacturer_tally.get("NULL")}')
    for product, qty in product_tally.items():
        if manufacturers_dict[product] == 'NULL':
            print(f' {qty : ^5}{product}')

def fetch_order_comments(SQL_file):
    comment_dict = {}
    with open (SQL_file, 'rt', encoding = "utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                customer_comment = row["osc_order_comment"]
                if customer_comment == 'NULL': continue
                order_number = row["increment_id"]
                customer_name = f'{row["customer_firstname"]} {row["customer_lastname"]}'
                customer_email = row["customer_email"]
                comment_dict[f'{order_number} - {customer_name} - {customer_email}'] = customer_comment
            except KeyError as key: 
                print(f'KeyError: something changed in the csv file headers. missing header: {key}')
                exit()
        return comment_dict

def main():
    SQL_file = get_SQL_file(SQL_file_path)
    print(f'\nSQL file used: {SQL_file}\n')

    product_tally = tally_products(SQL_file)
    print(f' Number of products to be shipped: {sum(product_tally.values())}\n')
    sort_by_seller(product_tally)

    print('\n ORDER COMMENTS:\n')
    customer_comment_dict = fetch_order_comments(SQL_file)
    if not customer_comment_dict: print(' 0 of those orders have customer comments.')
    for order in customer_comment_dict:
        print(f' {order} -  \n"{customer_comment_dict[order]}"')

    print()
    input('press enter to exit')
    
if __name__=='__main__':
    main()