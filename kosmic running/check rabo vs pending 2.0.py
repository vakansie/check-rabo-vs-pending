            ### vakansie payment order match machine ###

###  matches rabo payments to magento orders by comparing downloaded csv files ###

import re
import os
import csv
import glob
import datetime
import time
from operator import attrgetter
from fuzzywuzzy import fuzz

download_path = 'Z://downloads' 

generated_email_file = "Generated_emails.txt"

# These payment providers put the customer name 1 cell further to the right:
payment_description_exceptions = ()
# Transfers from these accounts are never payments for orders:
ignore_transfers_from = ()


class Payment:
    def __init__(self, order_number, name, amount_paid, date, description, weight_matched_order_list, match_type):
        self.name                      = name
        self.amount_paid               = amount_paid
        self.date                      = date
        self.order_number              = order_number
        self.description               = description
        self.weight_matched_order_list = []
        self.match_type                = match_type

    def merge_payments_for_same_order(rabo_payment_list):
        for payment_1 in rabo_payment_list:
            for payment_2 in rabo_payment_list:
                if rabo_payment_list.index(payment_1) != rabo_payment_list.index(payment_2):
                    if payment_1.order_number == payment_2.order_number and payment_1.name == payment_2.name:                        
                        payment_1.amount_paid += payment_2.amount_paid
                        rabo_payment_list.pop(rabo_payment_list.index(payment_2))
        return rabo_payment_list

    def __repr__(self):
        formatted_amount = Weight_Matched_Order.convert_float_to_printing_format(self.amount_paid)
        date = self.date.strftime('%d %b %Y')
        return f'{self.order_number:<13}-{formatted_amount:>9}   -  {self.name:<28} -  {self.description:<29} - {self.match_type:<23}- {date}'

    def sort(self):
        return self.order_number

class Order:
    def __init__(self, order_number, name, amount_owed, date, order_status, email, payment_method):
        self.order_number     = order_number
        self.name             = name
        self.amount_owed      = amount_owed
        self.date             = date 
        self.order_status     = order_status
        self.email            = email
        self.payment_method   = payment_method

    def __repr__(self):
        formatted_amount = Weight_Matched_Order.convert_float_to_printing_format(self.amount_owed)
        date = self.date.strftime('%d %b %Y %H:%M:%S')
        return f'{self.order_number:<13}-{formatted_amount:>9}   -  {self.name:<28} -   {self.email:<34} - {self.order_status:<10} - {date}'

class Weight_Matched_Order:
    def __init__(self, order_number, amount_owed, name, email, match_weight, order_status, date):
        self.order_number = order_number
        self.amount_owed  = amount_owed
        self.name         = name
        self.order_email  = email
        self.match_weight = match_weight
        self.order_status = order_status
        self.date         = date

    def __repr__(self):
        formatted_amount = Weight_Matched_Order.convert_float_to_printing_format(self.amount_owed)
        date = self.date.strftime('%d %b %Y %H:%M:%S')
        return f'{self.order_number:<13}-{formatted_amount:>9}   -  {self.name:<28} -  {self.order_email:<34} - {self.order_status:<18}- {date}'

    def convert_float_to_printing_format(amount):
        return str(f'{round(float(amount), 2):.2f}').replace('.', ',')

    def last_x_characters_of(number, x):
        return number[(len(number)-x):]        

class Payment_Order_Match:
    def __init__(self, order_number, amount_owed, amount_paid, name, amount_check_result, email):
        self.order_number           = order_number
        self.amount_owed            = amount_owed
        self.amount_paid            = amount_paid
        self.name                   = name
        self.amount_check_result    = amount_check_result
        self.email                  = email

    def __repr__(self):
        formatted_amount_owed = Weight_Matched_Order.convert_float_to_printing_format(self.amount_owed)
        formatted_amount_paid = Weight_Matched_Order.convert_float_to_printing_format(self.amount_paid)
        return f'{self.order_number:<13}-{formatted_amount_owed:>9}  -{formatted_amount_paid:>9}  -  {self.name:<28} - {self.amount_check_result}'

