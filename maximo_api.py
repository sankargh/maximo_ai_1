import requests
import json
import os
from dotenv import load_dotenv
from get_profile import getProfile
from Schema import  SCHEMA, SCHEMA_OS_DICT
from field_matcher import fix_clause
from tools import format_where_clause

load_dotenv(override=True)

MAXIMO_URL= os.getenv("MAXIMO_URL")
MAXIMO_API_KEY = os.getenv("MAXIMO_API_KEY")

os_name="MXASSET"
where_clause=os_name+"?"
where_clause="status=\"OPERATING\" and location.status=\"OPERATING\" and assetnum=\"10001\""
oslc_select="&oslc.select=assetnum,description,assettype,status,changedate&lean=1"
url = MAXIMO_URL+"/"+os_name+"?"+"oslc.where="+where_clause+oslc_select

payload = {}
headers = {
  'apikey': MAXIMO_API_KEY
}

def query_maximo(os_name,where_clause,select_clause):
  mboName=SCHEMA_OS_DICT[os_name]
  profileData = getProfile(mboName)
  siteWhereClause = " and siteid in ("+str(profileData["siteWhereClause"])+")"
  where_clause = format_where_clause(where_clause+siteWhereClause)
  print("Where Clause appended with Sites : "+where_clause)
  url = MAXIMO_URL+"/"+os_name+"?"+"oslc.where="+where_clause+"&oslc.select="+select_clause+"&lean=1"
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
  query_maximo(os_name,where_clause,select_clause)