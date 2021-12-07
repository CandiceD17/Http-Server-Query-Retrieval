# Server S for Query Retrieval
This is a **server** that extracts content from an information table (in .csv format) in your local database and outputs the matched rows to a .csv file. The rules for query matching is provided in `spec.md`.

## Environment

To build and test the server, you need at least:

- Python >= '3.7.0'
- flask >= '1.1.2'
- pandas >= '0.25.3'

## Usage

To get the server running, go to the directory containing the source code and type:

```shell
$ python3 my_server.py
```

Then, the program provides an API accessable from localhost, with port #9527. The query url should have the form "[127.0.0.1:9527/?query=](http://127.0.0.1:9527/?query=)<query string>" with the query string defined as below.

### Information Table Format

- The column name of the information table only be **characters or digits (A-Z, a-z, 0-9, case sensitive)**. But there are no constraint to the value of data.
- You should put your information table to the same directory with the source code and rename it to `data.csv` to be processed by the program.
- It should not be updated when the server is running, else the updated content will not be processed.

### Query String and Matching

**My own design is marked as bolded text.**

The query is similar to a Boolean expression targeting to a data row:

- It supports 4 operators: “==” equal, “!=” not equal, “$=” equal (case insensitive), “&=” contain (the query term is a substring of the data cell);
- Each predicate P is defined on a column (C1, C2, or C3) or all columns (\*), with an query term (a string wrapped in “"”). For example: “\* &= "123" ” yields true when the value of any column in a row contains “123”. 
- **Each element in the predicate P (column, operators, and query term) must be separated by at least one single space. i.e. {C1=="a"} is not acceptable. Additional white spaces are allowed between entries.**
- A query may contains several predicates which concatenated with “and” or “or”. **The 'and' 'or' operators are executed in sequential order.**
- **For the "" inside the query, the query term is the content wrapped by the first and last occurance of "" before the next query.**
  - In the processing of query term, **any sequence of consecutive spaces is reduced to a single space for clarity**. (since consecutive spaces usually do not convey any semantic meanings in phrases)
  - i.e. “\* &= "12      3" ” is reduced to “\* &= "12 3" ” in the program

- For example, the following are valid queries:
  - C1 == "A" or C2 &= "B"
  - C1 == "Test" and * $= "Prod" and * != "Hidden"

### Output

The result is the set of data rows that the query matches. If the query is successfully processed, you will receive a message in the localhost:

> The query has been successfully processed. To download the extracted results in a csv file, [click me.](http://127.0.0.1:9527/getCSV)

And the `click me` will direct you to downloading the processed dataset stored as `res.csv`.

If the query is malformed, the server will reject query processing and print out the corresponding error messages to your host.

## Design Concerns and Lessons Learnt

In my design, I implemented query parser and matcher separately, so the program will first check the validity of query and it in a more accessible format for query matching.

Still, there are several concerns about the edge cases:

- I define that the query term is the content wrapped by the first and last occurance of "" before the next query. To determine whether we encountered the next query, I searched for 'and' & 'or' in the following query message. If no 'and' & 'or' founded, I set the end of this query term to be the end of the entire query message. However, it is possible that there is a little typo in 'and' & 'or', i.e.

  > The query: ID == "1" ans Name == "Li" will be parsed into ['ID', '==', '"1" ans Name == "Li"']

  Then, the program cannot alert the user to change the typo and will still process this query as a valid message. This problem still needs further redesign of the parsing rules.

- For the consecutive spaces inside the query term, I reduce them into a single space for simple processing. However, these consecutive spaces may convey a special meaning, so further correction is required.

From this project, I learnt to systematically implement a server with query processing and design specific rules to ensure the clarity and solid performance of this server.

##