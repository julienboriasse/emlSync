import datetime
import json
import time
import imaplib
import eml_parser
import os
import sqlite3 as sl
from sqlite3 import Error
from time import struct_time
import datetime
from dateutil import parser

# Configuration
IMAP_SERVER = 'imap.mail.me.com'
EMAIL_ACCOUNT = 'julien.boriasse'
PASSWORD = 'ejhn-hbgg-xwhx-brwu'
EMAIL_FOLDER = 'INBOX.ArchiveProton'

# EML Parser object
ep = eml_parser.EmlParser()


def mailbox_login(server, account, password):
    M = imaplib.IMAP4_SSL(server)
    M.login(account, password)
    return M


def update_email_status(connection, email_id, status):
    sql = ''' UPDATE emlTransfers SET status = ? WHERE id = ?;'''
    cur = connection.cursor()
    cur.execute(sql, (status, email_id))
    connection.commit()

    return cur.lastrowid


def upload_eml_to_imap_server(email):

    try:
        date = email[4]
        date_time = imaplib.Time2Internaldate(time.strptime(date, "%Y-%m-%d %H:%M:%S%z"))
        with open(email[2], 'rb') as eml:
            rv, message = M.append(EMAIL_FOLDER, None, date_time, eml.read())
    except Exception as e:
        rv = 'ERR'
        message = e

    return rv, message


M = mailbox_login(IMAP_SERVER, EMAIL_ACCOUNT, PASSWORD)

M.create(EMAIL_FOLDER)

available_folders = list(map(lambda x: x.split()[-1].decode(), M.list()[1]))
# print(available_folders)


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
                email_datetime TIMESTAMP NOT NULL,
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
for root, dirs, files in os.walk(r"test"): #TODO Move all configuration to YAML file
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

    # print(parsed_eml['header']['date'])

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

    if eml_data == None:
        break;

    rv, message = upload_eml_to_imap_server(eml_data)

    # print(eml_data)
    # print(rv)

    if rv != 'OK':
        print(message)

        print("Failed to upload " + str(eml_data[2]))
        break;
        update_email_status(db_connection, eml_data[0], 1)
    else:
        update_email_status(db_connection, eml_data[0], 2)
        print("Email " + str(eml_data[2]) + " uploaded")





