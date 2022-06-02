import datetime
import json
import time

import eml_parser
import os
import sqlite3 as sl
from sqlite3 import Error

# EML Parser object
ep = eml_parser.EmlParser()


# Create database transfer table if not existing
# TODO Check if database structure is up to date
def create_connection(db_file):
    connection = None
    try:
        connection = sl.connect(db_file)
    except Error as e:
        print(e)

    return connection


def create_tables(connection):
    with connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS emlTransfers (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                datetime TIMESTAMP NOT NULL ,
                full_path TEXT NOT NULL UNIQUE,
                subject TEXT NOT NULL,
                email_datetime TEXT NOT NULL,
                status INTEGER
            );
        """)


def add_eml_to_database(conn, eml):
    sql = ''' INSERT INTO emlTransfers (datetime, full_path, subject, email_datetime, status)
              VALUES(?, ?, ?, ?, ?) '''
    cur = conn.cursor()
    cur.execute(sql, eml)
    conn.commit()

    return cur.lastrowid


# Connect to the local database
db_connection = create_connection('emlSync.db')
create_tables(db_connection)


# Get all the eml files from the directory
emlFiles = []
for root, dirs, files in os.walk(r"/Users/julien/pythonProject/emlSync"): #TODO Move all configuration to YAML file
    for file in files:
        if file.endswith(".eml"):
            emlFiles.append(os.path.join(root, file))

print(str(len(emlFiles)) + " emails found in the directory")


# import eml files to the database
for emlFile in emlFiles:
    with open(emlFile, 'rb') as fhdl:
        raw_email = fhdl.read()
    parsed_eml = ep.decode_email_bytes(raw_email)

    eml_data = (
        datetime.datetime.now(),
        emlFile,
        parsed_eml['header']['subject'],
        parsed_eml['header']['date'],
        0
    )

    print(eml_data)

    try:
        add_eml_to_database(db_connection, eml_data)
    except Error as e:
        print(e)




