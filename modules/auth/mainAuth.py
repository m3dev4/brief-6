from modules.auth.register.register import register
from modules.auth.login.login import login


def mainAuth():
    print("Bienvenue ! Veuillez vous connecter ou s'inscrire pour continuer.")
    choice = input("Tapez \n 1 pour s'inscrire, \n 2 pour se connecter, \n 3 pour quitter \n : ")

    match choice:
        case "1":
            print("Inscription")
            register()

        case "2":
            print("Connexion")
            login()

        case "3":
            print("Au revoir !")
            exit()
        case _:
            print("Choix invalide. Veuillez réessayer.")
