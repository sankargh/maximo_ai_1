import json
from openai import OpenAI
from dotenv import load_dotenv
import asyncio
import gradio as gr
from agents import Agent, Runner,trace, SQLiteSession
import maximo_api
from pydantic import BaseModel
from Schema import OS_SCHEMA_DICT,User_Options
# , DML
from tools import get_schema,extract_select_clause,extract_where_clause,fix_where_clause, format_json_as_text

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

agent_instructions = (
    "You are a SQL expert. "
    "Respond to the user's request for the given schema"
    "The schema_name and questions are fetched from the user's input. "
    "Firstly, use the {get_schema} tool to get the schema"
    "For Example run get_schema('Asset')"
    "Then, Follow the steps to generate A) SQL Query, B) Select Clause and C) Where Clause. "
    "Steps to follow: "
    "1. Generate SQL query for the given question and schema "
    "2. Use the {extract_select_clause} tool to extract Select clause from the generated SQL query. "
    "3. Use the {extract_where_clause} tool to extract Where clause from the generated SQL query. "
    "4. Ensure that the generated SQL query strictly adheres to the provided schema, "
    # " Use the {validate_select_clause} tool to check that all column names in the SELECT clause are valid according to the schema,"
        # " If there are any discrepancies, Generate the SQL query again ensuring that only valid column names are used. "
    # "5. Use the {fix_where_clause} tool to fix the Where clause"
    "5. Finally, return the SQL query, Select clause and Where clause as {sql_result} Base Model."
)

tools = []
sql_agent = Agent(
    name = "SQL_Query_Agent",
    instructions= agent_instructions,
    tools=[get_schema,extract_select_clause, extract_where_clause],
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

generic_agent = Agent(
    name="Generic",
    instructions="You are a Generic agent of Maximo applicaition,   \
                Respond to user's generic questions \
                If user asks about data retrieval of Maximo, Request the user to user relevant option in chatbot   \
                Otherwise,Just chat with the user normally.",
    model="gpt-4o-mini"
)

"""
1. No need to find matching names 
2. Rename to fix_oslc_clauses and remove the finding matches part
3. Use 'fix_oslc_clauses' as tool in the sql_agent
4. Route to a General agent for 'General' option
Move the function_tools and methods to tools.py script

"""
generic_chat_session=SQLiteSession("Generic_Agent")

async def run_generic_agent(user_query,history):    
    with trace ("Generic_Agent"):
        result = await Runner.run(generic_agent,user_query,session=generic_chat_session,max_turns=20)
        if type(result.final_output)!=None:
            return result.final_output
            
# if __name__=="__main__":
#     gr.ChatInterface(fn=chat).launch()

sql_chat_session=SQLiteSession("Query_Maximo")

async def run_sql_agent(user_query,os_name,schema_name): 
    """Run the SQL Agent and return the Maximo Data."""
    with trace ("SQL_Query_Agent"):
        # instructions = "The schema is as follows: {query_schema} "+"\n"+agent_instructions_2
        # input_data = {"schema_name": schema_name}
        payload = {"question":user_query, "schema_name":schema_name}
        # input_data = [{"content":json.dumps(payload)}]
        input_data=[
        {
            "type": "message",
            "role": "user",
            "content": json.dumps(payload)
        }
        ]
        # input_data=[{"type": "param", "text": "The schema name is "+schema_name+"  "}]
        result = await Runner.run(sql_agent,session=sql_chat_session,max_turns=20,input=input_data)
        if type(result.final_output)==sql_result:
            data_dict=result.final_output.model_dump()
            # oslc_parameters=get_oslc_parameters(data_dict)
            # fixed_where,fixed_select=oslc_parameters
            where_clause = data_dict["where_clause"]
            select_clause = data_dict["select_clause"]
            where_clause=fix_where_clause(where_clause)
            maximo_data=maximo_api.query_maximo(os_name,where_clause,select_clause)
            if maximo_data:
                final_response=format_json_as_text(maximo_data)
                return str(final_response)
            else:
                return "No data found for the given query."

# -----------------------------
# Gradio Wrapper (sync → async)
# -----------------------------

def gradio_handler(selected_option, user_query):
    print("Selected Option - "+str(selected_option))
    print("User Query - "+str(user_query))
    if selected_option != "General":
        schema_name=selected_option
        os_name = OS_SCHEMA_DICT[schema_name]
        # query_schema = SCHEMA[schema_name]
        return asyncio.run(run_sql_agent(user_query,os_name,schema_name))
    else:
        return asyncio.run(run_generic_agent(user_query, []))


# -----------------------------
# Gradio UI
# -----------------------------
with gr.Blocks(title=" Maximo Agentic Query") as demo:
    gr.Markdown("## 🤖 Maximo Agentic Query")

    option_selector = gr.Radio(
        # choices=["Asset", "Locations", "General"],
        choices=User_Options,
        label="Select Object Type",
        value="Asset"
    )

    user_input = gr.Textbox(
        label="Enter your question",
        placeholder="e.g. Show all active assets in Site A"
    )

    output = gr.Textbox(
        label="Response",
        lines=6
    )

    submit = gr.Button("Submit")

    submit.click(
        fn=gradio_handler,
        inputs=[option_selector, user_input],
        outputs=output
    )

demo.launch()
