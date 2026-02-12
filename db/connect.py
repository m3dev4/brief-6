from mysql.connector import connect, Error
import os
from dotenv import load_dotenv

load_dotenv()

db_name = os.getenv("DATABASE_NAME")
db_password = os.getenv("SECRET_PASSWORD")


def connect_to_db():
    try:
        conn = connect(
            host="localhost", user="root", password=db_password, database=db_name
        )
        if conn.is_connected():
            print("Connexion réussie à la base de données")
        return conn

    except Error as e:
        print(f"Erreur lors de la connexion à la base de données : {e}")
