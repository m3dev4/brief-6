# brief-6

## 1) Présentation générale

Ce projet est une application **CLI (console)** en Python qui permet :

- **Aux utilisateurs** :
  - de **s’inscrire**
  - de **se connecter**
  - de **créer un ticket** (demande)
  - de **consulter leurs tickets**

- **Aux administrateurs** :
  - de **voir tous les tickets**
  - de **valider / traiter les tickets** (changer leur statut)

L’application s’appuie sur :

- **MySQL** (stockage des utilisateurs et tickets)
- **bcrypt** (hachage et vérification des mots de passe)
- **dotenv** (chargement des variables d’environnement)
- Une **session locale** stockée dans un fichier `session.json` (persistée sur disque)

---

## 2) Structure du projet (dossiers & fichiers)

Racine :

- **`main.py`**
  - point d’entrée de l’application (lance le menu d’authentification)

- **`.env`** (présent mais gitignoré)
  - contient les secrets/paramètres DB utilisés par `db/connect.py`

- **`session.json`**
  - fichier de session (créé/écrasé lors d’une connexion réussie)

Dossiers :

- **`db/connect.py`**
  - connexion à MySQL via variables d’environnement

- **`utils/sessions.py`**
  - gestion de session : `save_session`, `load_session`, `clear_session`

- **`modules/auth/`**
  - `mainAuth.py` : menu principal (inscription/connexion/quitter)
  - `register/register.py` : inscription
  - `login/login.py` : connexion

- **`modules/menu/`**
  - `admin/admin.py` : menu admin (validation, liste tickets, etc.)
  - `user/userMenu.py` : menu utilisateur (créer ticket, voir ses tickets)

- **`modules/tickets/`**
  - `user/add/addTicket.py` : création de ticket
  - `user/list/listDemand.py` : affichage des tickets de l’utilisateur
  - `admin/validation/validateTicket.py` : validation / changement de statut
  - `admin/listAllTickets/allTickets.py` : listing de tous les tickets (admin)

---

## 3) Installation & exécution

### 3.1 Prérequis

- **Python** installé (version récente recommandée)
- **MySQL** installé et accessible en local
- Un utilisateur MySQL `root` (car `connect.py` utilise `user="root"`)

### 3.2 Variables d’environnement (fichier `.env`)

Le fichier `db/connect.py` charge `.env` et lit :

- **`DATABASE_NAME`** : nom de la base MySQL
- **`SECRET_PASSWORD`** : mot de passe MySQL (pour `root`)

Le code fixe également :

- **host** = `localhost`
- **user** = `root`

Donc ton `.env` doit contenir **au minimum** :

- `DATABASE_NAME=...`
- `SECRET_PASSWORD=...`

### 3.3 Lancement

Le point d’entrée est `main.py`. Il exécute `menu()`, qui appelle `mainAuth()`.

---

## 4) Base de données : ce que le code attend

Ce projet suppose l’existence d’au moins **2 tables** :

### 4.1 Table `users`

Le code lit/écrit les colonnes suivantes :

- `id` (utilisé partout comme identifiant)
- `name_user`
- `email`
- `password` (haché bcrypt, stocké en texte via `decode("utf-8")`)
- `role` (utilisé pour distinguer `admin` vs utilisateur normal)

#### Usage exact dans le code

- Inscription : `INSERT INTO users (name_user, email, password)`
  - donc `role` doit avoir :
    - soit une **valeur par défaut** en base
    - soit accepter `NULL` (sinon l’insert échouera)

- Connexion : `SELECT id, name_user, email, password, role FROM users WHERE email = %s`

- Vérification rôle admin :
  - `SELECT role FROM users WHERE email = %s`
  - `SELECT role FROM users WHERE id = %s`

### 4.2 Table `tickets`

Le code lit/écrit les champs suivants (d’après les requêtes + index utilisés dans les affichages) :

- `id`
- `title`
- `description`
- `niveau_urgence`
- `date_urgence` (dans le code c’est en réalité la date de création : `datetime.now()`)
- `user_id` (clé étrangère logique vers `users.id`)
- `statut` (utilisé pour filtrer, afficher, et mettre à jour)

