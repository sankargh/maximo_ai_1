import requests
import json
import os
from Schema import SCHEMA
from dotenv import load_dotenv

load_dotenv(override=True)

DEV_URL= os.getenv("DEV_URL")
DEV_ISR_API_KEY=os.getenv("DEV_ISR_API_KEY")

os_name="mxasset"
where_clause=os_name+"?"
where_clause="status=\"OPERATING\" and location.status=\"OPERATING\" and assetnum=\"10001\""
oslc_select="&oslc.select=assetnum,description,assettype,status,changedate&lean=1"
url = DEV_URL+"/"+os_name+"?"+"oslc.where="+where_clause+oslc_select

payload = {}
headers = {
  'apikey': DEV_ISR_API_KEY
}

def query_maximo(where_clause,select_clause):
  url = DEV_URL+"/"+os_name+"?"+"oslc.where="+where_clause+"&oslc.select="+select_clause+"&lean=1"
  response = requests.request("GET", url, headers=headers, data=payload)
  data=json.loads(response.text)
  if "member" in data and len(data["member"]) > 0:
    maximo_json=data["member"][0]
    filered_schema = select_clause.replace(" ","").split(",");
    data_columns = {key.lower() for key in filered_schema}
    print("Data Columns - "+str(data_columns))
    maximo_data = {k: v for k, v in maximo_json.items() if k.lower() in data_columns}
    print("Filtered Maximo Data - "+str(maximo_data))
    for key, value in maximo_data.items():
        print(f"{key}: {value}") 
    return maximo_data
  else:
    print("No data found for the given where clause.")
    return {}

if __name__=="__main__":
  select_clause="Assetnum, Description, AssetType, Status"
  query_maximo(where_clause,select_clause )