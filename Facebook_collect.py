import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

##########
#Facebook#
##########
#Like other platforms, Facebook could be done by downloading the provided CSV's, but scarping is used to show familiarity with the skill
countries = pd.read_csv("country_list_and_codes.csv").iloc[:,1:]
driver = webdriver.Chrome()#initialize automated browser
fb_data = pd.DataFrame()#creates a blank dataframe to store data in later
url = "https://transparency.fb.com/data/government-data-requests/country/XX/"
current_code = "XX"
driver.get(url) #navigates to the website
time.sleep(2) #waits for the initial page to load
driver.find_element(By.CLASS_NAME, "_9o-r ._9o-t").click() #accepts cookies
time.sleep(2)

for code in countries["Alpha-2 code"]: #see google data collection for next 4 lines
    time.sleep(2)
    url = url.replace(str(current_code),str(code))
    current_code = code
    driver.get(url)
    validity_check = driver.find_element(By.CLASS_NAME, "_9qfj").text #used to check the title text of a page

    if validity_check == "Requests by country": #if requests by country - the country code attempted is not used by Facebook
        print("No data for ", code)
        continue

    else:
        time.sleep(1)
        slicer = driver.find_elements(By.CLASS_NAME, "x1ypdohk") #find the buttons that navigate the time period
        print("There is an entry for ", code)
        for i in range(6): #click the button 6 times to get to the first half of 2019
            slicer[0].click()

        for i in range(4): #we only need 4 total half-year data, so this is used to keep track of that
            data = driver.find_elements(By.CLASS_NAME, "_9nos") #collect textual elements
            temp_table = pd.DataFrame( #create table from relevant elements
            {'Period': [data[33].text], 'Country': [str(code)],
             'Requested': [data[34].text], '%Produced': [data[42].text],
             'Accounts': [data[40].text]})

            fb_data = pd.concat([fb_data,temp_table]) #update table with newly collected values
            slicer[1].click() #change period to the next half-year

#Translating %disclosed to integers:
i = 0
while i < len(fb_data["%Produced"]):
    fb_data.iloc[i, 3] = fb_data.iloc[i,3].replace("%","")
    fb_data.iloc[i, 2] = fb_data.iloc[i,2].replace(",","")
    fb_data.iloc[i, 3] = int(fb_data.iloc[i, 3])
    fb_data.iloc[i, 2] = int(fb_data.iloc[i, 2])
    try:
        fb_data.iloc[i,3] = int(round((fb_data.iloc[i,2] * (fb_data.iloc[i,3]/100)),0))
    except:
        pass
    i += 1

fb_data.columns = ["Period","Country","Requests","Produced","Accounts"]

fb_data.to_csv("fb_data_fin.csv")
#fb_data_fin = pd.read_csv("fb_data_fin.csv").iloc[:,1:]