#### Usage exact dans le code

- Création ticket :
  - `INSERT INTO tickets (title, description, niveau_urgence, date_urgence, user_id)`
  - donc `statut` doit avoir :
    - une **valeur par défaut** en base (probablement `en-attente`)
    - sinon accepter `NULL` (sinon l’insert échouera)

- Tickets “à valider” (admin) :
  - `WHERE t.statut = 'en-attente'`

- Mise à jour statut :
  - `UPDATE tickets SET statut = %s WHERE id = %s`
  - valeurs possibles via menu admin :
    - `en-cours`
    - `résolu`

---

## 5) Fonctionnalités (explication détaillée du code)

Cette section explique **le comportement réel** du programme en suivant le code fichier par fichier.

---

### 5.1 Point d’entrée : `main.py`

#### Rôle du fichier

`main.py` est le **point de départ** du programme.

#### Décomposition du code

- **Import**
  - `from modules.auth.mainAuth import mainAuth`
  - But : récupérer la fonction `mainAuth()` qui gère l’écran principal (inscription/connexion).

- **Fonction `menu()`**
  - appelle `mainAuth()` sans paramètre
  - c’est une simple fonction “wrapper” pour démarrer l’application.

- **Bloc `if __name__ == "__main__":`**
  - garantit que `menu()` est exécutée uniquement si on lance `main.py` directement.

Flux : `main.py` -> `menu()` -> `mainAuth()`.

---

### 5.2 Connexion à la base de données : `db/connect.py`

#### Rôle du fichier

Centraliser la création d’une connexion MySQL via `mysql.connector`.

#### Décomposition du code

- **Imports**
  - `from mysql.connector import connect, Error`
    - `connect` : permet d’ouvrir une connexion MySQL
    - `Error` : type d’erreur spécifique MySQL utilisé dans le `except`
  - `import os` : lire les variables d’environnement
  - `from dotenv import load_dotenv` : charger le fichier `.env`.

- **`load_dotenv()`**
  - charge le fichier `.env` de la racine (si présent) dans les variables d’environnement du processus.

- **Lecture des variables**
  - `db_name = os.getenv("DATABASE_NAME")`
  - `db_password = os.getenv("SECRET_PASSWORD")`
  - ces 2 valeurs sont utilisées pour configurer l’accès à MySQL.

- **Fonction `connect_to_db()`**
  - `try:`
    - appelle `connect(host="localhost", user="root", password=db_password, database=db_name)`
    - si `conn.is_connected()` est vrai, affiche “Connexion réussie…”
    - retourne l’objet connexion `conn`
  - `except Error as e:`
    - affiche un message “Erreur lors de la connexion…”
    - (dans ce cas la fonction ne retourne rien explicitement, donc `None`)


---

### 5.3 Menu d’accueil (auth) : `modules/auth/mainAuth.py`

#### Rôle du fichier

Afficher le menu initial et router vers :

- inscription (`register()`)
- connexion (`login()`)
- quitter

#### Décomposition du code

- **Imports**
  - `register` depuis `modules.auth.register.register`
  - `login` depuis `modules.auth.login.login`

- **Fonction `mainAuth()`**
  - affiche un message de bienvenue.
  - demande un `choice` avec `input(...)`.
  - utilise `match choice:`
    - `case "1"` : affiche “Inscription”, puis appelle `register()`
    - `case "2"` : affiche “Connexion”, puis appelle `login()`
    - `case "3"` : affiche “Au revoir !”, puis `exit()` (arrête le programme)
    - `case _` : affiche “Choix invalide…”



---

### 5.4 Inscription : `modules/auth/register/register.py`

#### Rôle du fichier

Créer un nouvel utilisateur dans la table `users` et stocker son mot de passe sous forme **hachée** (bcrypt).

#### Décomposition du code

- **Imports**
  - `connect_to_db` : ouvrir une connexion DB
  - `bcrypt` : hachage du mot de passe
  - `login` : appelé à la fin pour enchaîner sur la connexion

- **Fonction `register()`**

##### (A) Connexion DB et préparation de la requête

- `conn = connect_to_db()`
- `cursor = conn.cursor()`
  - `cursor` sert à exécuter les requêtes SQL.
