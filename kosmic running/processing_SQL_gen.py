import csv
import re
import os
import time
import glob

magento_processing_file_path = 'Z://downloads' 

SQL_template = """
SELECT 
`sales_order`.status, `sales_order`.`base_grand_total`, `sales_order`.`shipping_amount`, `sales_order`.`shipping_tax_amount`, `sales_order`.`increment_id`, sales_order.`discount_amount`,`sales_order`.`grand_total`, sales_order_payment.method, `sales_order_item`.`name`, `sales_order_item`.`tax_percent`, `sales_order_item`.`qty_ordered`, `sales_order_item`.`original_price`, `sales_order_item`.`base_price`, `sales_order_item`.`base_tax_amount`,  `sales_order_item`.`product_type`

FROM sales_order

LEFT JOIN `sales_order_payment`
ON `sales_order`.entity_id = `sales_order_payment`.entity_id

LEFT JOIN `sales_order_item`
ON `sales_order`.entity_id = `sales_order_item`.`order_id`

WHERE    
`sales_order`.`increment_id` in {}

ORDER BY `sales_order`.`increment_id` DESC
    
"""

def get_magento_processing_file(magento_processing_file_path):
        possible_files = glob.glob(magento_processing_file_path+'\\export*.csv')
        try:
            magento_processing_file = max(possible_files, key=os.path.getctime)
        except ValueError: 
            print('\nPay inloggen, transacties tab, datums invullen, filters: status = succes + status = paid, uitvoeren als csv, save')
            input("\nFile not found. Download file and press enter.\n")
            magento_processing_file = get_magento_processing_file(magento_processing_file_path)
        print(f'\nMagento file used: {magento_processing_file}  {time.ctime(os.path.getmtime(magento_processing_file))}')
        return magento_processing_file

def generate_SQL(magento_processing_file):
    order_number_list = []
    with open (magento_processing_file, 'rt', encoding = "utf-8")as f:
            reader = csv.reader(f)
            for row in reader:
                order_as_list = list(row)
                try: 
                    possible_order_number = order_as_list[0]
                    order_status = order_as_list[7]
                    order_number_match = re.match("1000[0-1][0-9][0-9][0-9][0-9][0-9]-?(?=[0-9])?[0-9]?", possible_order_number)
                    if order_number_match and order_status == 'processing':
                        order_number = order_number_match.group()
                        order_number_list.append(order_number)
                except IndexError: pass
    SQL_content = "('"+"', '".join(order_number_list)+"')"
    SQL_query = SQL_template.format(SQL_content)
    return SQL_query

if __name__=='__main__':
    magento_processing_file = get_magento_processing_file(magento_processing_file_path)
    SQL_query = generate_SQL(magento_processing_file)
    print('Query to paste into phpMyadmin:\n')
    print(SQL_query)
    input('\nPress enter to exit')