import mysql.connector 
from mysql.connector import errorcode
def get_connection():
    try:
        conn = mysql.connector.connect(host="127.0.0.1",
                                   user="rutvik2samant",
                                   password="Innsworth@164",
                                   database="rutvik2samant_prj")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("[DB] Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("[DB] Database does not exist")
        else:
            print(err)
    else:
        print("[DB] Connection Established! IP: ", conn._host)
        return conn