- `query = "INSERT INTO users (name_user, email, password) VALUES (%s, %s, %s)"`
  - `%s` = placeholders (paramètres) pour éviter de concaténer des chaînes.

##### (B) Saisie `name_user` + validations

- boucle `while True:`
  - lit `name_user = input(...)`
  - `if name_user.strip() == ""` : refuse un nom vide (même si l’utilisateur tape des espaces)
  - `or len(name_user) < 3` : impose au moins 3 caractères
  - `or name_user.isdigit()` : refuse un nom composé uniquement de chiffres
  - sinon :
    - `name_user = name_user.capitalize()`
    - `break` (sort de la boucle)

##### (C) Saisie `email` + validations

- boucle `while True:`
  - lit `email = input(...)`
  - refuse si vide (`strip() == ""`)
  - refuse si pas de `@` ou pas de `.` (validation simple)
  - sinon :
    - `email = email.lower()` (normalisation)
    - `break`

##### (D) Saisie `password` + règles + hachage

- boucle `while True:`
  - lit `password = input(...)`
  - prépare le hash :
    - `pasword_hash = password.encode("utf-8")`
    - `salt = bcrypt.gensalt()`
    - `hashed_password = bcrypt.hashpw(pasword_hash, salt)`
  - refuse si `len(password) < 12`
  - refuse si `password.isdigit()` (uniquement chiffres)
  - refuse si `password.isalpha()` (uniquement lettres)
  - sinon `break`



##### (E) Insertion SQL

- `values = (name_user, email, hashed_password.decode("utf-8"))`
  - on stocke le hash en texte.
- `cursor.execute(query, values)`
- `conn.commit()` : rend l’insertion persistante.

##### (F) Enchaînement

- affiche “Inscription réussie…”
- appelle `login()` pour laisser l’utilisateur se connecter tout de suite.


---

### 5.5 Connexion : `modules/auth/login/login.py`

#### Rôle du fichier

Authentifier un utilisateur existant :

- vérifier que l’email existe
- vérifier le mot de passe (bcrypt)
- créer une session locale
- rediriger vers le menu **admin** ou **user**

#### Décomposition du code

- **Imports**
  - `connect_to_db` : DB
  - `bcrypt` : comparaison du mot de passe
  - `adminMenu` / `userMenu` : redirection après login
  - `save_session` : écrit `session.json`

- **Fonction `login()`**

##### (A) Connexion + requêtes SQL préparées

- `conn = connect_to_db()`
- `cursor = conn.cursor()`
- `query = "SELECT id, name_user, email, password, role FROM users WHERE email = %s"`
- `getRole = "SELECT role FROM users WHERE email = %s"`


##### (B) Pré-chargement des emails existants

- `cursor.execute("SELECT email FROM users")`
- `emails = [email[0] for email in cursor.fetchall()]`
  - construit une liste Python avec toutes les adresses.

##### (C) Saisie email

- boucle `while True:`
  - `email = input(...).strip().lower()`
  - refuse si vide ou sans `@`
  - refuse si `email not in emails` (email absent en DB)
  - sinon `break`

##### (D) Saisie mot de passe + vérification

- boucle `while True:`
  - lit `password = input(...).strip()`
  - refuse si vide
  - exécute `cursor.execute(query, (email,))`
  - `user = cursor.fetchone()`
    - si `None`, affiche “Email non trouvé…” (normalement déjà filtré par la liste)
  - unpack : `user_id, name_user, email, stored_password, role = user`
  - `stored_password = user[3].encode("utf-8")`
  - compare :
    - `bcrypt.checkpw(password.encode("utf-8"), stored_password)`

##### (E) Session + redirection

Si le mot de passe est correct :

- `save_session(user_id, name_user, email, role)`
- affiche “Connexion réussie !”
- relit le rôle :
  - `cursor.execute(getRole, (email,))`
  - `role = cursor.fetchone()[0]`
- ferme : `cursor.close()` puis `conn.close()`
- route :
  - si `role == "admin"` => `adminMenu()`
  - sinon => `userMenu()`

Si incorrect : message “Mot de passe incorrect…” et boucle.


---

