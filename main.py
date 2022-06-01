import datetime
import json
import eml_parser
import os
import sqlite3 as sl

# EML Parser object
ep = eml_parser.EmlParser()

# Connect to the local database
con = sl.connect('emlSync.db')

# Create database transfer table if not existing
# #TODO Check if database structure is up to date
with con:
    con.execute("""
        CREATE TABLE IF NOT EXISTS emlTransfers (
            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            datetime TIMESTAMP NOT NULL ,
            full_path TEXT NOT NULL,
            subject TEXT NOT NULL,
            email_datetime TEXT NOT NULL,
            status INTEGER
        );
    """)

# Get all the eml files from the directory
emlFiles = []
for root, dirs, files in os.walk(r"/Users/julien/pythonProject/emlSync"):
    for file in files:
        if file.endswith(".eml"):
            emlFiles.append(os.path.join(root, file))

print(str(len(emlFiles)) + " emails found in the directory")




for emlFile in emlFiles:
    with open(emlFile, 'rb') as fhdl:
        raw_email = fhdl.read()
    parsed_eml = ep.decode_email_bytes(raw_email)
    print(parsed_eml['header']['subject'])
    print(parsed_eml['header']['date'])
    print(" ")



