import requests
from bs4 import BeautifulSoup
import pandas as pd
headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'}

data = {'pricehush': [], 'price': [], 'amazon': [], 'flipkart': [], 'amazon_prices': [], 'amazon_outofstock': [], 'flipkart_prices': [], 'flipkart_outofstock': []}

base_url = "https://pricehush.com/brand/dell/page/"
total_pages = 6

urls = []

print("Appending URLs...")

for i in range(1, total_pages+1):
  urls.append(f'{base_url}{i}')

sublinks = []
pricehush_prices = []
amazon_links = []
flipkart_links = []
amazon_prices = []
flipkart_prices = []
amazon_outofstock = []
flipkart_outofstock = []

print("Requesting URLs and filling sublinks, prices...")

for url in urls:
  r = requests.get(url)
  soup = BeautifulSoup(r.text, 'html.parser')
  
  links = soup.select("h3.wd-entities-title > a")
  prices = soup.select("span.price > span.amount > bdi")
  
  for link in links:
    sublinks.append(link.get('href'))
    
  for price in prices:
    pricehush_prices.append(price.get_text())

print("Extracting amazon/flipkart from each link...")

i = 1

for sublink in sublinks:
  
  r = requests.get(sublink)
  soup = BeautifulSoup(r.text, 'html.parser')
  
  price_div = soup.select("p.price > a")
  
  print(f'Loop: {i}')
  
  if len(price_div) == 0:
    amazon_links.append("NULL")
    flipkart_links.append("NULL")
    
  if len(price_div) == 2:
    amazon_links.append(price_div[0].get('href'))
    flipkart_links.append(price_div[1].get('href'))
    
  if len(price_div) == 1:
    store_link = price_div[0].get('href')
    if 'flipkart' in store_link:
      amazon_links.append("NULL")
      flipkart_links.append(store_link)
    elif 'amazon' in store_link:
      amazon_links.append(store_link)
      flipkart_links.append("NULL")
      
  i += 1

# Extracting amazon prices

for amazon_link in amazon_links:
  
  # NULL Check
  if(amazon_link == 'NULL'):
    amazon_prices.append('NA')
    amazon_outofstock.append('NA')
    continue
  
  r = requests.get(amazon_link, headers=headers)
  soup = BeautifulSoup(r.text, 'html.parser')
  
  # Cases
  
  prices = soup.select('span.priceToPay > span > span.a-price-whole') # Best case
  if(len(prices)!=0):
    amazon_prices.append(prices[0].get_text())
    amazon_outofstock.append('No')
  else:
    prices = soup.find_all('span', class_=lambda x: x and 'a-size-medium' in x and 'a-color-success' in x) # Unavailable case
    if(len(prices)!=0):
      amazon_prices.append(prices[0].get_text())
      amazon_outofstock.append('Yes')
    else:
      prices = soup.select('td.a-span12 > span.apexPriceToPay > span.a-offscreen') # Weird case
      amazon_prices.append('NA')
      amazon_outofstock.append('No')

# Extracting flipkart prices

for flipkart_link in flipkart_links:
  
    # NULL Check
  if(flipkart_link == 'NULL'):
    flipkart_prices.append('NA')
    flipkart_outofstock.append('NA')
    continue
  
  r = requests.get(flipkart_link, headers=headers)
  soup = BeautifulSoup(r.text, 'html.parser')
  
  prices = soup.find_all('div', class_=lambda x: x and 'Nx9bqj' in x and 'CxhGGd' in x)
  stock_status = soup.select('div.Z8JjpR')
  
  if(len(prices)!=0):
    flipkart_prices.append(prices[0].get_text())
  else:
    flipkart_prices.append('NA')
    
  if(len(stock_status)!=0):
    flipkart_outofstock.append('Yes')
  else:
    flipkart_outofstock.append('No')

# Adding lists to data object

for link in sublinks:
  data['pricehush'].append(link)
  
for price in pricehush_prices:
  data['price'].append(price)

for amazon in amazon_links:
  data['amazon'].append(amazon)
  
for flipkart in flipkart_links:
  data['flipkart'].append(flipkart)

for amazon_price in amazon_prices:
  data['amazon_prices'].append(amazon_price)
  
for flipkart_price in flipkart_prices:
  data['flipkart_prices'].append(flipkart_price)
  
for amazon_oos in amazon_outofstock:
  data['amazon_outofstock'].append(amazon_oos)

for flipkart_oos in flipkart_outofstock:
  data['flipkart_outofstock'].append(flipkart_oos)

# Exporting to excel

df = pd.DataFrame.from_dict(data)
df.to_excel("dell.xlsx", index=False)
