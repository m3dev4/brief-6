from db.connect import connect_to_db



def list_all_tickets(user_id):
    db = connect_to_db()
    cursor = db.cursor()
    query = "SELECT role FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))
    result = cursor.fetchone()

    if result and result[0] == "admin":
        cursor.execute("SELECT * FROM tickets")
        tickets = cursor.fetchall()

        if tickets:
            print("\n--- Liste de tous les tickets ---")
            for ticket in tickets:
                print(
                    f"ID: {ticket[0]}, Titre: {ticket[1]}, Description: {ticket[2]}, Statut: {ticket[4]}, Date de création: {ticket[5]}"
                )
        else:
            print("Aucun ticket trouvé.")
    else:
        print("Accès refusé. Vous devez être administrateur pour voir cette page.")
        return

    cursor.close()
    db.close()
