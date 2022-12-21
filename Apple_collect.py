import pandas as pd
from zipfile import ZipFile
import itertools
import requests

#######
#Apple#
#######
#Apple could also be scraped, but the way they provide downloadable reports is used here to highlight familiarity with a different skill, navigating and organising data through code

url = "https://www.apple.com/legal/zip/transparency/Apple_Transparency_Report.zip" #loads url of data
file = requests.get(url) #downloads file
open("Apple.zip", "wb").write(file.content) #writes file into local storage

#Because file is zipped, we need to unzip it
with ZipFile("Apple.zip","r") as zObject: #opens zip in a way that is suitable for the module being used
    zObject.extract("account_requests.csv") #extracts files
    zObject.extract("device_requests.csv")
    zObject.extract("emergency_requests.csv")
    zObject.extract("financial_identifier_requests.csv")

apple_financial = pd.read_csv("financial_identifier_requests.csv") #loads files into python
apple_emergency = pd.read_csv("emergency_requests.csv")
apple_devices = pd.read_csv("device_requests.csv")
apple_accounts = pd.read_csv("account_requests.csv")

apple_financial = apple_financial[apple_financial["TR Period"].str.contains("2020|2019") == True] #filters files so that only the relevant time period is included
apple_emergency = apple_emergency[apple_emergency["TR Period"].str.contains("2020|2019") == True]
apple_devices = apple_devices[apple_devices["TR Period"].str.contains("2020|2019") == True]
apple_accounts = apple_accounts[apple_accounts["TR Period"].str.contains("2020|2019") == True]

apple_countries = list(set(itertools.chain(apple_financial["Country/Region"], apple_emergency["Country/Region"],apple_devices["Country/Region"],apple_accounts["Country/Region"]))) #collects all mentioned countries
apple_countries.sort() #sorts list of all mentioned countries alphabetically

apple_periods = ["2019 H1","2019 H2","2020 H1","2020 H2"] #list of relevant periods

apple_data = pd.DataFrame() #creates empty dataframe to store data later
i = 0

while i < len(apple_countries): #loop that goes through country names and saves data that appears next to the countries
    y = 0
    current_criteria = [apple_countries[i],""] #determines the country name this iteration is checking for
    while y < len(apple_periods):
        current_criteria[1] = apple_periods[y] #determines the period this nested loop is looking for alongside the country name
        row = [current_criteria[1], current_criteria[0], 0, 0, 0] #sets a default entry (so if a country doesn't have an entry next to it for a certain date, the 0s stay)

        x = 0
        while x < len(apple_emergency): #checks the emergency requests CSV for entries of currently selected country and period combination
            test = apple_emergency.iloc[x, :] #saves a row from the CSV
            if test[3] == current_criteria[0] and test[0] == current_criteria[1]: #checks whether row matches criteria
                row[2] = int(row[2]) + int(test[4]) #NO requests updated
                row[3] = int(row[3]) + int(test[7]) #NO provided updated
                x += 1
            else: #if no match, the previously created default entry is not updated
                x += 1
                continue

        x = 0
        while x < len(apple_devices): #checks the device requests CSV
            test = apple_devices.iloc[x, :]
            if test[3] == current_criteria[0] and test[0] == current_criteria[1]:
                row[2] = int(row[2]) + int(test[4])
                row[3] = int(row[3]) + int(test[6])
                x += 1
            else:
                x += 1
                continue

        x = 0
        while x < len(apple_financial): #checks the financial requests CSV
            test = apple_financial.iloc[x, :]
            if test[3] == current_criteria[0] and test[0] == current_criteria[1]:
                row[2] = int(row[2]) + int(test[4])
                row[3] = int(row[3]) + int(test[6])
                x += 1
            else:
                x += 1
                continue

        x = 0
        while x < len(apple_accounts): #checks the account requests CSV
            test = apple_accounts.iloc[x, :]
            if test[3] == current_criteria[0] and test[0] == current_criteria[1]:
                row[4] = int(test[5]) #NO accounts requested gets updated
                x += 1
            else:
                x += 1
                continue

        apple_data = pd.concat([apple_data, pd.DataFrame(row).transpose()]) #after checking every country/period combination, saves results to a new dataframe
        y += 1
    i += 1

apple_data.columns = ["Period","Country","Requests","Produced","Accounts"] #changes column names

#save data as backup / for final use
apple_data.to_csv("apple_data.csv")
#apple_data = pd.read_csv("apple_data.csv").iloc[:,1:]