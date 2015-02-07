# -*- coding: utf-8 -*-
# Database operations

import psycopg2
from unicodedata import normalize

from sql import CREATE_ATTR_TABLE


def save_to_file(result):
    ''' Save result to file, for testing..'''
    with open(result[0].split('.')[0]+'.txt', 'w') as handle:
        handle.write(repr(result[1]))


def do_sql(psycho_cursor, sql):
    '''Execute sql command for psycopg2 cursor'''
    return psycho_cursor.execute(sql)


def make_table_name(attr_str):
    '''Transforms unicode string to sql table name string.'''
    normalized = normalize('NFKD', attr_str).encode('ascii', 'ignore')
    # TODO: map(lambda word, char: str.replace(word, char, "_"), [" ","-"]) ??
    rep_funks = [lambda x: str.replace(x, " ", "_"),
                 lambda x: str.replace(x, "-", "_"),
                 lambda x: str.replace(x, "__", "_")]

    cleaned = reduce(lambda x, y: y(x), rep_funks, normalized)
    cleaned0 = cleaned if not cleaned[0] == "_" else cleaned[1:]
    return cleaned0


def init_schema(cur, schema_name):
    '''Deletes and recreates schema. For testing purposes.'''
    try:
        do_sql(cur, "DROP SCHEMA %s CASCADE" % schema_name)
        print("Dropped schema %s.") % schema_name
    except:
        print("Schema %s missing, unable to drop.") % schema_name

    res = cur.execute("create schema %s" % schema_name)
    print("Created new schema %s." % schema_name)
    return res


# TODO
def insert_record(cur, schema, result):
    '''Insert parser result to database, table for each
        attribute'''
    print "Inserting " + result[0]
    # Switch "scope" to selected schema
    do_sql(cur, "set search_path to %s" % schema)

    for record_entry in result[1]:
        table_name = make_table_name(record_entry['title'])
        do_sql(cur, CREATE_ATTR_TABLE % table_name)
        #do_sql(cur, '''INSERT INTO %s''')


    return 0


CONN_STR = "dbname='firm-db' user='dbuser' host='localhost' password='dbpass'"
schemas = ["first_pass", "second_pass"]

try:
    conn = psycopg2.connect(CONN_STR)
except:
    print("Unable to connect db.")

# Allow dropping schema in transaction
conn.set_isolation_level(0)
cur = conn.cursor()

for schema_name in schemas:
    init_schema(cur, schema_name)
