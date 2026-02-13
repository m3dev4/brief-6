from db.connect import connect_to_db
from modules.tickets.user.add.addTicket import addTicket
from modules.tickets.user.list.listDemand import listTickets
from utils.sessions import load_session

USER_SESSION = "session.json"

def userMenu():
    db = connect_to_db()
    cursor = db.cursor()
    
    session = load_session()
    
    if session is None:
        print("Aucune session active. Veuillez vous connecter.")
        return
    
    current_user_id = session.get("user_id")
    try:
        query = "SELECT id, name_user, email FROM users WHERE id = %s"
        cursor.execute(query, (current_user_id,))
        result = cursor.fetchone()
    except Exception as e:
        print(e)
    
    print(result)    
    if not result:
        print("Utilisateur non trouvé.")
        cursor.close()
        db.close()
    
    name_user = result[1]
    cursor.close()
    db.close()
    

    while True:
        print(f"\nBienvenue, {name_user} ! Que voulez-vous faire ?")
        print("######################################################")
        print("1. Créer un ticket")
        print("2. Voir mes tickets")
        print("3. Déconnexion")

        choice = input("Tapez le numéro de votre choix : ")

        match choice:
            case "1":
                addTicket(current_user_id)
            case "2":
                listTickets(current_user_id)
            case "3":
                print("Déconnexion réussie !")
                break
            case _:
                print("Choix invalide. Veuillez réessayer.")
