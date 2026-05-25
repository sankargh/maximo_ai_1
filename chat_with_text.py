import json
from openai import OpenAI
from dotenv import load_dotenv
import gradio as gr
from agents import Agent, Runner, trace, SQLiteSession
import maximo_api
import sqlparse
from sqlparse.sql import Identifier, IdentifierList, Where
from pydantic import BaseModel
from sqlparse.tokens import Keyword
from Schema import SCHEMA, SCHEMA_NAMES,OS_SCHEMA_DICT,OS_LIST
from tools import extract_select_clause,extract_where_clause, get_oslc_parameters
from tools import *

load_dotenv(override=True)

client = OpenAI()

class sql_result(BaseModel):
    sql_query: str
    select_clause: str
    where_clause: str

def extract_json(text: str) -> dict:
    start = text.find("{")
    end = text.rfind("}") + 1
    return json.loads(text[start:end])

agent_instructions = (
    "You are a SQL expert. "
    "Use the given schema to respond to the user's request. "
    "The schema is as follows: {SCHEMA} "
    "Follow the steps to generate 1) SQL Query, 2) Select Clause and 3) Where Clause. "
    "Steps to follow: "
    "1. Generate SQL query for the given question and schema. "
    "1a. Do Not make alias such as 'assettype as type or description as desc etc."    
    "2. Use the {extract_select_clause} tool to extract Select clause from the generated SQL query. "
    "3. Use the {extract_where_clause} tool to extract Where clause from the generated SQL query. "
    "4. Ensure that the generated SQL query strictly adheres to the provided schema, "
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

chat_session=SQLiteSession("Get-SQL-Query")

async def chat(message,history):    
    with trace ("SQL Query Agent"):
        result = await Runner.run(triage_agent,message,session=chat_session,max_turns=20)

        if type(result.final_output)==str:
            return result.final_output
        elif type(result.final_output)==sql_result:
            data_dict=result.final_output.model_dump()
            # print("Extracted Data Dict - "+str(type(data_dict)))
            
            "-- Get the parameters (OS name, where & select clauses) for Maximo API -- "
            oslc_parameters=get_oslc_parameters(data_dict)
            os_name,fixed_where,fixed_select=oslc_parameters
            
            "-- Query Maximo API with the parameters (OS name, where & select clauses) -- "
            maximo_data=maximo_api.query_maximo(os_name,fixed_where,fixed_select)

            if maximo_data:
                final_response=format_json_as_text(maximo_data)
                return str(final_response)
            else:
                return "No data found for the given query."
            

if __name__=="__main__":
    gr.ChatInterface(fn=chat).launch()
