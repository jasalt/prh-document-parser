# -*- coding: utf-8 -*-
""" Database operations. """

import logging
import psycopg2
from unicodedata import normalize
from random import randint

from sql import CREATE_ATTR_TABLE, CREATE_COMPANY_TABLE

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


# TODO clean up and fix this
def make_table_name(attr_u_str):
    '''Transforms unicode string to sql table name string.'''
    try:
        normalized = normalize('NFKD', attr_u_str)
        cleaned = reduce(lambda s, r: s.replace(r, "_"), [" ", "-", "__"],
                         normalized)  # Replace with underscore
        cleaned0 = cleaned if not cleaned[0] == "_" else cleaned[1:]
        return ''.join([i for i in cleaned0 if not i.isdigit()])  # rm
    # digits
    except:
        print "Unable to make_table_name from " + attr_u_str
        return "ILL_NAME" + str(randint(10000, 99999))


def init_schema(cur, schema_name):
    '''Deletes and recreates schema. For testing purposes.'''
    try:
        do_sql(cur, "DROP SCHEMA %s CASCADE" % schema_name)
        print("Dropped schema %s.") % schema_name
    except:
        print("Schema %s missing, unable to drop.") % schema_name

    do_sql(cur, "create schema %s" % schema_name)
    print("Created new schema %s." % schema_name)

    do_sql(cur, CREATE_COMPANY_TABLE)
    print("Initialized companies table")


# TODO Validations
def insert_record(cur, schema, parser_result):
    '''Insert parser result to database, table for each
        attribute'''
    filename = parser_result[0]
    result = parser_result[1]

    print "Inserting " + filename


    firm_id = result['firmID']

    do_sql(cur, '''INSERT INTO companies (name, firm_id, form)
                   VALUES ('%s', '%s', '%s')''' %
           (result['firmName'], firm_id, result['firmForm']))

    for record_entry in result['log']:
        table_name = make_table_name(record_entry['title'])
        do_sql(cur, CREATE_ATTR_TABLE % table_name)

        content = normalize('NFKD',
                            record_entry['content']).encode('ascii', 'ignore')

        # TODO handle bad characters properly ' ...
        try:
            do_sql(cur, '''INSERT INTO %s (firm_id, date, content)
            VALUES ('%s', '%s', '%s')''' %
                   (table_name, firm_id, record_entry['date'],
                    content.encode('ascii', 'ignore')))
        except:
            print "Can't insert record_entry " + str(record_entry)


def connect():
    """ Connects to database and returns database cursor.
        Returns None if connection to database fails. """
    cur = None
    try:
        conn = psycopg2.connect(CONN_STR)
        conn.set_client_encoding('UTF8')

        # Allow dropping schema in transaction
        conn.set_isolation_level(0)
        cur = conn.cursor()

        for schema_name in SCHEMAS:
            init_schema(cur, schema_name)
        
        do_sql(cur, "set search_path to %s" % SCHEMAS[0])
        print("Set search path to schema %s." % SCHEMAS[0])

    except psycopg2.OperationalError:
        logger.error("Unable to connect db.")
    return cur
