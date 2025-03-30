from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import yaml
from apprise import Apprise
from datetime import datetime
import re
import os
timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print(timestamp)
    
apobj = Apprise()

options = Options()
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")
options.add_argument("--user-data-dir=/config/session");  
driver = webdriver.Chrome(options=options)
    
with open('configCruise.yaml', 'r') as file:
    data = yaml.safe_load(file)
    if 'apprise' in data:
        for apprise in data['apprise']:
            url = apprise['url']
            apobj.add(url)
    
    if 'cruises' in data:
        for cruises in data['cruises']:
            cruiseURL = cruises['cruiseURL'] 
            cruiseXPath = cruises['cruiseXPath']
            paidPrice = float(cruises['paidPrice'])
    
            driver.get(cruiseURL)
            priceString = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, cruiseXPath))).text

            priceString = priceString.replace(",", "")
            m = re.search("\\$(.*)USD", priceString)
            priceOnlyString = m.group(1)
            price = float(priceOnlyString)

            if price < paidPrice:
                textString = "Rebook! New Price of " + str(price) + " is lower than " + str(paidPrice)
                print(textString)
                apobj.notify(body=textString, title='Cruise Price Alert')
            else:
                print("You have best Price of " + str(paidPrice) )
                if price > paidPrice:
                    print("\t Current Price is higher: " + str(price) )

