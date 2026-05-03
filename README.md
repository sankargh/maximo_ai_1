
This is and Openai Agent script to process user queries, thne pull results from Maximo API.

It follows the below steps:
    - Identify user question whether it is related ot data retrieval
    - Generate SQL queries for the 'User question' referencing to given schema of Maximo Tables
    - Extract the 'Select' and 'Where' clauses from query
    - Fix the column names in clauses by finding best match in data schema
    - Call the Maximo OSLC API with 'oslc.where' and 'oslc.select' paramers
    - Retrieve the result and display to user.