### 5.6 Session locale : `utils/sessions.py`

#### Rôle du fichier

Simuler une “session” dans une application console en stockant l’utilisateur courant dans `session.json`.

#### Décomposition du code

- `USER_SESSION = "session.json"`
  - chemin relatif : le fichier est créé dans la racine où tu exécutes le programme.

##### `save_session(user_id, name_user, email, role)`

- construit :
  - `session_data = {"user_id": ..., "name_user": ..., "email": ..., "role": ...}`
- écrit dans le fichier :
  - `with open(USER_SESSION, "w") as session_file:`
  - `json.dump(session_data, session_file, indent=4)`

##### `load_session()`

- vérifie l’existence : `os.path.exists(USER_SESSION)`
- si existe : lit le JSON et le retourne (dict)
- en cas d’erreur : affiche et retourne `None`

##### `clear_session()`

- supprime `session.json` avec `os.remove` si existant
- sinon affiche qu’il n’y a pas de session.

---

### 5.7 Menu utilisateur : `modules/menu/user/userMenu.py`

#### Rôle du fichier

Afficher un menu après connexion pour un utilisateur “standard”.

#### Décomposition du code

- **Imports**
  - `connect_to_db` : pour récupérer le nom de l’utilisateur
  - `addTicket` : création ticket
  - `listTickets` : liste des tickets
  - `load_session` : lire `session.json`

- **Fonction `userMenu()`**

##### (A) Connexion DB + lecture session

- `db = connect_to_db()`
- `cursor = db.cursor()`
- `session = load_session()`
- si `session is None` : affiche un message et `return`

##### (B) Récupération utilisateur DB

- `current_user_id = session.get("user_id")`
- exécute :
  - `SELECT id, name_user, email FROM users WHERE id = %s`
- `result = cursor.fetchone()`
- `print(result)` (debug)
- si pas de résultat : affiche “Utilisateur non trouvé.” puis ferme

Puis :

- `name_user = result[1]`
- ferme `cursor` et `db` avant d’afficher le menu.

##### (C) Boucle menu

- affiche :
  - `1` Créer un ticket
  - `2` Voir mes tickets
  - `3` Déconnexion
- lit `choice = input(...)`
- `match choice:`
  - `case "1"`: `addTicket(current_user_id)`
  - `case "2"`: `listTickets(current_user_id)`
  - `case "3"`: affiche “Déconnexion réussie !” puis `break`
  - `_`: affiche “Choix invalide…”


---

### 5.8 Création de ticket (user) : `modules/tickets/user/add/addTicket.py`

#### Rôle du fichier

Permettre à un utilisateur connecté de créer une nouvelle ligne dans `tickets`.

#### Décomposition du code

- **Imports**
  - `connect_to_db` : DB
  - `datetime` : date de création

- **Fonction `addTicket(user_id)`**

##### (A) Connexion + requête d’insert

- ouvre DB et cursor
- prépare :
  - `INSERT INTO tickets (title, description, niveau_urgence, date_urgence, user_id) ...`

##### (B) Validation `title`

- boucle `while True:`
  - lit `title`
  - refuse si vide / < 3 / uniquement chiffres
  - sinon `capitalize()` et `break`

##### (C) Saisie `description`

- lit la description
- applique `capitalize()`
- la boucle se termine immédiatement (pas de vraie validation).

##### (D) Choix `niveau_urgence`

- tableau `niveau_urgenceENUM = ["modéré", "élevé", "très élevé", "critique"]`
- affiche les options avec `enumerate(..., start=1)`
- demande un numéro
- vérifie que c’est un chiffre et qu’il est dans la bonne plage
- convertit le numéro en valeur texte

##### (E) Date

- `date_creation = datetime.now().strftime("%Y-%m-%d %H:%M:%S")`
- cette valeur est stockée dans la colonne `date_urgence`.

##### (F) Exécution SQL

- `values = (title, description, niveau_urgence, date_creation, user_id)`
- `cursor.execute(query, values)`
- `db.commit()`
- affiche un message de succès

---

### 5.9 Liste des tickets (user) : `modules/tickets/user/list/listDemand.py`

#### Rôle du fichier

Afficher tous les tickets appartenant à l’utilisateur courant.

