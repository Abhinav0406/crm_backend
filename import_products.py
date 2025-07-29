import requests

API_URL = 'http://localhost:8000/api/products/create/'
TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzUzNDQ0Mzc3LCJpYXQiOjE3NTM0NDA3NzcsImp0aSI6ImQ3OTg5OGQxMmY1ODQ1NDdhZjk2OTY1ZTRlM2EzNjBkIiwidXNlcl9pZCI6OX0.hgNL_tacx20K58NEp2PSySX0YPiu1OhPHFT3DJu9IVo'

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

product_data = {
    "G.AD.RING": ["Casting CZ", "Itlian", "Machine", "MS"],
    "G.AD.EARRING": ["Casting CZ", "Itlian", "Machine", "MS"],
    "G.18 CHAIN": ["Rudrax PL", "Two tone", "White gold"],
    "G.AD P.SET": ["Casting CZ"],
    "G.PENDENT": ["Handmade"],
    "G.BACCHA LUCKEY": ["Machine", "MS"],
    "G.LUCKEY": ["Rudrax PL", "Casting PL", "Handmade", "Itlian", "Machine", "MS", "Nawabi", "Rudrax PL", "Two tone", "Vertical hollow"],
    "G.MANGALSUTRA": ["Handmade", "Machine"],
    "G.CHAIN": ["Handmade", "Itlian", "Machine", "Nawabi", "Two tone", "Vertical hollow"],
    "G.AD PENDENT": ["Casting CZ"],
    "G.AD BRACLET": ["Casting CZ", "Casting PL", "Handmade", "MS"],
    "G.EARRINGS": ["Rudrax PL"],
    "G.RING": ["Handmade"],
    "G.BACCHA KADLI": ["Handmade"],
    "G.MALA": ["Handmade", "Hirakenthi", "Machine", "Rudrax PL", "Tulsi mala", "Vertical Solid"],
    "J.EARRINGS": ["Heritage", "Jadtar", "Semi jadtar", "Traditional", "Handmade"],
    "G.DOKIYU": ["Traditional"],
    "J.KANSER": ["Jadtar"],
    "G.BANGLES": ["Casting PL", "fancy"],
    "J.BRACLET": ["Heritage", "Jadtar", "Traditional"],
    "J.SET": ["Heritage", "Jadtar", "Semi jadtar", "Traditional"],
    "J.KADA": ["Heritage", "Jadtar", "Semi jadtar", "Traditional"],
    "G.PENDENT SET": ["Handmade"],
    "J.RING": ["Jadtar", "Traditional"],
    "G.AD BANGLES": ["Casting CZ", "Casting PL"],
    "G.KADLI": ["Copper"],
    "G.KADA": ["Handmade"],
    "14CT DI.VI.SET": [],
    "14CT DI.VI.BRACELET": [],
    "14CT DI.VI.EARRING": [],
}

def get_category_id(prod_name):
    if prod_name.startswith("G."):
        return 1  # Gold
    elif prod_name.startswith("J."):
        return 3  # Polki
    elif prod_name.startswith("14CT DI.VI."):
        return 2  # Diamond
    else:
        return 1  # Default to Gold if not matched

tenant_id = 4  # mandeep jewelries
sku_counter = 1
products = []

for prod_name, subtypes in product_data.items():
    category_id = get_category_id(prod_name)
    if subtypes:
        for subtype in subtypes:
            products.append({
                "name": f"{prod_name} - {subtype}",
                "sku": f"{prod_name.replace(' ', '').replace('.', '').upper()}_{subtype.replace(' ', '').upper()}_{sku_counter:03d}",
                "tenant": tenant_id,
                "category": category_id,
                "cost_price": 0,
                "selling_price": 0,
            })
            sku_counter += 1
    else:
        products.append({
            "name": prod_name,
            "sku": f"{prod_name.replace(' ', '').replace('.', '').upper()}_{sku_counter:03d}",
            "tenant": tenant_id,
            "category": category_id,
            "cost_price": 0,
            "selling_price": 0,
        })
        sku_counter += 1

for product in products:
    resp = requests.post(API_URL, json=product, headers=headers)
    print(product["name"], resp.status_code, resp.json())