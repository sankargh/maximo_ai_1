
"""This module defines the schema for the Maximo database, including table names and their corresponding columns. 
It serves as a reference for validating SQL queries and ensuring that they conform to the expected structure of the Maximo database.
The schema is represented as a dictionary where each key is a table name and the value is a set of column names associated with that table.
Example usage:
    from Schema import SCHEMA
"""


SCHEMA_NAMES = {"Asset", "Locations" ,"Workorder"}

User_Options = sorted(SCHEMA_NAMES)
User_Options.append("General")

print(str(User_Options))

OS_LIST = {"MXASSET", "MXLOCATIONS","MXAPIWODETAIL"}

OS_SCHEMA_DICT = {"Asset": "MXASSET", "Locations": "MXLOCATIONS","Workorder":"MXAPIWODETAIL"}
SCHEMA_OS_DICT = {'MXASSET': 'Asset', 'MXLOCATIONS': 'Locations', 'MXAPIWODETAIL': 'Workorder'}

SCHEMA = {
    "Asset": {
        "Assetnum",
        "Description",
        "AssetType",
        "Status",
        "Location",
        "SiteID",
        "ChangeDate",
    },
    "Locations": {
        (
        "Location",
        "Description",
        "Status",
        "SiteID",
        )
   
   
    },
    "Workorder":{
        "WONum","Description","Worktype","Status","Changedate",
        "Reportdate","WOPriority"
    }
}

# asset_columns = {
#         "Assetnum",
#         "Description",
#         "AssetType",
#         "Status",
#         "Location",
#         "SiteID",
#         "ChangeDate"
#         }
