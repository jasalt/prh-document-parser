import psycopg2

DB_CONN_STR = "dbname='firm-db' user='dbuser' host='localhost' password='dbpass'"

try:
    conn = psycopg2.connect(DB_CONN_STR)
except:
    print("Unable to connect db.")

conn.set_isolation_level(0)
cur = conn.cursor()

schema = "first_pass"
try:
    cur.execute("DROP SCHEMA %s CASCADE" % schema)
    print("Dropped schema %s.") % schema
except:
    print("Schema %s missing, unable to drop.") % schema


cur.execute("create schema %s" % schema)
print("Created new schema %s." % schema)
