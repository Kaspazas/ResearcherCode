import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By


###############
#country codes#
###############
#Country codes are collected to be used as a guide for what countries we're looking for.
#These codes are also later used in scraping Google and Facebook data
#It could also be used to highlight any mismatch in country listings by the companies being analysed

url = "https://www.iso.org/obp/ui/#search"
driver = webdriver.Chrome() #initialize automated browser
driver.get(url) #navigates to the website

#For this specific website, some interaction is required to get to the country data, not available just via URL
options = driver.find_elements(By.CLASS_NAME, "v-radiobutton.v-select-option") #there are 7 options for search parameters (e.g., Collections, Standarts), this saves all of them to a list
options[6].click() #here, we need to click on the last button. This could be done by identifying its name, but here there's no need to overcomplicate things (given that the buttons position is known)
driver.find_element(By.CLASS_NAME, "v-button-go .v-button-caption").click() #initialize the search

#By default, the results come in pages of 25 results
driver.find_element(By.CLASS_NAME, "search-header .v-select-select").click() #click on the "results per page" menu
options = driver.find_elements(By.CLASS_NAME, "search-header .v-select-select option") #find all potential options
options[(len(options)-1)].click() #click on the last option (biggest number)

#Actually collecting data
table_data = driver.find_elements(By.CLASS_NAME, ".v-grid-cell") #fetches all entries in table

cells = [] #creates a list for processed entries
for cell in table_data:
    cell = cell.text #turns a cell from a selenium item, into a string
    cells.append(cell) #adds processed cell to a new list

names = cells[::5] #selects every 5th list entry, because that's where english country names are
codes = cells[2::5] #from the second list entry on, selects every 5th element, because that's where country iso codes are
countries = pd.DataFrame([names,codes]).transpose() #creates a table from the two lists derived above
countries.columns = countries.iloc[0] #sets column names based on first entries
countries = countries.drop(countries.index[0]) #removes the non needed first row

countries = pd.concat([countries,pd.DataFrame({"English short name":["Kosovo"], "Alpha-2 code":["XK"]})]) #adds Kosovo, because it wasn't in the list, but Google has a report for it
countries = pd.concat([countries,pd.DataFrame({"English short name":["Netherlands Antilles"], "Alpha-2 code":["AN"]})]) #adds Netherlands Antilles, because it wasn't in the original list, but is included by Facebook

i = 0
while i < len(countries):
    countries["English short name"][i] = countries["English short name"][i].replace("(the)","")
    i +=1

countries["English short name"][216] = "Taiwan" #Changes the name of "Taiwan (province of China)" to Taiwan (because that is more standart)
countries["English short name"][118] = "South Korea" #Changes the name of "Korea (republic of)" to South Korea (because that is more standart)
countries["Alpha-2 code"][152] = "NA" #Changes Alpha code of Namibia because it was saved as nan (no data)

countries.to_csv("country_list_and_codes.csv") #saves table as csv
#countries = pd.read_csv("country_list_and_codes.csv").iloc[:,1:]






