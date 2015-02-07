# Some SQL

# TODO create proper data types for validation
# TODO Table for company data
CREATE_COMPANY_TABLE = '''
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

# Create table for attribute
# TODO date formatting
CREATE_ATTR_TABLE = '''
CREATE TABLE IF NOT EXISTS %s (
id           serial,
firm_id      integer NOT NULL,
date         text NOT NULL,
content      text NOT NULL
)
'''
