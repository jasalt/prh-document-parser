# Database operations
import psycopg2

def save_to_file(result):
    ''' Save result to file, for testing..'''
    with open(result[0].split('.')[0]+'.txt', 'w') as handle:
        handle.write(repr(result[1]))


def do_sql(psycho_cursor, sql):
    '''Execute sql command for psycopg2 cursor'''
    return psycho_cursor.execute(sql)


def make_table_name(attr_str):
    ''' Transform string into a sql table name'''
    return attr_str.replace(" ", "_").upper()


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
    do_sql(cur, "set search_path to %s" % schema)
    print "do smthn for result " + str(len(result))
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
