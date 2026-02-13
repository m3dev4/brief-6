from db.connect import connect_to_db

def listTickets(user_id):
    db = connect_to_db()
    cursor = db.cursor()
    query = "SELECT * from tickets WHERE user_id = %s"
    try:
        cursor.execute(query, (user_id,))
    except Exception as e:
        print(f"Erreur lors de la récupération des tickets : {e}")
        cursor.close()
        db.close()
    results = cursor.fetchall()
    
    
    if results is None:
        print("Aucun tickets enrégistré pour le moment.")
        cursor.close()
        db.close()
    
    print("Voici l'ensemble des demande que vous avez effectué: ")   
    for result in results:
        print("#################################################")
        print(f"ID: {result[0]}, Titre: {result[1]}, Description: {result[2]}, Statut: {result[3]}, Date: {result[4]}")
        