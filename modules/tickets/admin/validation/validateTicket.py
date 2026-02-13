from db.connect import connect_to_db


def validate_ticket():
    db = connect_to_db()
    cursor = db.cursor()
    # jointure entre ticket et user
    query = """
    SELECT t.id, t.title, t.statut, t.niveau_urgence, u.name_user, 
    u.email
    FROM tickets t
    JOIN users u ON t.user_id = u.id
    WHERE t.statut = 'en-attente'
    """
    cursor.execute(query)
    results = cursor.fetchall()

    if not results:
        print("Aucun ticket en attente de validation.")
        cursor.close()
        db.close()
        return

    for result in results:
        print(result)

    update_ticket = input("Entrez l'id du ticket à valider : ")

    print("Choissisez le nouveau statut")
    print("1. En cours")
    print("2. résolu")

    while True:
        choice = input("Entrez votre choix : ")

        match choice:
            case "1":
                choice = "en-cours"
                break
            case "2":
                choice = "résolu"
                break
            case _:
                print("Choix invalide")
                continue

    query = "UPDATE tickets SET statut = %s WHERE id = %s "
    cursor.execute(query, (choice, update_ticket))
    db.commit()

    print("Ticket mis à jour avec succès !")

    cursor.close()
    db.close()
