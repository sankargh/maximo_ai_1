# from email import message
import json
import re
import token
# from tkinter.tix import Select
from openai import OpenAI
from dotenv import load_dotenv
import gradio as gr
from agents import Agent, Runner, trace, SQLiteSession, function_tool, handoffs
from field_matcher import fix_clause, match_fields
import maximo_api
import sqlparse
from sqlparse.sql import Identifier, IdentifierList, Where
# , IdentifierList, Identifier
from pydantic import BaseModel
from sqlparse.tokens import Keyword
from Schema import SCHEMA, SCHEMA_NAMES
# , DML

load_dotenv(override=True)

client = OpenAI()

user_question = "List the departments having more than 100 employees?"

# schema = """
#     Table: Asset (Assetnum, Description, AssetType, Status, Location,SiteID,ChangeDate)
#     Table: Locations (Location, Description, Status,SiteID)
#     """

class sql_result(BaseModel):
    sql_query: str
    select_clause: str
    where_clause: str

def extract_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])

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

agent_instructions = (
    "You are a SQL expert. "
    "Use the given schema to respond to the user's request. "
    "The schema is as follows: {SCHEMA} "
    "Follow the steps to generate 1) SQL Query, 2) Select Clause and 3) Where Clause. "
    "Steps to follow: "
    "1. Generate SQL query for the given question and schema. "
    "2. Use the {extract_select_clause} tool to extract Select clause from the generated SQL query. "
    "3. Use the {extract_where_clause} tool to extract Where clause from the generated SQL query. "
    "4. Ensure that the generated SQL query strictly adheres to the provided schema, "
    # " Use the {validate_select_clause} tool to check that all column names in the SELECT clause are valid according to the schema,"
        # " If there are any discrepancies, Generate the SQL query again ensuring that only valid column names are used. "
    "5. Finally, return the SQL query, Select clause and Where clause as {sql_result} Base Model."
)

sql_agent = Agent(
    name = "SQL_Query_Agent",
    instructions= agent_instructions,
    tools=[extract_select_clause, extract_where_clause],
    model="gpt-4o-mini",
    output_type=sql_result
)

# Triage Agent: Decides which agent to hand off to based on the user's question. I
# If the question is related to SQL or data, it will hand off to the SQL Agent. Otherwise, it will respond directly.
triage_agent = Agent(
    name="Triage",
    instructions="If the user asks for a data or SQL query, hand off to sql_agent.  \
                    Otherwise,Just chat with the user normally.",
    handoffs=[sql_agent],
    model="gpt-4o-mini"
)

def get_oslc_clauses(data_dict: dict) -> tuple[str, str]:

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
    
    return fixed_where,fixed_select


chat_session=SQLiteSession("Get-SQL-Query")

async def chat(message,history):    
    with trace ("SQL Query Agent"):
        result = await Runner.run(triage_agent,message,session=chat_session,max_turns=20)

        if type(result.final_output)==str:
            return result.final_output
        elif type(result.final_output)==sql_result:
            data_dict=result.final_output.model_dump()
            # print("Extracted Data Dict - "+str(type(data_dict)))
            
            "-- Get the fixed where clause and select clause for the Maximo API -- "
            oslc_clauses=get_oslc_clauses(data_dict)
            fixed_where,fixed_select=oslc_clauses
            
            "-- Query Maximo API with the fixed where clause and select clause -- "
            maximo_data=maximo_api.query_maximo(fixed_where,fixed_select)

            if maximo_data:
                return str(maximo_data)
            else:
                return "No data found for the given query."
            

if __name__=="__main__":
    gr.ChatInterface(fn=chat).launch()