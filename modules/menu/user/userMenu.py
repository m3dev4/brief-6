from db.connect import connect_to_db

def userMenu():
    current_user = None
    conn = connect_to_db()
    cursor = conn.cursor()
    query = "SELECT name_user FROM users WHERE email = %s"
    cursor.execute(query, (current_user,))
    name_user = cursor.fetchone()[0]
    print(f"Bienvenue, {name_user} ! Que voulez-vous faire ?")
    print("######################################################")
    print("1. Creer un ticket")
    print("2. Voir mes tickets")
    print("3. Deconnexion")
    
    choice = input("Tapez le numéro de votre choix : ")
    match choice:
        case "1":
            print("Création de ticket")
            # Appeler la fonction de création de ticket ici
        case "2":
            print("Voir mes tickets")
            # Appeler la fonction pour voir les tickets ici
        case "3":
            print("Déconnexion")
            # Appeler la fonction pour modifier le profil ici
        case _:
            print("Choix invalide. Veuillez réessayer.")