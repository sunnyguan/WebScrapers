import selenium
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs4
import time
import requests 
import os.path
import sys

def camelCase(st):
    output = ''.join(x for x in st.title() if x.isalnum())
    return output[0].lower() + output[1:]

username = sys.argv[1]
passwd = sys.argv[2]

options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.get('https://open.kattis.com/login/email')

user = driver.find_element_by_id('user_input')
password = driver.find_element_by_id('password_input')
user.send_keys(username)
password.send_keys(passwd)
driver.find_element_by_name('submit').click()
user_link = driver.find_element_by_css_selector('#menu1 > li:nth-child(2) > a:nth-child(1)').get_attribute('href')
driver.get(user_link)
cookies = driver.get_cookies()
s = requests.Session()
driver.quit()

cookie_str = ''
for cookie in cookies:
    cookie_str += cookie['name'] + "=" + cookie['value'] + "; "

url = "https://open.kattis.com/users/sunny-guan"
payload = {}
headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
  'Accept-Language': 'en-US,en;q=0.5',
  'Connection': 'keep-alive',
  'Referer': 'https://open.kattis.com/',
  'Cookie': cookie_str,
  'Upgrade-Insecure-Requests': '1'
}

response = requests.request("GET", url, headers=headers, data = payload)
resp = response.text;

soup = bs4(resp, features='html.parser')
allsubs = soup.select('tbody > tr')
good_subs = [[c.get('data-submission-id'), camelCase(c.select('#problem_title > a')[0].text)] for c in allsubs if len(c.select('span.accepted')) != 0]
for id in good_subs:
    filename = id[1] + '.java'
    if not os.path.isfile(filename):
        resp2 = requests.request("GET", 'https://open.kattis.com/submissions/' + id[0] + '/source/Main.java', headers=headers, data=payload)
        f = open(filename, "w")
        f.write(resp2.text)
        f.close()
        print('written: ' + id[1])
    else:
        print('skipped (exist already): ' + id[1])