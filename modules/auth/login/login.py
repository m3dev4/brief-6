from db.connect import connect_to_db
import bcrypt
from modules.menu.admin.admin import adminMenu
from modules.menu.user.userMenu import userMenu
from utils.sessions import save_session

def login():
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "SELECT id, name_user, email, password FROM users WHERE email = %s"
    getRole = "SELECT role FROM users WHERE email = %s"
    email_exist = True

    if email_exist:
        cursor.execute("SELECT email FROM users")
        emails = [email[0] for email in cursor.fetchall()]

        while True:
            email = input("Entrer votre adresse email : ").strip().lower()
            if email == "" or "@" not in email:
                print("Email invalide. Veuillez réessayer.")
                continue
            elif email not in emails:
                print("Email non trouvé. Veuillez réessayer.")
                continue
            break
        while True:
            password = input("Entrer votre mot de passe : ").strip()
            if password == "":
                print("Mot de passe invalide. Veuillez réessayer.")
                continue
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user is None:
                print("Email non trouvé. Veuillez réessayer.")
                continue

            user_id, name_user, email, stored_password = user
            
            print(user)

            stored_password = user[3].encode("utf-8")
            if bcrypt.checkpw(password.encode("utf-8"), stored_password):
                save_session(user_id, name_user, email)
                print("Connexion réussie !")
                cursor.execute(getRole, (email,))
                role = cursor.fetchone()[0]
                cursor.close()
                conn.close()
                if role == "admin":
                    adminMenu()
                else:
                    userMenu()
                break
            else:
                print("Mot de passe incorrect. Veuillez réessayer.")
                continue
