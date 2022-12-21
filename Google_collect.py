import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import time


########
#Google#
########
#Google transparency data could be downloaded in the form of Excel files, but is scraped here.

countries = pd.read_csv("country_list_and_codes.csv").iloc[:,1:] #loads list of countries
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
#google_data = pd.read_csv("google_data.csv").iloc[:,1:]

# i = 0
# while i < len(google_data):
#     google_data["Period"][i] = google_data["Period"][i].replace("–","")
#     google_data["Accounts"][i] = google_data["Accounts"][i].replace(",", "")
#     i +=1

periods = ["Jan 2019  Jun 2019","Jul 2019  Dec 2019","Jan 2020  Jun 2020","Jul 2020  Dec 2020"]
countries_in_google = list(set(google_data["Country"]))
countries_in_google.sort()

google_data_updated = pd.DataFrame() #creates empty dataframe to store data later
i = 0

while i < len(countries_in_google): #loop that goes through country names and saves data that appears next to the countries
    y = 0
    current_criteria = [countries_in_google[i],""] #determines the country name this iteration is checking for
    while y < len(periods):
        current_criteria[1] = periods[y] #determines the period this nested loop is looking for alongside the country name
        row = [current_criteria[1], current_criteria[0], 0, 0, 0] #sets a default entry (so if a country doesn't have an entry next to it for a certain date, the 0s stay)

        x = 0
        while x < len(google_data):
            test = google_data.iloc[x, :] #saves a row from the CSV
            if test[1] == current_criteria[0] and test[0] == current_criteria[1]: #checks whether row matches criteria
                row[2] = int(row[2]) + int(test[2]) #NO requests updated
                row[3] = int(row[3]) + int(test[3]) #NO provided updated
                row[4] = int(row[4]) + int(test[4])
                x += 1
            else: #if no match, the previously created default entry is not updated
                x += 1
                continue

        google_data_updated = pd.concat([google_data_updated, pd.DataFrame(row).transpose()]) #combines existing dataframe with the current row
        y += 1
    i += 1

google_data_updated.columns = ["Period", "Country", "Requests", "Produced", "Accounts"]  #changes column names

#Changing country codes to previously collected country names
i = 0
while i <len(google_data_updated): #for every country in the fb data list
    x = 0
    while x <len(countries): #for every country in the country list
        if google_data_updated.iloc[i,1] == countries.iloc[x,1]: #if the Alpha-2 of the country currently selected from Google list matches the currently selected country code from countries list
            google_data_updated.iloc[i,1] = countries.iloc[x,0] #Change country alpha-2 in Google list to appropriate english name
            x += 1
        else:
            x += 1
    i += 1

#save data as backup / final use
google_data_updated.to_csv("google_data_fin.csv")