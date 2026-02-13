from db.connect import connect_to_db
from datetime import datetime


def addTicket(user_id):
    db = connect_to_db()
    cursor = db.cursor()
    query = "INSERT INTO tickets (title, description, niveau_urgence, date_urgence, user_id) VALUES (%s, %s, %s, %s, %s)"
    niveau_urgenceENUM = ["modéré", "élevé", "très élevé", "critique"]

    while True:
        title = input("Entrer le titre du ticket : ")
        if title == "" or len(title) < 3 or title.isdigit():
            print(
                "Le titre du ticket doit contenir au moins 3 caractères et ne pas être vide ou composé uniquement de chiffres. Veuillez réessayer."
            )
            continue
        else:
            title = title.capitalize()
            break

    while True:
        description = input(
            "Entrer la description du ticket (ou taper fait entrer pour sauter cette etape.) : "
        )
        description = description.capitalize()
        break

    while True:
        for i, niveau in enumerate(niveau_urgenceENUM, start=1):
            print(f"{i}. {niveau}")
        niveau_urgence_choice = input(
            "Choisir le niveau d'urgence du ticket (tapez le numéro correspondant) : "
        )
        if niveau_urgence_choice.isdigit() and 1 <= int(niveau_urgence_choice) <= len(
            niveau_urgenceENUM
        ):
            niveau_urgence = niveau_urgenceENUM[int(niveau_urgence_choice) - 1]
            break
        else:
            print("Choix invalide. Veuillez réessayer.")
    date_creation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    values = (title, description, niveau_urgence, date_creation, user_id)
    try:

        cursor.execute(query, values)
        db.commit()
    except Exception as e:
        print(e)
    print(
        "Ticket créé avec succès ! L'administrateur va traiter votre demande dans les plus brefs délais."
    )
