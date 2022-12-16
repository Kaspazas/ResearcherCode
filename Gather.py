import pandas as pd
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import selenium
from selenium.common.exceptions import ElementClickInterceptedException
from selenium import webdriver
import requests
from selenium.webdriver.common.by import By
import time

#Collect country codes (alpha-2,not 3) and names. This uses the more basic requests package
url = "https://countrycode.org/"
raw_country_codes = requests.get(url).content #fetch the page

tables = pd.read_html(raw_country_codes) #pandas saves all tables into a list of tables
countries = tables[1] #select the appropriate table

##loop used to save the alpha-2 codes into a separate list, used to remove alpha-3 codes because theyre not used in relevant data (Google, MS, Apple, Facebook)
isos = []
for entry in countries["ISO CODES"]:
    iso = entry[:2]
    isos.append(iso)

countries["ISO CODES"] = isos #replaces the existing alpha-2/3 column with just alpha-2 values
countries.drop(["COUNTRY CODE"], axis=1) #removes a useless column

countries.to_csv("country_list_and_codes.csv") #saves DataFrame as a csv
#countries = pd.read_csv("country_list_and_codes.csv").iloc[:,1:] #load the file into environment

########
#Google#
########
#This section uses HTML adresses to go through data, as opposed to having to navigate a page (which is needed later)
#url = "https://transparencyreport.google.com/user-data/overview?hl=en&user_requests_report_period=series:requests,accounts;authority:LT;time:&lu=user_requests_report_period&legal_process_breakdown=expanded:0"
url = "https://transparencyreport.google.com/user-data/overview?hl=en&user_requests_report_period=series:requests,accounts;authority:XX;time:&lu=user_requests_report_period&legal_process_breakdown=expanded:0"
current_code = "XX"
driver = webdriver.Chrome()
for code in countries["ISO CODES"]:

    url = url.replace(str(current_code),str(code))
    current_code = code
    #Using Selenium, this section navigates to the pages (where the
    #search_url="https://transparencyreport.google.com/user-data/overview?hl=en&user_requests_report_period=series:requests,accounts;authority:LT;time:&lu=user_requests_report_period&legal_process_breakdown=expanded:0"

    driver.get(url) #navigates to the website
    time.sleep(2) #wait for page to load
    #driver.find_element(By.CLASS_NAME, "element-row.expandable").click() #closes an expandable selection, cause otherwise downloaded elements would be polluted
    table_data = driver.find_elements(By.CLASS_NAME, "md-lite mat-row") #downloads relevant elements
    if len(table_data) == 0:
        continue
    else:

        google_data = pd.DataFrame()

        i = 0
        while i<len(table_data):
            row = pd.DataFrame(table_data[i].text.split("\n")).transpose()
            count = table_data[i].text.split("\n")
            country = code
            if len(count) == 1:
                print("skipping, no data at ", i)
                i += 1
                continue
            else:
                google_data = pd.concat([google_data, row], axis=0, ignore_index=True)
                #google_data = pd.concat([google_data,country], axis=1, ignore_index=True)
                i += 1
        google_data.columns = ["Period","Requests","Accounts","%Produced"]#,"Country"]
        google_data = google_data[google_data["Period"].str.contains("2020|2019")==True]





