# -*- coding: utf-8 -*-
""" Database operations. """

import logging
import psycopg2
from unicodedata import normalize

from sql import CREATE_ATTR_TABLE

CONN_STR = "dbname='firm-db' user='dbuser' host='localhost' password='dbpass'"
SCHEMAS = ["first_pass", "second_pass"]

logger = logging.getLogger(__name__)


def save_to_file(result):
    ''' Save result to file, for testing..'''
    with open(result[0].split('.')[0]+'.txt', 'w') as handle:
        handle.write(repr(result[1]))


def do_sql(psycho_cursor, sql):
    '''Execute sql command for psycopg2 cursor'''
    return psycho_cursor.execute(sql)


def make_table_name(attr_u_str):
    '''Transforms unicode string to sql table name string.'''
    normalized = normalize('NFKD', attr_u_str).encode('ascii', 'ignore')
    cleaned = reduce(lambda s, r: s.replace(r, "_"), [" ", "-", "__"],
                     normalized)
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
    filename = result[0]
    print "Inserting " + filename
    # Switch "scope" to selected schema
    do_sql(cur, "set search_path to %s" % schema)

    for record_entry in result[1]:
        table_name = make_table_name(record_entry['title'])
        do_sql(cur, CREATE_ATTR_TABLE % table_name)

        content = normalize('NFKD',
                            record_entry['content']).encode('ascii', 'ignore')

        # TODO Proper firm_id, validations, ...
        res = do_sql(cur, '''INSERT INTO %s (firm_id, date, content)
                             VALUES ('%s', '%s', '%s')''' %
                     (table_name, 1, record_entry['date'], content))

    return res


def connect():
    """ Connects to database and returns database cursor.
        Returns None if connection to database fails. """
    cur = None
    try:
        conn = psycopg2.connect(CONN_STR)

        # Allow dropping schema in transaction
        conn.set_isolation_level(0)
        cur = conn.cursor()

        for schema_name in SCHEMAS:
            init_schema(cur, schema_name)
    except psycopg2.OperationalError:
        logger.error("Unable to connect db.")
    return cur
