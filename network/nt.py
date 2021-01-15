from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re

PATH = "./chromedriver.exe"

driver = webdriver.Chrome(PATH)

driver.get('http://www.nasdaqtrader.com/')

driver.refresh()
driver.find_element_by_id('tab4').click()
time.sleep(1)
driver.find_element_by_id('ahButton').click()
time.sleep(1)


soup = BeautifulSoup(driver.page_source, 'html.parser')


t = soup.find(text=re.compile('Last updated*'))
print(str(t))
data = []
table = soup.find('div', attrs={'id':'asGrid'})

table = table.find('div')
table_body = table.findAll('tbody')[1]

for i in table_body.findAll('tr'):
    col =i.find_all('td')
    cols = [ele.text.strip() for ele in col]
    data.append(cols)

data2 = []
table = soup.find('div', attrs={'id':'ahGrid'})

table = table.find('div')
table_body = table.findAll('tbody')[1]

for i in table_body.findAll('tr'):
    col =i.find_all('td')
    cols = [ele.text.strip() for ele in col]
    data2.append(cols)

print(data)



