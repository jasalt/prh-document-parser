# Some SQL

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
