import psycopg2

CONN_STR = "dbname='firm-db' user='dbuser' host='localhost' password='dbpass'"

# TODO create proper data types for validation
CREATE_SQL = '''
CREATE TABLE companies (
id           serial,
name         text,
business_id  text,
reg_date     date,
form         text,
location     text,
entries_from date,
entries_to   date,
contact_info text,
mail_address text,
loc_address  text,
telephone    text,
fax          text,
email        text,
homepage     text
)
'''
schema = "first_pass"


class DbHelper:
    """ Handle database connection """
    cur = None

    def __init__(self):
        try:
            conn = psycopg2.connect(CONN_STR)
        except:
            print("Unable to connect db.")

        conn.set_isolation_level(0)
        cur = conn.cursor()

        try:
            cur.execute("DROP SCHEMA %s CASCADE" % schema)
            print("Dropped schema %s.") % schema
        except:
            print("Schema %s missing, unable to drop.") % schema

        cur.execute("create schema %s" % schema)
        print("Created new schema %s." % schema)
        cur.execute("setattr search_path to %s" % schema)

        cur.execute(CREATE_SQL)
        print("Created table company")

    def insert(tablename, firm_id, content, date):
        '''Insert parser result to database, each attribute it's own table'''
        return 0

    def make_table_name(attr_str):
        ''' Transform string into a sql table name'''
        return 0

    def save_to_file(result):
        ''' Save result to file '''
        with open(result[0].split('.')[0]+'.txt', 'w') as handle:
            handle.write(repr(result[1]))
