import requests
import pandas as pd
import itertools

###########
#Microsoft#
###########
#Microsoft only provides file links, so they are used
#These are quite inconveniently constructed, so to process them with code, the script is verbose to be understandable
file_names = ["MS_19_1.xlsx", "MS_19_2.xlsx", "MS_20_1.xlsx", "MS_20_2.xlsx"] #list of filenames to be used in storing downloaded files
urls = ["https://query.prod.cms.rt.microsoft.com/cms/api/am/binary/RE49sEF", "https://query.prod.cms.rt.microsoft.com/cms/api/am/binary/RE4sg0d", #list of urls where CSV's are available
        "https://query.prod.cms.rt.microsoft.com/cms/api/am/binary/RE4GuvI", "https://query.prod.cms.rt.microsoft.com/cms/api/am/binary/RWAlQ4"]

i=0
while i < 4:
    url = urls[i]
    file = requests.get(url) #downloads file
    open(file_names[i], "wb").write(file.content) #writes file into local storage
    file.close() #deletes files from memory after its stored on computer
    i += 1

sheet_names = ["Criminal","Emergencies","Civil Legal Requests"] #sets names of sheets so that they don't have to be typed out later
file_names = ["MS_19_1.xlsx","MS_19_2.xlsx","MS_20_1.xlsx","MS_20_2.xlsx"] #sets names of files so that they don't have to be typed out later
periods = ["Jan - Jun 2019","Jul - Dec 2019","Jan - Jun 2020","Jul - Dec 2020"] #sets names of periods so that they don't have to be typed out later
all_ms_reports = [] #creates empty list which will be used to store aggregated data

##################################################################################
y=0
while y < len(file_names): #for every file

    ms_sheet = pd.read_excel(file_names[y], sheet_name=sheet_names[0]) #read the first sheet
    countries = list(ms_sheet.iloc[4:,1]) #saves country names as a list
    requests = list(ms_sheet.iloc[4:, 3]) #saves numbers of requests
    accounts = list(ms_sheet.iloc[4:, 4]) #saves numbers of accounts
    produced = [] #blank list to be updated with number of disclosures
    i = 4
    while i < (len(countries) + 4): #As per the government surveillance report published on surfshark.com, both types of disclosures need to be added up
        produced.append((int(ms_sheet.iloc[i, 7]) + int(ms_sheet.iloc[i, 9]))) #combine both types of disclosures and adds them to the produced list
        i += 1

    len_count = len(countries) #saves the lenght of the countries

    ms_sheet = pd.read_excel(file_names[y], sheet_name=sheet_names[1]) #read the second sheet of the file
    i = 4 #the useful data only starts appearing on row 6 is in the actual file. But the way the file is read in pyhton, it's row 4, so we only collect data from row 4 onwards
    while i < len(ms_sheet):
        row = ms_sheet.iloc[i, :] #saves row
        x = 0
        while x < len_count: #this loop goes through previously saved countries (from first sheet) and checks whether they exist in this sheet
            country = countries[x]
            if row[1] == country: #if country in the current row mathces the country being checked
                requests[x] = int(requests[x]) + int(row[3]) #adds the number of requests from this sheet to existing number
                accounts[x] = int(accounts[x]) + int(row[4]) #adds the number of accounts from this sheet to existing number
                produced[x] = (int(produced[x]) + int(row[7]) + int(row[9])) #adds the number produced from this sheet to existing number
            elif row[1] in countries: #if the current country doesnt match with country in row, this catches if it exists elsewhere in the list of countries
                print(row[1], " exists in list, but not here")
            else: #if the current country doesnt match with country in row, and is not in the list of countries, we save the country and relevant values
                countries.append(row[1])
                requests.append(row[3])
                accounts.append(row[4])
                produced.append((int(row[7]) + int(row[9])))
                print("adding new values and country ", row[1])
            print(x)
            x += 1

        i += 1

    ms_sheet = pd.read_excel(file_names[y], sheet_name=sheet_names[2])
    i = 4
    while i < len(ms_sheet):
        row = ms_sheet.iloc[i, :]

        if row[1] == "USA": #For some reason, in the civil requests sheet of the MS excel files, the names of US and UK are shortened?
            row[1] = "United States" #so these lines change them to the standard name used in other sheets
        if row[1] == "UK":
            row[1] = "United Kingdom"

        x = 0
        while x < len_count: #this loop goes through previously saved countries (from first and second sheet) and checks whether they exist in this sheet
            country = countries[x]
            if row[1] == country:
                requests[x] = int(requests[x]) + int(row[3])
                accounts[x] = int(accounts[x]) + int(row[4])
                produced[x] = (int(produced[x]) + int(row[7]) + int(row[9]))
                print("updating values for ", country)
            elif row[1] in countries:
                print("exists in list, but not here")
            else:
                countries.append(row[1])
                requests.append(row[3])
                accounts.append(row[4])
                produced.append((int(row[7]) + int(row[9])))
                print("adding new values and country ", country)
            print(x)
            x += 1
            continue
        i += 1

    period = [] #creates a list that indicates period
    for i in range(len(countries)): #adds current period that list as many times as there are countries
        period.append(periods[y])

    ms_file_values = pd.DataFrame([period,countries,requests,produced,accounts]).transpose() #creates a dataframe with all values from the current excel file (all sheets)
    ms_file_values.columns = ["Period", "Country", "Requests", "Produced", "Accounts"] #sets column names
    all_ms_reports.append(ms_file_values) #adds the dataframe with all current file values to a list (simplifies procedures later)

    y+=1

#Merging separate tables into one
periods = ["Jan - Jun 2019","Jul - Dec 2019","Jan - Jun 2020","Jul - Dec 2020"]
countries_in_ms = list(set(itertools.chain(all_ms_reports[0]["Country"], all_ms_reports[0]["Country"],all_ms_reports[0]["Country"],all_ms_reports[0]["Country"]))) #collects all mentioned countries
countries_in_ms.sort()

all_ms_reports = pd.concat([all_ms_reports[0],all_ms_reports[1],all_ms_reports[2],all_ms_reports[3]])

ms_data = pd.DataFrame() #creates empty dataframe to store data later
i = 0

while i < len(countries_in_ms): #loop that goes through country names and saves data that appears next to the countries
    y = 0
    current_criteria = [countries_in_ms[i],""] #determines the country name this iteration is checking for
    while y < len(periods):
        current_criteria[1] = periods[y] #determines the period this nested loop is looking for alongside the country name
        row = [current_criteria[1], current_criteria[0], 0, 0, 0] #sets a default entry (so if a country doesn't have an entry next to it for a certain date, the 0s stay)

        x = 0
        while x < len(all_ms_reports):
            test = all_ms_reports.iloc[x, :] #saves a row from the CSV
            if test[1] == current_criteria[0] and test[0] == current_criteria[1]: #checks whether row matches criteria
                row[2] = int(row[2]) + int(test[2]) #NO requests updated
                row[3] = int(row[3]) + int(test[3]) #NO provided updated
                row[4] = int(row[4]) + int(test[4])
                x += 1
            else: #if no match, the previously created default entry is not updated
                x += 1
                continue

        ms_data = pd.concat([ms_data, pd.DataFrame(row).transpose()])
        y += 1
    i += 1

ms_data.columns = ["Period", "Country", "Requests", "Produced", "Accounts"]  # changes column names

#save data as backup
ms_data.to_csv("microsoft_data.csv")
#ms_data = pd.read_csv("microsoft_data.csv").iloc[:,1:]