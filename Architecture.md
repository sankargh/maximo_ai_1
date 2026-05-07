Based on the code files provided, here's the program flow:

## Program Flow: Maximo Agentic Query Processor

### **Entry Point: Gradio UI (chat_with_options.py)**

1. **User Interface Layer**
   - User selects an object type (Asset, Locations, Workorder, or General) via Radio button
   - User enters a natural language question in the text input
   - User clicks "Submit" button

2. **Route Handler (gradio_handler)**
   - Checks if selected option is "General"
   - **If "General":** Routes to `run_generic_agent()`
   - **If specific object:** Routes to `run_sql_agent()` with schema_name and os_name

### **For Data Queries (run_sql_agent path)**

3. **SQL Agent Execution**
   - Receives: user_query, os_name (e.g., "MXASSET"), schema_name (e.g., "Asset")
   - Creates payload with question and schema_name
   - Invokes SQL Agent with triage handoff capability

4. **Agent Processing (SQL_Query_Agent)**
   - **Step 1:** Calls `get_schema(schema_name)` tool to retrieve schema from Schema.py
   - **Step 2:** Generates SQL query based on user question and retrieved schema
   - **Step 3:** Calls `extract_select_clause()` tool to extract SELECT clause from SQL
   - **Step 4:** Calls `extract_where_clause()` tool to extract WHERE clause from SQL
   - **Step 5:** Returns `sql_result` object with sql_query, select_clause, where_clause

5. **Clause Processing & Validation (tools.py)**
   - Extracts where_clause and select_clause from sql_result
   - Calls `fix_where_clause()` to normalize WHERE clause:
     - Removes spaces around "="
     - Replaces single quotes with double quotes
     - Removes trailing semicolons

6. **Maximo API Query**
   - Calls `maximo_api.query_maximo(os_name, where_clause, select_clause)`
   - Submits OSLC-compliant query to Maximo instance
   - Returns structured data

7. **Result Formatting & Response**
   - Calls `format_json_as_text(maximo_data)` to convert JSON to "Field: Value" format
   - Returns formatted response to Gradio UI
   - Displays result in output textbox

### **For General Queries (run_generic_agent path)**

3. **Generic Agent Execution**
   - User query routed to Generic Agent (no schema involved)
   - Agent responds to user's generic questions about Maximo
   - If data retrieval is requested, directs user to use appropriate object option

### **Key Components:**

| Component | Purpose |
|-----------|---------|
| **chat_with_options.py** | Main UI with object selection and routing logic |
| **chat_with_text.py** | Text-based UI interface for direct natural language queries |
| **tools.py** | Tool functions for SQL extraction and clause fixing |
| **Schema.py** | Database schema definitions and OS mappings |
| **maximo_api.py** | External API calls to Maximo instance |
| **agents.py** | OpenAI Agent framework (external dependency) |

### **Data Flow Summary:**

```
User Input (UI)
    ↓
Route Decision (General vs. Specific Object)
    ↓
SQL Agent (if specific object)
    ├─ Get Schema
    ├─ Generate SQL
    ├─ Extract SELECT/WHERE
    └─ Return sql_result
    ↓
Fix Clauses (normalize format)
    ↓
Query Maximo API
    ↓
Format Results
    ↓
Display to User
```
