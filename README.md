# OpenAI Agent – Maximo Data Query Processor

This is an **OpenAI Agent** that converts natural-language questions into **Maximo OSLC API** queries and returns structured results.

## How It Works
```
User Query
    ↓
Intent Check (Validate query intent)
    ↓
SQL Generation (Schema-Aware analysis)
    ↓
Extract SELECT / WHERE clauses
    ���
Fix Column Names (Validate against schema)
    ↓
Maximo OSLC API Call
    ↓
Parse & Return Results
```

**Process Details:**
1. **Intent Check** - Validates that the query is a valid data retrieval request
2. **SQL Generation** - Creates SQL based on schema understanding
3. **Column Validation** - Maps user-referenced columns to actual Maximo table columns
4. **API Execution** - Submits OSLC-compliant query to Maximo
5. **Result Parsing** - Structures and returns data to the user

## Requirements
- **Python 3.9+**
- **uv** (Python package manager)
- Active Maximo instance with OSLC API enabled
- OpenAI API key (`OPENAI_API_KEY`)
- Maximo credentials and connection details

## Setup

1. **Create `.env` file** with the following variables:
```
MAXIMO_HOST=<your_maximo_host_name>
MAXIMO_URL=<your_maximo_url>
MAXIMO_API_KEY=<your_maximo_api_key>
OPENAI_API_KEY=<your_openai_api_key>
```

## Quick Start

### Sync Dependencies
```bash
uv sync
```

### Run with Chat Interface (Dropdown Options)
```bash
uv run chat_with_options.py
```

### Run with Chat Interface (Text Input)
```bash
uv run chat_with_text.py
```

## Limitations
- **Read-Only Queries** - Supports SELECT operations only; no INSERT, UPDATE, or DELETE
- **Schema Registry Dependency** - Only tables defined in the schema registry are queryable
- **Complex Joins** - Limited support for multi-table joins with complex conditions

---
