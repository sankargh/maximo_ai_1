import requests
import json
import os
from dotenv import load_dotenv

load_dotenv(override=True)

MAXIMO_HOST= os.getenv("MAXIMO_HOST")
MAXIMO_API_KEY = os.getenv("MAXIMO_API_KEY")

payload = {}
headers = {
  'apikey': MAXIMO_API_KEY
}

MAXIMO_WHOAMI_URL = f"{MAXIMO_HOST}/maximo/api/whoami?lean=1" 

def getUserInfo():
  response = requests.request("GET", MAXIMO_WHOAMI_URL, headers=headers, data=payload)
  data=json.loads(response.text)
  return data

# userInfo = getUserInfo()
# print("\n ** User Details ** ")
# for key,value in userInfo.items():
#   print(f"{key} : {value}")

getProfileScript = "GET_PROFILE"

def getProfile(mboName):
    MAXIMO_PROFILE_URL = f"{MAXIMO_HOST}/maximo/api/script/{getProfileScript}?lean=1&mboname={mboName}"
    response = requests.request("POST", MAXIMO_PROFILE_URL, headers=headers, data=payload)
    data=json.loads(response.text)
    return data

# mboName = "WORKORDER"
# userProfile = getProfile(mboName)

# print("\n ** User Profile ** ")
# for key,value in userProfile.items():
#   print(f"{key} : {value}")