def get_rabo_and_magento_file(download_path):
    def get_download_path_from_user():
        given_path = input('copy-paste the path to your download folder here: \n')
        if len(given_path) > 2:
            temp_download_path = given_path.replace("\\",'/')
            check_rabo_file_vs_magento_file(temp_download_path)
    files_found = False
    while files_found == False: 
        list_of_rabo_files = glob.glob(download_path+'\\TRANSACTION_SEARCH_*.csv')
        for file in glob.glob(download_path+'\\CSV_T_*.csv'): list_of_rabo_files.append(file)
        for file in glob.glob(download_path+'\\ZOEK_RESULTAAT_*.csv'): list_of_rabo_files.append(file)

        list_of_magento_files = glob.glob(download_path+'\\export*.csv')
        try:
            rabo_file = max(list_of_rabo_files, key=os.path.getctime)
            magento_file = max(list_of_magento_files, key=os.path.getctime)
            files_found = True
        except ValueError: 
            user_input = input(f"Files not found in {download_path}. Download the files and press enter. To change the folder to look for files enter: 'change': \n")
            if user_input.upper() == 'CHANGE':
                get_download_path_from_user()
    print(f'magento file:  {time.ctime(os.path.getmtime(magento_file))}  {magento_file}')
    print(f'rabo file:     {time.ctime(os.path.getmtime(rabo_file))}  {rabo_file}')
    print('-'*10)
    return (magento_file, rabo_file)

def process_the_magento_file(magento_file):
    magento_order_list = []
    with open(magento_file, 'rt', encoding = "utf-8", errors='ignore' ) as p:
        reader2 = csv.reader(p)
        for row in reader2:
            order_as_list = tuple(row)
            try:
                amount_owed = round(float(order_as_list[5]), 2)
                try:
                    order_number       = order_as_list[0]
                    name               = str(order_as_list[3]).upper()
                    order_status       = order_as_list[7]
                    date               = datetime.datetime.strptime(order_as_list[2], '%b %d, %Y %H:%M:%S %p')
                    email              = order_as_list[11]
                    payment_method     = order_as_list[16]
                    row_contains_order = True
                except IndexError: raise ValueError
            except ValueError: row_contains_order = False
            except IndexError: row_contains_order = False
            if row_contains_order == True:
                order = Order(order_number, name, amount_owed, date, order_status, email, payment_method)
                magento_order_list.append(order)
        print(len(magento_order_list), ' orders in magento file:')
        print('-'*10)
        return magento_order_list

def get_rabo_date_format(rabo_file):
    file_name = str(rabo_file)
    if file_name[14:20] == 'CSV_T_': rabo_date_format = '%Y-%m-%d'
    if file_name[14:29] == 'ZOEK_RESULTAAT_': rabo_date_format = '%d/%m/%Y'
    if file_name[14:33] == 'TRANSACTION_SEARCH_': rabo_date_format = '%d-%m-%Y'
    return rabo_date_format

def process_the_rabo_file(rabo_file, date_format):
    rabo_payment_list = []
    with open(rabo_file, 'rt', encoding = "ISO-8859-1") as f:
        reader = csv.reader(f)
        for row in reader:
            transaction = tuple(row)
            try:
                name                = str(transaction[9]).upper()
                description         = transaction[19]
                order_number_fields = transaction[9:28]
                for exception in payment_description_exceptions:
                    if name == exception.upper():
                        name = str(transaction[10]).upper()
                transaction_code = transaction[13]
                #print(transaction[4]) 
                try:
                    amount_paid = round(float(str(transaction[6]).replace(',', '.')), 2)
                    date = datetime.datetime.strptime(transaction[4], date_format)
                except ValueError: raise IndexError
            except IndexError: pass
            transaction_codes = ('cb', 'wb')
            if transaction_code in transaction_codes and name not in ignore_transfers_from: 
                order_number = 'none found'
                for field in order_number_fields:
                    extracted_numbers = set(re.findall('1000[0-9][0-9][0-9][0-9][0-9][0-9]-?(?=[0-9])?[0-9]?', field))
                    for order_number_found in set(extracted_numbers): 
                        order_number = order_number_found

                payment = Payment(order_number, name, amount_paid, date, description, weight_matched_order_list = [], match_type = None)
                rabo_payment_list.append(payment)
    rabo_payment_list.sort(key=Payment.sort)
    return rabo_payment_list

