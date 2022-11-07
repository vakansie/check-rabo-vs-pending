import tkinter as tk
from dataclasses import dataclass
from collections import Counter
import csv
import os
import glob

SQL_file_path = ''


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
        return {product: qty for product, qty in self.__dict__.items() if qty != 0}

    def sanitize(self):
        return get_quantities(self).to_order_dict()

class UI:
    def __init__(self, order):
        self.window = tk.Tk()
        self.window.title('Sirius Email Generator')
        self.order = order
        self.shuttles_to_order = tk.IntVar(self.window, value=0)
        self.shuttles_entry = tk.Entry(self.window,name='shuttles', textvariable=self.shuttles_to_order)
        self.shuttles_label = tk.Label(self.window, text = 'Space Shuttles', font=('calibre',10, 'bold'))
        self.shuttles_label.grid(row=0,column=0)
        self.shuttles_entry.grid(row=0,column=1)
        self.dolphins_to_order = tk.IntVar(self.window, value=0)
        self.dolphins_entry = tk.Entry(self.window,name='dolphins', textvariable=self.dolphins_to_order)
        self.dolphins_label = tk.Label(self.window, text = 'Dolphins', font=('calibre',10, 'bold'))
        self.dolphins_label.grid(row=1,column=0)
        self.dolphins_entry.grid(row=1,column=1)
        self.teachers_to_order = tk.IntVar(self.window, value=0)
        self.teachers_entry = tk.Entry(self.window,name='teachers', textvariable=self.teachers_to_order)
        self.teachers_label = tk.Label(self.window, text = 'Golden Teachers', font=('calibre',10, 'bold'))
        self.teachers_label.grid(row=2,column=0)
        self.teachers_entry.grid(row=2,column=1)
        self.connectors_to_order = tk.IntVar(self.window, value=0)
        self.connectors_entry = tk.Entry(self.window,name='connectors', textvariable=self.connectors_to_order)
        self.connectors_label = tk.Label(self.window, text = 'Cosmic Connectors', font=('calibre',10, 'bold'))
        self.connectors_label.grid(row=3,column=0)
        self.connectors_entry.grid(row=3,column=1)
        self.rain_to_order = tk.IntVar(self.window, value=0)
        self.rain_entry = tk.Entry(self.window,name='rain', textvariable=self.rain_to_order)
        self.rain_label = tk.Label(self.window, text = 'Purple Rain', font=('calibre',10, 'bold'))
        self.rain_label.grid(row=4,column=0)
        self.rain_entry.grid(row=4,column=1)
        self.diamonds_to_order = tk.IntVar(self.window, value=0)
        self.diamonds_entry = tk.Entry(self.window,name='diamonds', textvariable=self.diamonds_to_order)
        self.diamonds_label = tk.Label(self.window, text = 'White Diamonds', font=('calibre',10, 'bold'))
        self.diamonds_label.grid(row=5,column=0)
        self.diamonds_entry.grid(row=5,column=1)
        self.beluga_to_order = tk.IntVar(self.window, value=0)
        self.beluga_entry = tk.Entry(self.window,name='beluga', textvariable=self.beluga_to_order)
        self.beluga_label = tk.Label(self.window, text = 'Royal Beluga', font=('calibre',10, 'bold'))
        self.beluga_label.grid(row=6,column=0)
        self.beluga_entry.grid(row=6,column=1)
        self.mothers_10g_to_order = tk.IntVar(self.window, value=0)
        self.mothers_10g_entry = tk.Entry(self.window,name='mothers_10g', textvariable=self.mothers_10g_to_order)
        self.mothers_10g_label = tk.Label(self.window, text = 'Mothers Finest 10g', font=('calibre',10, 'bold'))
        self.mothers_10g_label.grid(row=7,column=0)
        self.mothers_10g_entry.grid(row=7,column=1)
        self.mothers_15g_to_order = tk.IntVar(self.window, value=0)
        self.mothers_15g_entry = tk.Entry(self.window,name='mothers 15g', textvariable=self.mothers_15g_to_order)
        self.mothers_15g_label = tk.Label(self.window, text = 'Mothers Finest 15g', font=('calibre',10, 'bold'))
        self.mothers_15g_label.grid(row=8,column=0)
        self.mothers_15g_entry.grid(row=8,column=1)
        self.mix_green_to_order = tk.IntVar(self.window, value=0)
        self.mix_green_entry = tk.Entry(self.window,name='mix green', textvariable=self.mix_green_to_order)
        self.mix_green_label = tk.Label(self.window, text = 'Mystery Mix Green', font=('calibre',10, 'bold'))
        self.mix_green_label.grid(row=9,column=0)
        self.mix_green_entry.grid(row=9,column=1)
        self.mix_orange_to_order = tk.IntVar(self.window, value=0)
        self.mix_orange_entry = tk.Entry(self.window,name='mix_orange', textvariable=self.mix_orange_to_order)
        self.mix_orange_label = tk.Label(self.window, text = 'Mystery Mix Orange', font=('calibre',10, 'bold'))
        self.mix_orange_label.grid(row=10,column=0)
        self.mix_orange_entry.grid(row=10,column=1)
        self.mix_purple_10g_to_order = tk.IntVar(self.window, value=0)
        self.mix_purple_10g_entry = tk.Entry(self.window,name='mix purple 10g', textvariable=self.mix_purple_10g_to_order)
        self.mix_purple_10g_label = tk.Label(self.window, text = 'Mystery Mix Purple 10g', font=('calibre',10, 'bold'))
        self.mix_purple_10g_label.grid(row=11,column=0)
        self.mix_purple_10g_entry.grid(row=11,column=1)
        self.mix_purple_15g_to_order = tk.IntVar(self.window, value=0)
        self.mix_purple_15g_entry = tk.Entry(self.window,name='mix purple 15g', textvariable=self.mix_purple_15g_to_order)
        self.mix_purple_15g_label = tk.Label(self.window, text = 'Mystery Mix Purple 15g', font=('calibre',10, 'bold'))
        self.mix_purple_15g_label.grid(row=12,column=0)
        self.mix_purple_15g_entry.grid(row=12,column=1)
        self.bronze_to_order = tk.IntVar(self.window, value=0)
        self.bronze_entry = tk.Entry(self.window,name='bronze', textvariable=self.bronze_to_order)
        self.bronze_label = tk.Label(self.window, text = 'Bronze', font=('calibre',10, 'bold'))
        self.bronze_label.grid(row=13,column=0)
        self.bronze_entry.grid(row=13,column=1)
        self.silver_to_order = tk.IntVar(self.window, value=0)
        self.silver_entry = tk.Entry(self.window,name='silver', textvariable=self.silver_to_order)
        self.silver_label = tk.Label(self.window, text = 'Silver', font=('calibre',10, 'bold'))
        self.silver_label.grid(row=14,column=0)
        self.silver_entry.grid(row=14,column=1)
        self.gold_to_order = tk.IntVar(self.window, value=0)
        self.gold_entry = tk.Entry(self.window,name='gold', textvariable=self.gold_to_order)
        self.gold_label = tk.Label(self.window, text = 'Gold', font=('calibre',10, 'bold'))
        self.gold_label.grid(row=15,column=0)
        self.gold_entry.grid(row=15,column=1)
        self.palladium_to_order = tk.IntVar(self.window, value=0)
        self.palladium_entry = tk.Entry(self.window,name='palladium', textvariable=self.palladium_to_order)
        self.palladium_label = tk.Label(self.window, text='Palladium', font=('calibre',10, 'bold'))
        self.palladium_label.grid(row=16,column=0)
        self.palladium_entry.grid(row=16,column=1)
        self.freshup_to_order = tk.IntVar(self.window, value=0)
        self.freshup_entry = tk.Entry(self.window,name='freshup', textvariable=self.freshup_to_order)
        self.freshup_label = tk.Label(self.window, text='FreshUp Microdosing', font=('calibre',10, 'bold'))
        self.freshup_label.grid(row=17,column=0)
        self.freshup_entry.grid(row=17,column=1)
        self.bind_keys()
        self.generate_button = tk.Button(self.window, text='Generate Email', command=lambda: write_email(order.sanitize())).grid(row=19,column=0)
        self.reset_button = tk.Button(self.window, text='Reset', command=lambda: reset_quantities()).grid(row=19,column=1)
        self.import_button = tk.Button(self.window, text='Add Products From Processing Orders', command=lambda: import_from_file()).grid(row=19,column=2)
        self.email_field = tk.Text(self.window, height = 25, width = 60, font=('calibre',10))
        self.email_field.grid(row=0, rowspan=17,column=2)
        self.file_field = tk.Text(self.window, height = 1, width = 60, font=('calibre',8))
        self.file_field.grid(row=18, column=2)
        self.product_vars_dict = {
        'Space Shuttles Truffles': self.shuttles_to_order,
        'Dolphins Delight Truffles': self.dolphins_to_order,
        'Golden Teacher Truffles': self.teachers_to_order,
        'Cosmic Connectors Truffles': self.connectors_to_order,
        'Purple Rain Truffles-15 grams': self.rain_to_order,
        'White Diamonds Truffles-15 grams': self.diamonds_to_order,
        'Royal Beluga Truffles-15 grams': self.beluga_to_order,
        'Mothers Finest Truffles -10 grams': self.mothers_10g_to_order,
        'Mothers Finest Truffles 15 grams': self.mothers_15g_to_order,
        'Mystery Mix Green Truffles': self.mix_green_to_order,
        'Mystery Mix Orange Truffles': self.mix_orange_to_order,
        'Mystery Mix Purple Truffles-10 grams': self.mix_purple_10g_to_order,
        'Mystery Mix Purple Truffles-15 grams': self.mix_purple_15g_to_order,
        'Bronze Truffles': self.bronze_to_order,
        'Silver Truffles': self.silver_to_order,
        'Gold Truffles': self.gold_to_order,
        'Palladium Truffles': self.palladium_to_order,
        'FreshUp Microdosing': self.freshup_to_order}
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

    def bind_keys(self):
        self.window.bind("R", lambda x: reset_quantities())
        self.window.bind("F", lambda x: import_from_file())
        self.window.bind("<Return>", lambda x: write_email(self.order.sanitize()))

def get_quantities(order):
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
        except ValueError: 
            ui.file_field.insert(tk.END,'ERROR: no SQL file found. Run: Generate Databse Query.bat')
            SQL_file = get_SQL_file(SQL_file_path)
        return SQL_file

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

def set_fields(product_tally):
    for product, qty in product_tally.items():
        if isinstance(ui.product_vars_dict[product].get(), int):
            ui.product_vars_dict[product].set((ui.product_vars_dict[product].get() + qty))

def import_from_file():
    SQL_file = get_SQL_file(SQL_file_path)
    product_tally = tally_products(SQL_file)
    set_fields(product_tally)

def write_email(ordered_products):
    ui.email_field.delete(1.0,tk.END)
    ui.email_field.insert(tk.END, '''
Hoi Paulette,

Ik zou graag bestellen:
''')
    for product, quantity in ordered_products.items():
            ui.email_field.insert(tk.END, f'\n{quantity:>5} {ui.product_dict[product]:^5}')
    ui.email_field.insert(tk.END, '''

Groeten,
Frans
''')

def main():
    global ui
    order = Sirius_Order()
    ui = UI(order)
    ui.window.mainloop()

if __name__ == '__main__':
    main()