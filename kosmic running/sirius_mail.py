import tkinter as tk
from dataclasses import dataclass
from collections import Counter
import csv
import os
import glob

SQL_file_path = 'C://Users\win 10\Desktop\mapmap\kosmic_python\kosmic running'# 'Z://downloads'


@dataclass
class Sirius_Order:
    shuttles: int = 0
    dolphins: int = 0
    teachers: int = 0
    connectors: int = 0
    rain: int = 0
    diamonds: int = 0
    beluga: int = 0
    mothers_10g: int = 0
    mothers_15g: int = 0
    mix_green: int = 0
    mix_orange: int = 0
    mix_purple_10g: int = 0
    mix_purple_15g: int = 0
    bronze: int = 0
    silver: int = 0
    gold: int = 0
    palladium: int = 0
    freshup: int = 0

    def to_order_dict(self):
        return {product: qty for product, qty in self.__dict__.items() if qty > 0}

    def prepare_email(self):
        return update_quantities(self).to_order_dict()

class UI:
    def __init__(self, order):
        self.window = tk.Tk()
        self.window.title('Sirius Email Generator')
        self.order = order
        self.product_vars = {}
        self.generate_product_vars()
        self.label_names = ['Space Shuttles',
                            'Dolphins',
                            'Golden Teachers',
                            'Cosmic Connectors',
                            'Purple Rain',
                            'White Diamonds',
                            'Royal Beluga',
                            'Mothers Finest 10g',
                            'Mothers Finest 15g',
                            'Mystery Mix Green',
                            'Mystery Mix Orange',
                            'Mystery Mix Purple 10g',
                            'Mystery Mix Purple 15g',
                            'Bronze',
                            'Silver',
                            'Gold',
                            'Palladium',
                            'FreshUp Microdosing']
        self.product_vars_dict = {
        'Space Shuttles Truffles': self.product_vars['shuttles'],
        'Dolphins Delight Truffles': self.product_vars['dolphins'],
        'Golden Teacher Truffles': self.product_vars['teachers'],
        'Cosmic Connectors Truffles': self.product_vars['connectors'],
        'Purple Rain Truffles-15 grams': self.product_vars['rain'],
        'White Diamonds Truffles-15 grams': self.product_vars['diamonds'],
        'Royal Beluga Truffles-15 grams': self.product_vars['beluga'],
        'Mothers Finest Truffles -10 grams': self.product_vars['mothers_10g'],
        'Mothers Finest Truffles 15 grams': self.product_vars['mothers_15g'],
        'Mystery Mix Green Truffles': self.product_vars['mix_green'],
        'Mystery Mix Orange Truffles': self.product_vars['mix_orange'],
        'Mystery Mix Purple Truffles-10 grams': self.product_vars['mix_purple_10g'],
        'Mystery Mix Purple Truffles-15 grams': self.product_vars['mix_purple_15g'],
        'Bronze Truffles': self.product_vars['bronze'],
        'Silver Truffles': self.product_vars['silver'],
        'Gold Truffles': self.product_vars['gold'],
        'Palladium Truffles': self.product_vars['palladium'],
        'FreshUp Microdosing': self.product_vars['freshup']}
        self.product_dict = {
        'shuttles': 'shuttles',
        'dolphins': 'dolphins',
        'teachers': 'teachers',
        'connectors': 'connectors',
        'rain': 'rain',
        'diamonds': 'diamonds',
        'beluga': 'beluga',
        'mothers_10g': 'mothers 10g',
        'mothers_15g': 'mothers 15g',
        'mix_green': 'mystery mix green',
        'mix_orange': 'mystery mix orange',
        'mix_purple_10g': 'mystery mix purple 10g',
        'mix_purple_15g': 'mystery mix purple 15g',
        'bronze': 'bronze',
        'silver': 'silver',
        'gold': 'gold',
        'palladium': 'palladium',
        'freshup': 'freshup microdose'}
        self.order_var_dict = dict(zip(self.product_dict.keys(), self.product_vars_dict.values()))
        self.product_labels_dict = dict(zip(self.product_dict.keys(), self.label_names))
        self.generate_general_ui_elements()
        self.generate_product_ui_elements()
        self.bind_keys()

    def generate_general_ui_elements(self):
        self.generate_button = tk.Button(self.window, text='Generate Email', command=lambda: write_email(self.order.prepare_email())).grid(row=len(self.product_dict)+2,column=0)
        self.reset_button = tk.Button(self.window, text='Reset', command=lambda: reset_quantities()).grid(row=len(self.product_dict)+2,column=1)
        self.import_button = tk.Button(self.window, text='Add Products From Processing Orders', command=lambda: add_from_file()).grid(row=len(self.product_dict)+2,column=2)
        self.email_field = tk.Text(self.window, height = 25, width = 60, font=('calibre',10))
        self.email_field.grid(row=0, rowspan=len(self.product_dict),column=2)
        self.file_field = tk.Text(self.window, height = 1, width = 60, font=('calibre',8))
        self.file_field.grid(row=len(self.product_dict)+1, column=2)

    def generate_product_vars(self):
        for product in self.order.__dict__.keys():
            self.product_vars[product] = tk.IntVar(self.window, value=0)

    def generate_product_ui_elements(self):
        self.product_entries = {}
        self.product_labels = {}
        for position, product in enumerate(self.order.__dict__.keys()):
            self.product_entries[product] = tk.Entry(self.window,name=self.product_dict[product], textvariable=self.product_vars[product])
            self.product_labels[product] = tk.Label(self.window, text=self.product_labels_dict[product], font=('calibre',10, 'bold'))
            self.product_entries[product].grid(row=position, column=1)
            self.product_labels[product].grid(row=position, column=0)

    def bind_keys(self):
        self.window.bind("R", lambda x: reset_quantities())
        self.window.bind("F", lambda x: add_from_file())
        self.window.bind("<Return>", lambda x: write_email(self.order.prepare_email()))

