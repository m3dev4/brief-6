from db.connect import connect_to_db
from modules.tickets.admin.validation.validateTicket import validate_ticket
from utils.sessions import load_session
from modules.tickets.admin.listAllTickets.allTickets import list_all_tickets

def adminMenu():
    session = load_session()
   
    if session is None:
        print("Aucun session ouvert ! Veuillez vous connecter")
        
    userAdmin = session.get("role") == "admin"
    userGetId = session.get("user_id")
    
    if userAdmin:
        print(f"Bienvenue dans le menu administrateur, {session.get('name_user')} !") 
        while True:
            print("\n--- Menu Admin ---")
            print("1. Valider un ticket")
            print("2. Afficher tous les tickets")
            print("3. Afficher les utilisateurs")
            print("4. Déconnexion")

            choice = input("Choisissez une option : ")

            match choice:
                case "1":
                    validate_ticket()
                case "2":
                    list_all_tickets(userGetId)
                case "3":
                    # Afficher les utilisateurs
                    pass
                case "4":
                    print("Déconnexion réussie !")
                    break
                case _:
                    print("Choix invalide. Veuillez réessayer.")
    else:
        print("Accès refusé. Vous n'êtes pas administrateur.")

    