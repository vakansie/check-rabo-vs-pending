import requests
from collections import Counter
import tkinter as tk
from manufacturer_dict import manufacturer_dict

manufacturers_dict = {}
manufacturer_tally = Counter()

base_url = 'https://my_magento_website.com'
# Get token by creating an integration in magento. On the Admin panel, click System. In the Extensions section, select Integrations.
access_token = 'asdasdf' 
headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

class UI:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title('Processing orders: Product and Comment Info')
        self.focus = 1
        self.generate_main_ui_elements()
        self.window.lift()
        self.window.attributes('-topmost',True)
        self.window.after_idle(self.window.attributes,'-topmost',False)

    def generate_main_ui_elements(self):
        self.tally_field: tk.Text = tk.Text(self.window, height = 32, width = 120, font=('calibre',12))
        self.tally_field.grid(row=0, rowspan=3,column=1, columnspan=3)
        self.file_label = tk.Label(self.window, text='SQL file: ')
        self.file_label.grid(row=5, column=0, columnspan=1)
        self.file_field = tk.Text(self.window, height = 1, width = 120, font=('calibre',12))
        self.file_field.grid(row=5, column=1, columnspan=2)
        self.count_label = tk.Label(self.window, text='Products:')
        self.count_label.grid(row=6, column=0)
        self.count_field = tk.Text(self.window, height = 1, width = 120, font=('calibre',12))
        self.count_field.grid(row=6, column=1, columnspan=2)
        self.revenue_label = tk.Label(self.window, text='Revenue:')
        self.revenue_label.grid(row=7, column=0)
        self.revenue_field = tk.Text(self.window, height = 1, width = 120, font=('calibre',12))
        self.revenue_field.grid(row=7, column=1, columnspan=2)


def sort_by_seller(product_tally):
    ui.tally_field.delete(1.0,tk.END)
    for manufacturer in manufacturer_tally:
        if not manufacturer: continue
        ui.tally_field.insert(tk.END, f' {manufacturer}: {manufacturer_tally[manufacturer]}\n')
        for product, qty in product_tally.items():
            if manufacturers_dict[product] == manufacturer:
                ui.tally_field.insert(tk.END, f' {qty : ^5}{product}\n')
    ui.tally_field.insert(tk.END, f' Other: {manufacturer_tally.get(0)}\n')
    for product, qty in product_tally.items():
        if not manufacturers_dict[product]:
            ui.tally_field.insert(tk.END, f' {qty : ^5}{product}\n')

def fetch_processing_order_data():
    orders = []
    comment_dict = {}
    # Define the search criteria for processing orders
    search_criteria = (
        '?searchCriteria[filter_groups][0][filters][0][field]=status'
        '&searchCriteria[filter_groups][0][filters][0][value]=processing'
        '&searchCriteria[filter_groups][0][filters][0][condition_type]=eq'
    )
    # Make the GET request to the /V1/orders endpoint with the search criteria
    order_data = requests.get(f'{base_url}/rest/V1/orders{search_criteria}', headers=headers).json()
    for order in order_data.get('items', []):
        order_info = {
            'customer_comment': order.get('osc_order_comment', ""),
            'order_number': order.get('increment_id'),
            'customer_firstname': order.get('customer_firstname', 'N/A'),
            'customer_lastname': order.get('customer_lastname', 'N/A'),
            'customer_country': order.get('extension_attributes', {}).get('shipping_assignments', [{}])[0].get('shipping', {}).get('address', {}).get('country_id', 'N/A'),
            'customer_phone': order.get('extension_attributes', {}).get('shipping_assignments', [{}])[0].get('shipping', {}).get('address', {}).get('telephone', 'N/A'),
            'customer_email': order.get('customer_email', 'N/A'),
            'shipping_method': order.get('shipping_description', 'N/A')
        }
        order_info['payment_method'] = order.get('payment', {}).get('method', 'N/A')  # Fallback to 'N/A' if not available
        order_info['order_status'] = order.get('status', 'N/A')
        order_info['order_creation_date'] = order.get('created_at', 'N/A')
        order_info['amount_owed'] = order.get('base_grand_total', 'N/A')
        product_details = []
        # Iterate over each item in the order to extract product details
        for item in order.get('items', []):
            if item['product_type'] != 'simple': continue
            product_info = {
                'product_name': item['name'],
                'product_type': item['product_type'],
                'product_id': item['product_id'],
                'price': item.get('price_incl_tax') if item.get('price_incl_tax') else item['parent_item'].get('price_incl_tax'),
                'sku': item['sku'],
                'manufacturer': fetch_product_manufacturer(item['sku']),
                'qty_ordered': item['qty_ordered']}
            if product_info['manufacturer']:
                product_info['manufacturer'] = manufacturer_dict.get(int(product_info['manufacturer']))
            product_details.append(product_info)
        # Add the product details to the order info
        order_info['products'] = product_details
        if order_info['customer_comment'] != "":
            customer_name = f"{order_info['customer_firstname']} {order_info['customer_lastname']}"
            key = f"{order_info['order_number']} - {customer_name} - {order_info['customer_email']}"
            comment_dict[key] = order_info['customer_comment']
        orders.append(order_info)
    return orders, comment_dict
    
def tally_products_api(order_details):
    global manufacturers_dict
    global manufacturer_tally
    product_tally = Counter()
    product_revenue = 0
    for order in order_details:
        for product in order['products']:
            try:
                product_name = product['product_name']
                product_type = product['product_type']
                manufacturer = product['manufacturer']
                qty_ordered = int(product['qty_ordered'])
                revenue = float(product['price'])
                product_revenue += revenue * qty_ordered
                if product_type.lower() == 'simple':
                    product_tally.update({product_name: qty_ordered})
                    manufacturer_tally.update({manufacturer: qty_ordered})
                    manufacturers_dict[product_name] = manufacturer
            except KeyError as key:
                print(f'ERROR: missing expected product detail: {key}')
    sorted_product_tally = dict(product_tally.most_common())
    manufacturer_tally = dict(manufacturer_tally.most_common())
    return sorted_product_tally, product_revenue

def fetch_product_manufacturer(product_sku):
    endpoint = f'/rest/V1/products/{product_sku}'
    response = requests.get(f'{base_url}{endpoint}', headers=headers)
    if response.status_code != 200:
        return f"Failed to retrieve product details. Status code: {response.status_code}"
    product_details = response.json()
    custom_attributes = product_details.get('custom_attributes', [])
    manufacturer_value = next((attr['value'] for attr in custom_attributes if attr['attribute_code'] == 'manufacturer'), 0)
    return manufacturer_value if manufacturer_value else 0

def main():
    global ui
    ui = UI()
    orders, customer_comment_dict = fetch_processing_order_data()
    product_tally, product_revenue = tally_products_api(orders)
    ui.count_field.delete(1.0,tk.END)
    ui.count_field.insert(tk.END, f'{sum(product_tally.values())}')
    ui.revenue_field.delete(1.0,tk.END)
    ui.revenue_field.insert(tk.END, f'€{round(product_revenue, 2)}')
    sort_by_seller(product_tally)
    ui.tally_field.insert(tk.END, f'\nORDER COMMENTS:')
    if not customer_comment_dict: ui.tally_field.insert(tk.END, '\n0 of those orders have customer comments.\n')
    for order in customer_comment_dict:
        ui.tally_field.insert(tk.END, f' {order} -  \n"{customer_comment_dict[order]}"\n')
    ui.window.mainloop()

if __name__=='__main__':
    main()
