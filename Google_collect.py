import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time

########
#Google#
########
#Google transparency data could be downloaded in the form of Excel files, but is scraped here.
countries = pd.read_csv("country_list_and_codes.csv").iloc[:,1:]
url = "https://transparencyreport.google.com/user-data/overview?hl=en&user_requests_report_period=series:requests,accounts;authority:XX;time:&lu=user_requests_report_period&legal_process_breakdown=expanded:0"
current_code = "XX"
driver = webdriver.Chrome()#initialize automated browser
google_data = pd.DataFrame()#creates a blank dataframe to store data in later

for code in countries["Alpha-2 code"]: #this loop goes through the previously collected country codes
    url = url.replace(str(current_code),str(code)) #changes the url to a new country code
    current_code = code #save current country code to be used later in changing it
    driver.get(url) #navigates to the website
    time.sleep(2) #wait for page to load
    table_data = driver.find_elements(By.CLASS_NAME, "md-lite mat-row") #downloads relevant elements
    if len(table_data) == 0: #if collected elements are empty, skip this country
        print("No data for ", code)
        continue
    else:
        print("Found data for ", code)
        i = 0
        while i<len(table_data): #if data, iterates over table data
            row = table_data[i].text.split("\n") #the entries were a single string which is broken up here
            row.append(code) #adds country code to the entry
            row = pd.DataFrame(row).transpose()
            count = table_data[i].text.split("\n")#used to detect if the data currently selected data is of the expected lenght
            if len(count) < 4:
                i += 1
                continue
            else:
                google_data = pd.concat([google_data, row], axis=0, ignore_index=True) #adds info to overall data table
                i += 1

google_data.columns = ["Period","Requests","Accounts","%Produced","Country"] #sets column names

google_data = google_data[google_data.columns[[0,1,2,4,3]]]#rearranges data to match other sources better
google_data = google_data[google_data["Period"].str.contains("2020|2019")==True] #filters data to only include relevant time periods

#Backup of whole dataset
google_data.to_csv("raw_google.csv")
#google_data = pd.read_csv("raw_google.csv")

countries_available = list(set(google_data["Country"]))#saves all the countries that were available

#translating % produced to number produced
i = 0
while i < len(google_data["%Produced"]):
    try:
        google_data.iloc[i, 3] = google_data.iloc[i,3].replace("%","")
    except:
        pass
    try:
        google_data.iloc[i, 2] = google_data.iloc[i,2].replace(",","")
    except:
        pass
    try:
        google_data.iloc[i, 3] = int(google_data.iloc[i, 3])
    except:
        pass
    try:
        google_data.iloc[i, 2] = int(google_data.iloc[i, 2])
    except:
        pass
    try:
        google_data.iloc[i,3] = int(round((google_data.iloc[i,2] * (google_data.iloc[i,3]/100)),0))
    except:
        pass
    i += 1

google_data.columns = ["Period","Country","Requests","Produced","Accounts"]

#final dataset
google_data.to_csv("google_data.csv")
#google_data = pd.read_csv("google_data.csv")