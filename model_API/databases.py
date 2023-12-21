## LOCAL MYSQL CONNECTOR ##

# from mysql.connector import connect, Error
#
#
# def mysql():
#     try:
#         cnx = connect(
#             host='localhost',
#             username='root',
#             password='root',
#             database='kompetisiku'
#         )
#         return cnx
#     except Error as e:
#         print("Terjadi masalah pada Database : " + str(e))
#         return None

## CLOUD SQL CONNECTOR ##

# Import the connector helper
# import pymysql
# from google.cloud.sql.connector import Connector, IPTypes
#
#
# # function to return the database connection
# def getconn() -> pymysql.connections.Connection:
#     conn: pymysql.connections.Connection = Connector.connect(
#         "psychic-linker-402714:us-central1:kompetisiku-backend",
#         "pymysql",
#         user="root",
#         password="root",
#         db="kompetisiku"
#     )
#     return conn

import os
import pymysql

db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')


def open_connection():
    unix_socket = '/cloudsql/{}'.format(db_connection_name)
    try:
        if os.environ.get('GAE_ENV') == 'standard':
            conn = pymysql.connect(user=db_user, password=db_password,
                                unix_socket=unix_socket, db=db_name,
                                cursorclass=pymysql.cursors.DictCursor
                                )
    except pymysql.MySQLError as e:
        conn = str(e)
    return conn

# def get_user():
#     conn = open_connection()
#     with conn.cursor() as cursor:
#         result = cursor.execute('SELECT * FROM users')
#         user = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
#         if result > 0:
#             got_user = user
#         else:
#             got_user = 'No Users in DB'
#     conn.close()
#     return got_user
#
# def get_compe():
#     conn = open_connection()
#     with conn.cursor() as cursor:
#         result = cursor.execute('SELECT * FROM competitions')
#         compe = [dict((cursor.description[i][0], value) for i, value in enumerate(row)) for row in cursor.fetchall()]
#         if result > 0:
#             got_compe = compe
#         else:
#             got_compe = 'No Competitions in DB'
#     conn.close()
#     return got_compe
