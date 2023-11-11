# Author: Mayank Arora
# Institution: Algonquin College, Ottawa

# The program takes an indeed URL, scraps job location, and feeds it to the geolocation 
# API to get lattitude and longitude. THe job location and the coordinates are then 
# used to find the OC Transpo bus routes near the job through the OC Transpo API.


# import requests for making fetch requests and beautiful soup to 
# parse data from the location div 

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import json

#indeed job url whose location would be parsed
url = 'https://ca.indeed.com/viewjob?jk=a7302b662309a60a&tk=1he3tht2fj3vg800&from=hp&advn=5363784814176646&adid=421619153&ad=-6NYlbfkN0BYPexibh28lm8WNlvKz86rpk7bvftiND5B3KeZyq7b79IVij62gqvV4YWCtcZMODhoz_sLRrHyI2Ed3vnUA3Erfr4pVOovBuElv49s1QxGkwxNKsfRz2I42faUie5fIYw3OgZhqTGPPJaqbxXQl2gazVTt0IhvvxtGGkTdt0zBZvNc-LGSPAB-ajh4j-nIMyR1k9_Ac4tmNssq2qs_IidqQeCIAhW1sJFmaRsVgzwXU7-d526W0RCXvxL2WhM4_dVww4FES6bd99Goig2Gd8OZesVCKtirTYze6blKLVWenM2qvr2B09P6hdXvdQvtNal8C3V569bSKp5pAfMP4Nj0hjyCJ_WJjAzoiidGKQkwUhAdcUnYR4qp2RwmTWui-vlchvtQaImj1--SIIsaRCnwq4e7TyuZQhHZjcVvfA2dEMcgXq8sra4dk4ob6lQPoR2pwTftsaHvt9r_q_lmoJ_jl8KeRqTzFFv3SwO8SwoDetoADbmjED-r1XA-488IWhvtXIjlzFKQGhHP8sTetPZq&pub=4a1b367933fd867b19b072952f68dceb&xkcb=SoB_-_M3IDzIdUxyiJ0KbzkdCdPP&xpse=SoDS6_I3IDzd0rwY4h0JbzkdCdPP&vjs=3'


#make a request to the url
driver = webdriver.Chrome()
driver.get(url=url)

#get the page source through selenium
data = driver.page_source

#feed the page source into beautfil soup 

soup = BeautifulSoup(data,'html.parser')

#get the job location 
jobLocation = soup.find('div', {'data-testid': 'job-location'}).text


# splits the job location into an array delimited at space
jobLocationArray = jobLocation.split()

#api KEY for tom tom to make gelocation request
tomtomAPIKey=''

# API request for the given location
apiRequest = f"https://api.tomtom.com/search/2/geocode/\"{jobLocation}\".json?key={tomtomAPIKey}"

# Getting the result of the geolocation API request and convertin it to JSON
result = requests.get(apiRequest).json()

# Latitude of the location
latitude = result['results'][0]['position']['lat']

# Longitude of the location
longitude = result['results'][0]['position']['lon']

print(f'lattitude is {latitude} longitude is {longitude}')

#OC Transpo API Key
OCTranspoAPIKey=''

# Make a request to OC transpo to get data about all the stations
stationDetails = requests.get(f"https://api.octranspo1.com/v2.0/Gtfs?appID=8b4e6ddf&apiKey={OCTranspoAPIKey}&table=stops&id=&column=&value=&order_by=&direction=&limit=&format=json").json()

#Get the stop details from stopsArray
stopsArray=stationDetails['Gtfs']

#Defining a large number as maxLatitude as difference between the two latitudes can never be 1000
maxLatitude = 1000 

#stopCode to be used for making further requests
stopCode=""

#Iterates the stopsArray to find the closest stop to our latitude and gets its stop code
for stops in stopsArray:
    if jobLocationArray[1].lower() in stops["stop_name"].lower():
        latitudeDistance = latitude-float(stops["stop_lat"])
        if(latitudeDistance<maxLatitude):
            maxLatitude=latitudeDistance
            stopCode=stops["stop_code"]

#Coverts stopCode to int for making API requests
int(stopCode)

#API request URL to get the bus routes available at the specific stop
busRoutesURL = f"https://api.octranspo1.com/v2.0/GetRouteSummaryForStop?appID=8b4e6ddf&apiKey={OCTranspoAPIKey}&stopNo={stopCode}&format=json"

#Make API request to get the routes available
routes = requests.get(busRoutesURL).json()

#Prints the bus routes and direction
for route in routes["GetRouteSummaryForStopResult"]["Routes"]["Route"]:
    print(f'You can take {route["RouteNo"]} towards {route["RouteHeading"]} to reach your job location')