#### Décomposition du code

- **Imports**
  - `connect_to_db`

- **Fonction `listTickets(user_id)`**
  - ouvre DB + cursor
  - prépare `query = "SELECT * from tickets WHERE user_id = %s"`
  - exécute `cursor.execute(query, (user_id,))`
  - récupère `results = cursor.fetchall()`

Affichage :

- si `results is None` : message “Aucun tickets…”
  - (en pratique `fetchall()` renvoie souvent `[]`, donc ce test peut ne jamais être vrai)
- affiche ensuite chaque ligne avec des index :
  - `result[0]` id
  - `result[1]` titre
  - `result[2]` description
  - `result[3]` statut
  - `result[4]` date


---

### 5.10 Menu admin : `modules/menu/admin/admin.py`

#### Rôle du fichier

Donner à un admin des actions de gestion :

- valider des tickets en attente
- voir tous les tickets

#### Décomposition du code

- **Imports**
  - `connect_to_db` (importé mais non utilisé dans ce fichier)
  - `validate_ticket`
  - `load_session`
  - `list_all_tickets`

- **Fonction `adminMenu()`**
  - lit la session
  - si `None` : affiche un message (mais ne quitte pas immédiatement)
  - `userAdmin = session.get("role") == "admin"`
  - `userGetId = session.get("user_id")`

Si admin :

- boucle menu :
  - `1` -> `validate_ticket()`
  - `2` -> `list_all_tickets(userGetId)`
  - `3` -> `pass` (non implémenté)
  - `4` -> `break`

Sinon : affiche “Accès refusé”.

---

### 5.11 Validation / changement de statut (admin) : `modules/tickets/admin/validation/validateTicket.py`

#### Rôle du fichier

Permettre à un admin de traiter les tickets “en-attente” en les passant à :

- `en-cours`
- `résolu`

#### Décomposition du code

- **Fonction `validate_ticket()`**
  - ouvre DB + cursor
  - exécute une requête multi-lignes (join) :
    - sélectionne des champs ticket + infos user
    - filtre uniquement les tickets dont `statut = 'en-attente'`
  - `results = cursor.fetchall()`
  - si vide : message + fermeture + `return`
  - affiche chaque ticket (tuple complet)

Ensuite :

- demande `update_ticket` (id ticket)
- propose un choix :
  - `1` => `en-cours`
  - `2` => `résolu`
- applique :
  - `UPDATE tickets SET statut = %s WHERE id = %s`
- `db.commit()`
- fermeture cursor + db

---

### 5.12 Liste de tous les tickets (admin) : `modules/tickets/admin/listAllTickets/allTickets.py`

#### Rôle du fichier

Afficher l’ensemble des tickets, uniquement si l’utilisateur passé en paramètre est admin.

#### Décomposition du code

- **Fonction `list_all_tickets(user_id)`**
  - ouvre DB + cursor
  - vérifie le rôle dans la DB :
    - `SELECT role FROM users WHERE id = %s`
  - si admin :
    - `SELECT * FROM tickets`
    - boucle d’affichage
  - sinon : “Accès refusé…” et `return`
  - ferme cursor + db


---

## 6) Sécurité & validations implantées

- **bcrypt** pour les mots de passe (hash + check)
- mot de passe :
  - min 12 caractères
  - pas uniquement lettres
  - pas uniquement chiffres
- email : validation simple et vérification d’existence à la connexion
- rôle : champ `role`, valeur attendue : `admin`

---

## 7) Limites / comportements notables (tel que le code fonctionne actuellement)

- **Déconnexion** : `break` dans les menus, mais pas de suppression systématique de `session.json`.
- **Fermeture DB** : pas toujours faite dans le flux normal dans certains modules tickets.
- **Affichage de données** : des `print(...)` affichent des tuples DB (potentiellement sensibles).
- **Incohérence possible sur l’ordre des colonnes `tickets`** :
  - `listDemand.py` et `allTickets.py` n’utilisent pas les mêmes index pour `statut`/`date`.
- **Option admin “Afficher les utilisateurs”** : annoncée mais non implantée.
- **Menu auth** : ne reboucle pas sur saisie invalide.