def weigh(rabo_payment_list, magento_order_list):
    for payment in rabo_payment_list:
        weight_matched_order_list = []
        payment.weight_matched_order_list = []
        for order in magento_order_list:
            possible_match = Weight_Matched_Order(order.order_number, order.amount_owed, order.name, order.email, 0, order.order_status, order.date)
            weight_matched_order_list.append(possible_match)
            ### exact string matching
            possible_match.match_weight += 10 * (payment.name.upper()        == possible_match.name.upper()) # will also get 10 from fuzzy match
            possible_match.match_weight += 15 * (payment.description.upper() == possible_match.name.upper() or payment.description == possible_match.order_email)
            possible_match.match_weight +=  3 * (possible_match.amount_owed  == payment.amount_paid)
            possible_match.match_weight -=  3 * (order.order_status          == 'canceled')
            ###lower weight if the payment is more than the amount owed
            paid = float(str(payment.amount_paid).replace(',', '.'))
            owed = float(str(possible_match.amount_owed).replace(',', '.'))
            percentage_of_amount_owed = (paid - owed) / owed
            possible_match.match_weight -= min(5, (10 * percentage_of_amount_owed)) * (percentage_of_amount_owed > 0.1)
            ### fuzzy string matching
            fuzzy_name_weight = round((fuzz.token_sort_ratio(possible_match.name, payment.name) // 10))
            if 7 < fuzzy_name_weight <= 10: fuzzy_name_weight_scaled = fuzzy_name_weight *2
            elif fuzzy_name_weight > 5:     fuzzy_name_weight_scaled = fuzzy_name_weight/2
            elif fuzzy_name_weight < 5:     fuzzy_name_weight_scaled = fuzzy_name_weight/4
            else:                           fuzzy_name_weight_scaled = 0
            possible_match.match_weight +=  fuzzy_name_weight_scaled
            ### partial name matching
            partial_name_count = 0
            for partial_payment_name in payment.name.split():
                possible_match.match_weight += 2 * (partial_payment_name.upper() in order.email.upper() and len(partial_payment_name) > 2)
                for partial_order_name in possible_match.name.split():
                    partial_name_count += 1 * (len(partial_payment_name) > 2 and partial_payment_name.upper() == partial_order_name.upper())
                    possible_match.match_weight += partial_name_count**2
            partial_name_count = 0
            for partial_description in re.sub('\W', ' ' , payment.description).split():
                for partial_order_name in possible_match.name.split():
                    partial_name_count += 1 * (partial_description.upper() == partial_order_name.upper() and len(partial_description) >2)
                    possible_match.match_weight += (partial_name_count**2)%10 
            ### exact order number matching
            possible_match.match_weight += 10 * (possible_match.order_number == payment.order_number)
            ### partial order number matching
            for number in payment.description.split():
                if len(number) >= 5:
                    if Weight_Matched_Order.last_x_characters_of(number,5) == Weight_Matched_Order.last_x_characters_of(possible_match.order_number,5): 
                        possible_match.match_weight += 10
                    else:
                        for undashed_number in number.split('-'):
                            if Weight_Matched_Order.last_x_characters_of(undashed_number,5) == Weight_Matched_Order.last_x_characters_of(possible_match.order_number,5):
                                possible_match.match_weight += 8
            ### matching by ignoring the '-[0-9]'
            for i in payment.description.split('-'):
                if '-' in  possible_match.order_number and order.order_status == 'pending':
                    for j in possible_match.order_number.split('-'):
                        if len(i) >= 9 and len(j) >= 9:
                            try: possible_match.match_weight += 20 * (int(i) == int(j))
                            except ValueError: pass
            ### date penalty for each week late
            possible_match.match_weight -= 1 * round((payment.date-possible_match.date).total_seconds()/604800)
        ### clean up
            possible_match.match_weight = round(possible_match.match_weight)
            if possible_match.match_weight <= 0: weight_matched_order_list.pop()
        weight_matched_order_list.sort(reverse=True, key=attrgetter('match_weight'))
        payment.weight_matched_order_list = weight_matched_order_list[:3]
        if payment.weight_matched_order_list: payment.match_type = '... weighing'
        else: payment.match_type = 'X  no match found'
    return rabo_payment_list

def match_by_order_number(rabo_payment_list, magento_order_list):

    def payment_matched_to_order(payment, order):
        if (payment.order_number == order.order_number\
        and ((fuzz.token_sort_ratio(payment.name, order.name) > 50 or (abs(order.amount_owed - payment.amount_paid) < 1) and abs(order.amount_owed - payment.amount_paid) < 25)))\
        and payment.weight_matched_order_list[0].order_number == payment.order_number:
            return True
        elif  Weight_Matched_Order.last_x_characters_of(payment.description,5) == Weight_Matched_Order.last_x_characters_of(order.order_number,5)\
        and fuzz.token_sort_ratio(payment.name, order.name) > 80:
            return True
        else:
            return False

    def amount_check(payment_order_match):
        paid = float(str(payment_order_match.amount_paid).replace(',', '.'))
        owed = float(str(payment_order_match.amount_owed).replace(',', '.'))
        difference = str(format((abs(paid - owed)), '.2f'))
        if owed == paid:
            amount_check_result = "exact"
        elif owed < paid:
            amount_check_result = f'overpaid:  {difference:>5}- {payment_order_match.email}'
        elif owed > paid:
            amount_check_result = f'underpaid: {difference:>5}- SEE: Generated_emails.txt :  {payment_order_match.email}'
            generate_under_paid_emails(payment_order_match)
        return amount_check_result

    unmatched_payment_list = []
    matched_payments_list = []
    for payment in rabo_payment_list:
        match = False
        for order in magento_order_list:
            ### create a match object for good matches between payments and pending orders
            if payment_matched_to_order(payment, order):
                if (order.order_status == 'pending' or order.order_status == 'holded')\
                and all(order.order_number != already_matched.order_number for already_matched in matched_payments_list):
                        matched_payment = Payment_Order_Match(order.order_number, order.amount_owed, payment.amount_paid, order.name, 'not checked', order.email) 
                        matched_payments_list.append(matched_payment)
                        match = True
                elif (order.order_status == 'complete' or order.order_status == 'processing'): match = True
                payment.match_type = f'V  matched: {order.order_status}'
                if order.order_status == 'canceled': payment.match_type = '... canceled'
        if not match: unmatched_payment_list.append(payment)
    for payment_order_match in matched_payments_list:
        payment_order_match.amount_check_result = amount_check(payment_order_match)
    return (unmatched_payment_list, matched_payments_list)

def match_by_weight(unmatched_payment_list, matched_payments_list):
    print('-'*10)
    print(f'{len(unmatched_payment_list)} not matched by order number: \n')
    if len(unmatched_payment_list) == 0: print('all payments matched by order number.')
    for payment in unmatched_payment_list:
        print(f'Payment to match:               ?? {payment}')
        for count, order in enumerate(payment.weight_matched_order_list, start=1):
            print(f'best match {count}: match weight ={order.match_weight:>3} || {order}')
            for match in matched_payments_list:
                if order.order_number == match.order_number: print (f'!!! already matched to payment: ?! {match}')
        if not payment.weight_matched_order_list: print('no matches found')
        print('-'*10)

def generate_under_paid_emails(payment_order_match):
    f = open(generated_email_file, "at", encoding="utf-8")
    underpaid_by = Weight_Matched_Order.convert_float_to_printing_format(payment_order_match.amount_owed - payment_order_match.amount_paid).replace(',00', ',-')
    paid         = Weight_Matched_Order.convert_float_to_printing_format(payment_order_match.amount_paid).replace(',00', ',-')
    owed         = Weight_Matched_Order.convert_float_to_printing_format(payment_order_match.amount_owed).replace(',00', ',-')
    name_list    = payment_order_match.name.lower().capitalize().split()
    name         = name_list[0]
    f.write(payment_order_match.email)
    f.write('\n')
    f.write('\n')
    f.write(f'Insufficient payment for order {payment_order_match.order_number}\n')
    f.write('\n')  
    f.write('\n')     
    f.write(f'Hey {name},\n')
    f.write('\n')
    f.write(F'We received your payment of €{paid} for order {payment_order_match.order_number} but the order was for €{owed}.\n')
    f.write(f'Please transfer the remaining €{underpaid_by} so we can ship your order.\n')
    f.write('\n')
    f.write('Kind regards,\nBernard\n')
    f.write('\n')
    f.write('-----\n')
    f.close()

def clear_old_generated_emails_file(generated_email_file):
    f = open(generated_email_file, "wt", encoding="utf-8")
    f.write('')
    f.close()

def get_pay_at_the_store_orders(magento_order_list):
    print('Pay at the store orders:\n') 
    magento_order_list.sort(reverse=True, key=attrgetter('date'))
    for order in magento_order_list:
        if order.payment_method == 'checkmo' and order.order_status in ['pending', 'processing', 'holded']:
            print(order)

def print_payments(rabo_payment_list):
    print(f'{len(rabo_payment_list)} Rabobank payments for orders:\n')
    print('Order Number - € Amount   -  Name                         -  Description                   - Match')
    for payment in rabo_payment_list:
        print(payment)
    print('-'*10)

def print_matches(matched_payments_list):
    print(len(matched_payments_list), 'paid but pending:\n')
    if matched_payments_list:
        print('Order Number -     Owed  -     Paid  -  Name on order                - Check')
        for payment_order_match in matched_payments_list:
            print(payment_order_match)

def check_rabo_file_vs_magento_file(download_path):
    print('\n','-'*10, "vakansie payment order match machine", ('-'*10), '\n')
    clear_old_generated_emails_file(generated_email_file)
    magento_file, rabo_file = get_rabo_and_magento_file(download_path)
    rabo_date_format = get_rabo_date_format(rabo_file)
    magento_order_list = process_the_magento_file(magento_file)
    rabo_payment_list = process_the_rabo_file(rabo_file, rabo_date_format)
    Payment.merge_payments_for_same_order(rabo_payment_list)
    weigh(rabo_payment_list, magento_order_list)
    unmatched_payment_list, matched_payments_list = match_by_order_number(rabo_payment_list, magento_order_list)
    print_payments(rabo_payment_list)
    print_matches(matched_payments_list)
    match_by_weight(unmatched_payment_list, matched_payments_list)
    get_pay_at_the_store_orders(magento_order_list)
    input('\npress enter to exit')

if __name__ == "__main__":
    check_rabo_file_vs_magento_file(download_path)