
"""This module defines the schema for the Maximo database, including table names and their corresponding columns. 
It serves as a reference for validating SQL queries and ensuring that they conform to the expected structure of the Maximo database.
The schema is represented as a dictionary where each key is a table name and the value is a set of column names associated with that table.
Example usage:
    from Schema import SCHEMA
"""


SCHEMA_NAMES = {"Asset", "Locations"}

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
        "Location",
        "Description",
        "Status",
        "SiteID",
    }
}

asset_columns = {
        "Assetnum",
        "Description",
        "AssetType",
        "Status",
        "Location",
        "SiteID",
        "ChangeDate"
        }
