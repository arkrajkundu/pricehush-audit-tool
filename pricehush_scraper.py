import requests
from bs4 import BeautifulSoup
import pandas as pd

data = {'pricehush': [], 'price': [], 'amazon': [], 'flipkart': []}

base_url = "https://pricehush.com/brand/lenovo/page/"
total_pages = 10

urls = []

print("Appending URLs...")

for i in range(1, total_pages+1):
  urls.append(f'{base_url}{i}')

sublinks = []
pricehush_prices = []
amazon_links = []
flipkart_links = []

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


for link in sublinks:
  data['pricehush'].append(link)
  
for price in pricehush_prices:
  data['price'].append(price)

for amazon in amazon_links:
  data['amazon'].append(amazon)
  
for flipkart in flipkart_links:
  data['flipkart'].append(flipkart)

df = pd.DataFrame.from_dict(data)
df.to_excel("data.xlsx", index=False)