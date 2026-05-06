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
    ↓
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

## Key Features
- Natural language to SQL conversion
- Schema-aware column validation
- Automatic column name correction
- OSLC-compliant query execution
- IBM Maximo integration

## Requirements
- **Python 3.9+**
- Active Maximo instance with OSLC API enabled
- OpenAI API key (`OPENAI_API_KEY`)
- Maximo credentials and connection details

## Limitations
- ⚠️ **Read-Only Queries** - Supports SELECT operations only; no INSERT, UPDATE, or DELETE
- ⚠️ **Schema Registry Dependency** - Only tables defined in the schema registry are queryable
- ⚠️ **Language Support** - Optimized for English-language queries
- ⚠️ **Complex Joins** - Limited support for multi-table joins with complex conditions
- ⚠️ **Rate Limiting** - Subject to OpenAI API rate limits

---
