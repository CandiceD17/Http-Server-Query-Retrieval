# Rules for Query Retrieval

1. you need to create an API server providing HTTP service (denoted as *S*). Server *S* should handle the query for information from a table. Please implement the servers satisfying the following requirements. You can choose one of the following language for your implementation: C#, Java, Python, JavaScript (node), C/C++. The result of this task should be **a ZIP archive** containing all related files, as well as **a document** covering some design considerations and lessons-learnt during the implementation. 

2. 1. The information table contains several columns with free-text contents, as illustrated below:

| C1            | C2                 | C3      |
| ------------- | ------------------ | ------- |
| Sample Text 1 | Another “Sample”   | Value 1 |
| Sample Text 2 | Another “Sample” 2 | Value 2 |

1. The column name only be characters or digits (A-Z, a-z, 0-9, case sensitive). But there are no constraint to the value of data.
2. It is stored in a CSV file (with column header) when the server starts and won’t be updated when the server is running;

1. The query is similar to a Boolean expression targeting to a data row:

2. 1. It supports 4 operators: “==” equal, “!=” not equal, “$=” equal (case insensitive), “&=” contain (the query term is a substring of the data cell);

   2. Each predicate P is defined on a column (C1, C2, or C3) or all columns (*), with an query term (a string wrapped in “"”). For example: “* &= "123" ” yields true when the value of any column in a row contains “123”. 

   3. A query may contains several predicates which concatenated with “and” or “or”. For example, the following are valid queries:

   4. 1. C1 == "A" or C2 &= "B"
      2. C1 == "Test" and * $= "Prod" and * != "Hidden"

   5. For the any unspecified aspects, you can define them accordingly (for example, how to handle the possible “"” in side of the query term);

3. The result is the set of data rows that the query matches. The format of the data should be CSV with column headers;

4. If the query is malformed, the server should reject query processing and try to point out the issue within the query. The error message should be helpful to the user for efficient query correction.

5. The program should provide an API accessable from localhost, with port #9527. The query url should have the form "[127.0.0.1:9527/?query=](http://127.0.0.1:9527/?query=)<query string>", where <query string> is the query condition follows the format defined above.