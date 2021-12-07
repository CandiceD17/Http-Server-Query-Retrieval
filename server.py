from flask import Flask, request
import csv
import pandas as pd


app = Flask(__name__)

@app.route('/')
def get_info():
    args = request.args
    query = args['query']

    # &= will separate the query to two parts
    for key, val in args.items():
        if key == 'query':
            continue
        if key == '':
            query += '&=' + val
        else:
            return 'Invalid Input'
    
    print(query)
    and_queries = query.split('and')
    and_queries = [q.strip() for q in and_queries]
    print(and_queries)
    or_queries = query.split('or')
    or_queries = [q.strip() for q in or_queries]
    print(or_queries)

    df = pd.read_csv('data.csv')
    columns = df.columns.ravel()
    print(df)
    if len(and_queries) > 1:
        for q in and_queries:
            eq = q.split('==')
            neq = q.split('!=')
            seq = q.split('$=')
            ceq = q.split('&=')
            if len(eq) > 1:
                key = str(eq[0])
                val = eq[1].strip('"')
                if key == '*':
                    for c in columns:
                        df = df[df[c] == val]
                else:
                    df = df[df[key] == val]

            elif len(neq) > 1:
                pass

            elif len(seq) > 1:
                pass

            elif len(ceq) > 1:
                pass
        return df.to_string()

    elif len(or_queries) > 1:
        pass
    else:
        pass

    return "hello world"


if __name__ == '__main__':
   app.run(host='127.0.0.1', port=9527)