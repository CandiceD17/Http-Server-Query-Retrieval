import re
from io import StringIO

from flask import Flask, request, Response, redirect
import pandas as pd


app = Flask(__name__)


def is_valid_query(q):
    '''
    A query is valid if it is strictly consisted of the following three entries:
    [(A-Z, a-z, 0-9)+ or *] [==, !=, $=, &=] ["..."]
    Queries can be concat with 'and' & 'or'. The 'and' 'or' operators are executed in sequential order.
    Entries and operators must be separated by at least one single space. i.e. {C1=="a"} is not acceptable.
    Additional white spaces are allowed between entries.
    For the "" inside the query, the query term is the content wrapped by the first and last occurance of "".
    In the processing of query term, any sequence of consecutive spaces is reduced to a single space for clarity. 
    (since consecutive spaces usually do not convey any semantic meanings in phrases)

    Output: 
    a message indicating the validity of query ("valid" or error message), 
    a list of valid queries (each query is represented by a 3-element list), 
    a list of and/or operators
    '''
    entries = q.split()
    valid_q = [] # a 3-element list consist of 3 valid entries
    queries = [] # list of valid_q
    operators = [] # operators between queries
    operand = ['==', '!=', '$=', '&='] # valid operand

    # check the valid status of three entries defined above
    valid_first = False
    valid_second = False
    valid_third = False

    i = 0
    while(i < len(entries)):
        if not valid_first:
            column = re.findall('[A-Za-z0-9]+|\*', entries[i])
            # if valid, must be exactly one match
            # i.e. "abc*123" will give three matches and is invalid
            if len(column) != 1 or column[0] != entries[i]:
                return "Invalid column name", queries, operators
            else:
                valid_q.append(entries[i])
                valid_first = True

        elif not valid_second:
            if entries[i] not in operand:
                return "Invalid operator, must be ==, !=, $=, &=", queries, operators
            else:
                # store as int if only numbers
                valid_q.append(entries[i])
                valid_second = True

        elif not valid_third:
            if entries[i][0] != '\"':
                return "Invalid query term, must begin with \"", queries, operators
            else: # traverse the list to find the last " before the next query
                term = ""
                # find the string before next query
                if entries[i:].count('and') > 0:
                    end = entries[i:].index('and') + i
                    term = " ".join(entries[i:end])
                elif entries[i:].count('or') > 0:
                    end = entries[i:].index('or') + i
                    term = " ".join(entries[i:end])
                else:
                    end = len(entries)
                    term = " ".join(entries[i:])
                # test the validity of term
                if term[-1] != '\"':
                    return "Invalid query term, must end with \"", queries, operators
                else:
                    i = end
                    valid_q.append(term[1:-1]) # remove the front and end "" when storing
                    valid_third = True
                    continue
                
        else:
            if i == len(queries) - 1:
                return "Extra term after queries", queries, operators
            if entries[i] == 'and' or entries[i] == 'or':
                queries.append(valid_q)
                operators.append(entries[i])
                valid_q = []
                valid_first = valid_second = valid_third = False
            else:
                return "Invalid and/or operand between queries", queries, operators
        i += 1
    
    # append the last valid query and check incomplete query
    if valid_first and valid_second and valid_third:
        queries.append(valid_q)
    else:
        return "Missing entries in queries", queries, operators
    
    return "valid", queries, operators


def match_query(queries, operators, df):
    '''
    This function matches the queries associated with the operators to df.
    Output: 
    a message indicating the validity of query matching ('valid' or error message)
    matched rows in df
    '''
    columns = df.columns.tolist()
    res_df = pd.DataFrame(columns = columns) # empty df to append matching rows

    for i,q in enumerate(queries):
        # if this is the first query or the operator connecting pervious query is 'or', check the entire df
        if i - 1 < 0 or operators[i - 1] == 'or':
            cur_df = df.astype(str) # convert the content of df to string for comparison
        elif operators[i - 1] == 'and':
            cur_df = res_df 
                
            # select rows from df
        if q[0] == "*":
            select_df = pd.DataFrame(columns = columns) # empty df to append matching rows
            for (col, _) in cur_df.iteritems():
                if q[1] == "==":
                    select_df = select_df.append(cur_df[cur_df[col] == q[2]])
                elif q[1] == "!=":
                    drop_df = cur_df[cur_df[col] == q[2]]
                    select_df = select_df.append(cur_df.drop(index=drop_df.index.tolist()))
                elif q[1] == "$=":
                    select_df = select_df.append(cur_df[cur_df[col].str.lower().isin([q[2].lower()])])
                elif q[1] == "&=":
                    select_df = select_df.append(cur_df[cur_df[col].str.contains(q[2], case=True)])
            cur_df = select_df.drop_duplicates(keep='first')
        else:
            if q[0] not in columns:
                return 'No corresponding column name in data', res_df
            elif q[0] not in cur_df.columns:
                cur_df = pd.DataFrame(columns = columns) # no matching column, set the cur_df to empty
            else:
                if q[1] == "==":
                    cur_df = cur_df[cur_df[q[0]] == q[2]]
                elif q[1] == "!=":
                    drop_df = cur_df[cur_df[q[0]] == q[2]]
                    cur_df = cur_df.drop(index=drop_df.index.tolist())
                elif q[1] == "$=":
                    cur_df = cur_df[cur_df[q[0]].str.lower().isin([q[2].lower()])]
                elif q[1] == "&=":
                    cur_df = cur_df[cur_df[q[0]].str.contains(q[2], case=True)]

        # update res_df according to 'and' 'or' operators
        if i - 1 < 0 or operators[i - 1] == 'or':
            res_df = res_df.append(cur_df)
            res_df.drop_duplicates(keep='first',inplace=True)
        elif operators[i - 1] == 'and':
            res_df = cur_df 
    
    if res_df.empty:
        return 'No corresponding items for the query', res_df
    return 'valid', res_df


@app.route('/')
def get_info():
    args = request.args
    query = args['query']

    # '&' will separate the query to two items, append it back
    for key, val in args.items():
        if key == 'query':
            continue
        if key == '':
            query += '&=' + val
        else:
            query += '&' + key
    print(query)

    # Query error checking and parsing
    mes, queries, operators = is_valid_query(query)
    if mes != "valid":
        return mes
    print(queries)
    print(operators)
    
    # Query match
    df = pd.read_csv('data.csv')
    mes, res_df = match_query(queries, operators, df)
    if mes != "valid":
        return mes
    
    res_df.to_csv('res.csv')

    return '''
        <html><body>
        The query has been successfully processed. 
        To download the extracted results in a csv file, <a href="/getCSV">click me.</a>
        </body></html>
        '''


@app.route("/getCSV")
def getCSV():
    output = StringIO()
    df = pd.read_csv('res.csv')
    df.to_csv(output)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-disposition":"attachment; filename=res.csv"})


if __name__ == '__main__':
   app.run(host='127.0.0.1', port=9527)

