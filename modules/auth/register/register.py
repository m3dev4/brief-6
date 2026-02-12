from db.connect import connect_to_db
import bcrypt
from modules.auth.login.login import login


def register():
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "INSERT INTO users (name_user, email, password) VALUES (%s, %s, %s)"

    while True:
        name_user = input("Entrer votre prenom et nom : ")
        if name_user.strip() == "" or len(name_user) < 3 or name_user.isdigit():
            print(
                "Le nom d'utilisateur doit contenir au moins 3 caractères et ne pas être vide ou composé uniquement de chiffres. Veuillez réessayer."
            )
        else:
            name_user = name_user.capitalize()
            break

    while True:
        email = input("Entrer votre adresse email : ")
        if email.strip() == "" or "@" not in email or "." not in email:
            print(
                "L'adresse email doit être valide et ne pas être vide. Veuillez réessayer."
            )
        else:
            email = email.lower()
            break

    while True:
        password = input("Entrer votre mot de passe : ")
        pasword_hash = password.encode("utf-8")
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(pasword_hash, salt)

        if len(password) < 12:
            print(
                "Le mot de passe doit contenir au moins 12 caractères. Veuillez réessayer."
            )
            continue
        elif password.isdigit() or password.isalpha():
            print(
                "Le mot de passe doit contenir à la fois des lettres et des chiffres. Veuillez réessayer."
            )
            continue
        else:
            break
    values = (name_user, email, hashed_password.decode("utf-8"))
    cursor.execute(query, values)
    conn.commit()
    print("Inscription réussie ! Vous pouvez maintenant vous connecter.")
    print("######################################################")
    login()