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

## 5) Fonctionnalités : détail complet

### 5.1 Démarrage & navigation globale (`main.py`)

#### Fichier : `main.py`

- **Fonction** : `menu()`
  - appelle `mainAuth()`

- **Bloc** :
  - `if __name__ == "__main__": menu()`

#### Résultat

Quand tu lances le script, l’utilisateur arrive **directement** sur le menu d’auth.

---

### 5.2 Menu d’authentification (`modules/auth/mainAuth.py`)

#### Fonction : `mainAuth()`

Affiche :

- `1` : inscription
- `2` : connexion
- `3` : quitter

Puis, selon le choix :

- `register()` si `"1"`
- `login()` si `"2"`
- `exit()` si `"3"`
- sinon affiche `Choix invalide...`

**Remarque importante** : le menu ne reboucle pas sur un mauvais choix (il affiche juste le message).

---

### 5.3 Inscription (`modules/auth/register/register.py`)

#### Fonction : `register()`

##### Étape 1 : Connexion DB

- utilise `connect_to_db()`
- crée un `cursor`

##### Étape 2 : Saisie et validation `name_user`

Boucle jusqu’à obtenir un nom valide :

- refuse si :
  - vide (après `strip`)
  - longueur `< 3`
  - composé uniquement de chiffres (`isdigit()`)
- sinon :
  - applique `capitalize()`

##### Étape 3 : Saisie et validation `email`

Boucle jusqu’à obtenir un email valide :

- refuse si :
  - vide
  - ne contient pas `@`
  - ne contient pas `.`
- sinon :
  - met en minuscules `lower()`

##### Étape 4 : Saisie et validation `password`

Boucle jusqu’à obtenir un mot de passe valide :

- hachage bcrypt :
  - `salt = bcrypt.gensalt()`
  - `hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)`
- refuse si :
  - longueur `< 12`
  - uniquement chiffres (`isdigit()`) ou uniquement lettres (`isalpha()`)

##### Étape 5 : Insertion DB

Requête :

```sql
INSERT INTO users (name_user, email, password) VALUES (%s, %s, %s)
```

Valeurs :

- `name_user`
- `email`
- `hashed_password.decode("utf-8")`

Puis :

- `conn.commit()`
- affiche un message de succès
- appelle directement `login()`

**Point clé** : le `role` n’est pas fourni à l’insertion.

---

### 5.4 Connexion (`modules/auth/login/login.py`)

#### Fonction : `login()`

##### Étape 1 : Connexion DB

- `connect_to_db()`
- `cursor = conn.cursor()`

##### Étape 2 : Récupération de tous les emails

- `cursor.execute("SELECT email FROM users")`
- liste `emails = [email[0] for email in cursor.fetchall()]`

##### Étape 3 : Saisie/validation email

Boucle :

- email normalisé avec `strip().lower()`
- refuse si vide / pas de `@`
- refuse si email non présent en base (pas dans `emails`)

##### Étape 4 : Saisie/validation password + vérification bcrypt

- récupère l’utilisateur :

```sql
SELECT id, name_user, email, password, role FROM users WHERE email = %s
```

- vérifie le mot de passe :
  - `bcrypt.checkpw(password.encode("utf-8"), stored_password)`

##### Étape 5 : Session + redirection

Si correct :

- `save_session(user_id, name_user, email, role)`
- récupère à nouveau le rôle avec :

```sql
SELECT role FROM users WHERE email = %s
```

- si rôle `admin` => `adminMenu()`
- sinon => `userMenu()`

Sinon : message “Mot de passe incorrect”.

**Détail important** : le code affiche `print(user)` (tuple DB), ce qui peut exposer le hash en console.

---

### 5.5 Gestion de session (`utils/sessions.py`)

La session est un **fichier JSON local** : `session.json`.

- **`save_session(user_id, name_user, email, role)`**
  - écrit `{user_id, name_user, email, role}` dans `session.json`

- **`load_session()`**
  - lit `session.json` si existant et retourne un dict

- **`clear_session()`**
  - supprime `session.json`

**Remarque** : les menus “Déconnexion” ne suppriment pas forcément `session.json` (pas d’appel systématique à `clear_session()`).

---

### 5.6 Menu utilisateur (`modules/menu/user/userMenu.py`)

#### Fonction : `userMenu()`

- charge la session (`load_session`)
- récupère l’utilisateur en base via son `user_id`
- boucle de menu :
  - `1` : créer un ticket => `addTicket(current_user_id)`
  - `2` : voir mes tickets => `listTickets(current_user_id)`
  - `3` : déconnexion => `break`

---

### 5.7 Création de ticket (`modules/tickets/user/add/addTicket.py`)

#### Fonction : `addTicket(user_id)`

- valide `title` (min 3 caractères, pas uniquement chiffres)
- lit `description` (optionnelle, pas de validation forte)
- impose un `niveau_urgence` parmi :
  - `modéré`, `élevé`, `très élevé`, `critique`
- met une date `datetime.now()` dans `date_urgence`
- insère le ticket :

```sql
INSERT INTO tickets (title, description, niveau_urgence, date_urgence, user_id)
```

---

### 5.8 Liste des tickets utilisateur (`modules/tickets/user/list/listDemand.py`)

#### Fonction : `listTickets(user_id)`

- récupère les tickets du user :

```sql
SELECT * from tickets WHERE user_id = %s
```

- affiche chaque ticket avec des index de colonnes (suppose un ordre précis).

---

### 5.9 Menu admin (`modules/menu/admin/admin.py`)

#### Fonction : `adminMenu()`

- lit la session, vérifie `role == "admin"`
- menu :
  - `1` : valider un ticket => `validate_ticket()`
  - `2` : afficher tous les tickets => `list_all_tickets(userGetId)`
  - `3` : afficher les utilisateurs => **non implémenté** (`pass`)
  - `4` : déconnexion => `break`

---

### 5.10 Validation / traitement tickets (admin) (`modules/tickets/admin/validation/validateTicket.py`)

#### Fonction : `validate_ticket()`

- liste les tickets en attente :
  - jointure `tickets` + `users`
  - filtre : `t.statut = 'en-attente'`
- demande l’id du ticket à mettre à jour
- propose le nouveau statut :
  - `en-cours`
  - `résolu`
- applique l’update :

```sql
UPDATE tickets SET statut = %s WHERE id = %s
```

---

### 5.11 Liste de tous les tickets (admin) (`modules/tickets/admin/listAllTickets/allTickets.py`)

#### Fonction : `list_all_tickets(user_id)`

- re-vérifie le rôle admin via DB :

```sql
SELECT role FROM users WHERE id = %s
```

- si admin :

```sql
SELECT * FROM tickets
```

- affiche tous les tickets.

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
