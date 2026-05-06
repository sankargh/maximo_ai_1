"""Tools for the Maximo Agentic Query."""
from dotenv import load_dotenv
from agents import function_tool
import sqlparse
from sqlparse.sql import Identifier,Where
from sqlparse.tokens import Keyword
from Schema import SCHEMA, OS_SCHEMA_DICT, SCHEMA_NAMES
from field_matcher import fix_clause, match_fields

load_dotenv(override=True)

# @function_tool
def validate_select_clause(select_clause: str, valid_columns: set) -> tuple[bool, list[str]]:
    """
    Validates a SELECT clause string against a set of valid column names.
    
    Args:
        select_clause: e.g. "id, name, email" or "*"
        valid_columns: e.g. {"id", "name", "email", "created_at"}
    
    Returns:
        (is_valid, invalid_columns)
    """
    clause = select_clause.strip()
    
    if clause == "*":
        return True, []
    
    requested = {col.strip() for col in clause.split(",")}
    invalid = [col for col in requested if col not in valid_columns]
    
    return len(invalid) == 0, invalid

"-- Format Json to a Field: Value text --"

def format_json_as_text(json_input):
    # If the input is already a dict, iterate; if string, parse first
    if isinstance(json_input, dict):
        data = json_input
    else:
        import json
        data = json.loads(json_input)
    
    # Create the "Field: Value" format
    return "\n".join([f"{key.title()} : {value}" for key, value in data.items()])


# ============================================================
# TOOL 1 — SELECT CLAUSE EXTRACTOR
# ============================================================

@function_tool
def extract_select_clause(sql: str) -> str:
    """
    Extract SELECT clause.
    """
    parsed = sqlparse.parse(sql)
    statement = parsed[0]
    select_clause = ""
    for token in statement.tokens:
        if "SELECT" in str(token):
        # if token.ttype is Keyword and token.value.upper() == "SELECT":            
            continue
        elif "FROM" in str(token):
        # elif token.ttype is Keyword and token.value.upper() == "FROM":            
            break
        else:
            select_clause += str(token)
    return select_clause.strip()

    
# ============================================================
# TOOL 2 — WHERE CLAUSE EXTRACTOR
# ============================================================

@function_tool
def extract_where_clause(sql: str) -> str:
    """
    Extract WHERE clause.
    """
    parsed = sqlparse.parse(sql)
    statement = parsed[0]

    for token in statement.tokens:
        if isinstance(token, Where):
            return str(token)[5:].strip()
    
    return "No Where Clause"

def get_schema_name(sql: str) -> str:
    """"Extract schema name from SQL query."""
    parsed = sqlparse.parse(sql)
    statement = parsed[0]
    table_name = None
    from_seen = False
    for token in statement.tokens:
        """ Detect FROM keyword"""
        if token.ttype is Keyword and token.value.upper() == "FROM":
            from_seen = True
            continue
        """ First identifier after FROM is the main table """
        if from_seen:
            if isinstance(token, Identifier):
                table_name = token.get_real_name()
                break
    return table_name if table_name else "Unknown Schema"

# @function_tool
def fix_where_clause(where_clause: str) -> tuple[str, str]:
    """"Fix the Where clause for OSLC parameter"""
    fixed_where=where_clause.replace(" = ","=")
    fixed_where=fixed_where.replace("\'","\"")
    if fixed_where.endswith(";"):
        fixed_where=fixed_where[:-1]
    print("WHERE -> ", fixed_where)
    return fixed_where

def get_oslc_parameters(data_dict: dict) -> tuple[str, str]:

    """"Fix the SQL clauses and Extract the Schema Name for the given values of SQL Query and Clauses."""

    sql_query=data_dict["sql_query"]
    select_clause=data_dict["select_clause"]
    where_clause=data_dict["where_clause"]
    print("SQL Query - "+str(sql_query))
    " -- Extract Schema Name from SQL Query -- "
    schema_name=get_schema_name(sql_query)  
    print("Extracted Schema Name - "+str(schema_name))
    
    " -- Find the matching Schema Name for the extracted schema name -- "
    matched_schemas = match_fields(SCHEMA_NAMES, [schema_name])
    schema_name=str(matched_schemas[0])
    print("Matched Schema Name - "+str(schema_name))

    "-- Get the corresponding OS name for the matched schema name -- "
    os_name=OS_SCHEMA_DICT[schema_name]
    print("OS Name - "+str(os_name))

    " -- Get the corresponding schema for the matched schema name -- "
    query_schema = SCHEMA[schema_name]
    
    " -- Fix column names in Select and Where clauses -- "
    fixed_select = fix_clause(select_clause, query_schema)
    fixed_where  = fix_clause(where_clause, query_schema)
    fixed_where=fixed_where.replace(" = ","=")
    # "-- Replace single quotes with double quotes in where clause--  "
    fixed_where=fixed_where.replace("\'","\"")
    if fixed_where.endswith(";"):
        fixed_where=fixed_where[:-1]
    print("SELECT -> ", fixed_select)
    print("WHERE -> ", fixed_where)
    
    return os_name,fixed_where,fixed_select

@function_tool
def get_schema(schema_name:str):
    return SCHEMA[schema_name]