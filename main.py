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


def select_next_task(conn):
    sql = ''' SELECT * FROM emlTransfers 
              WHERE status=0
              LIMIT 0,1; '''
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    return cur.fetchone()




# Connect to the local database
db_connection = create_connection('emlSync.db')
create_tables(db_connection)


# Get all the eml files from the directory
emlFiles = []
for root, dirs, files in os.walk(r"/Users/julien/Downloads/email_proton_2021-11-24"): #TODO Move all configuration to YAML file
    for file in files:
        if file.endswith(".eml"):
            emlFiles.append(os.path.join(root, file))

print(str(len(emlFiles)) + " emails found in the directory")


# import eml files to the database
db_imported = 0
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

    try:
        add_eml_to_database(db_connection, eml_data)
        db_imported = db_imported + 1
    except Error as e:
        pass

print(str(db_imported) + " new eml files imported to the database")

while True:
    eml_data = select_next_task(db_connection)

    upload_eml_to_imap_server()

print(eml_data)