def update_quantities(order):
    for product in order.__dict__.keys():
        try:
            order.__dict__[product] = int(ui.order_var_dict[product].get())
        except: order.__dict__[product] = 0 
    return order

def reset_quantities():
    for entry_var in ui.product_vars_dict.values():
        entry_var.set(0)

def get_SQL_file(SQL_file_path):
        possible_files = glob.glob(SQL_file_path+'\\sales_order*.csv')
        try:
            SQL_file = max(possible_files, key=os.path.getctime)
            ui.file_field.insert(tk.END, f'file used: {SQL_file}')
            return SQL_file
        except ValueError: 
            ui.file_field.insert(tk.END,'ERROR: no SQL file found. Run: Generate Databse Query.bat')
            return

def tally_products(SQL_file):
    product_tally = Counter()
    with open (SQL_file, 'rt', encoding = "utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                product_type = row["product_type"]
                if product_type.lower() != 'simple': continue
                manufacturer = row["manufacturer_value"]
                if manufacturer != 'Freshbox': continue
                product_name = row['name']
                qty_ordered = int(float(row['qty_ordered']))
                product_tally.update({product_name: qty_ordered})
            except KeyError as key: print(f'KeyError: something changed in the csv file headers. missing header: {key}')
        return product_tally

def add_to_fields(product_tally):
    for product, qty in product_tally.items():
        if isinstance(ui.product_vars_dict[product].get(), int):
            ui.product_vars_dict[product].set((ui.product_vars_dict[product].get() + qty))

def add_from_file():
    SQL_file = get_SQL_file(SQL_file_path)
    if not SQL_file: return
    product_tally = tally_products(SQL_file)
    add_to_fields(product_tally)

def write_email(ordered_products):
    ui.email_field.delete(1.0,tk.END)
    ui.email_field.insert(tk.END, 'Hoi Paulette,\n\nIk zou graag bestellen:\n')
    for product, quantity in ordered_products.items():
            ui.email_field.insert(tk.END, f'\n{quantity:>5} {ui.product_dict[product]:^5}')
    ui.email_field.insert(tk.END, '\n\nGroeten,\nFrans')

def main():
    global ui
    order = Sirius_Order()
    ui = UI(order)
    ui.window.mainloop()

if __name__ == '__main__':
    main()