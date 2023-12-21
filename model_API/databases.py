from mysql.connector import connect, Error


def mysql():
    try:
        cnx = connect(
            host='localhost',
            username='root',
            password='root',
            database='kompetisiku'
        )
        return cnx
    except Error as e:
        print("Terjadi masalah pada Database : " + str(e))
        return None
