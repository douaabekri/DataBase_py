import sqlite3
import csv
import os
import random
import string
import re

class DatBase:
    @staticmethod
    def generate_safe_password(length=8):
        if length < 8:
            length = 8  # Longueur minimale
        all_characters = string.ascii_letters + string.digits + string.punctuation
        password = [
            random.choice(string.ascii_uppercase),  # Au moins une majuscule
            random.choice(string.digits),          # Au moins un chiffre
            random.choice(string.punctuation)      # Au moins un symbole
        ]
        password += random.choices(all_characters, k=length - len(password))
        random.shuffle(password)  # Mélanger les caractères
        return ''.join(password)

    @staticmethod
    def is_safe_password(password):
        if len(password) < 8:
            return False
        if not any(char.isdigit() for char in password):
            return False
        if not any(char.isupper() for char in password):
            return False
        if not any(char in string.punctuation for char in password):
            return False
        return True

    @staticmethod
    def is_valid_email(email):
        regex = r"[a-zA-Z][a-zA-Z0-9_.\-]*@[a-zA-Z]+\.[a-zA-Z]+"
        return bool(re.match(regex, email))

    @staticmethod
    def process_data():
        db_file = "user_data.db"
        if not os.path.exists(db_file):
            print("Aucune base de données trouvée.")
            return

        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()

        # Vérifier et corriger les mots de passe non sécurisés
        cursor.execute("SELECT username, password FROM users")
        users = cursor.fetchall()
        for username, password in users:
            if not DatBase.is_safe_password(password):
                safe_password = DatBase.generate_safe_password()
                cursor.execute("UPDATE users SET password = ? WHERE username = ?", (safe_password, username))
                print(f"Mot de passe mis à jour pour {username}")

        connection.commit()

        # Exporter les données dans différents fichiers CSV
        categories = {
            "usernames_passwords.csv": ["username", "password"],
            "usernames_emails.csv": ["username", "email"],
            "usernames_ages.csv": ["username", "age"],
            "usernames_occupations.csv": ["username", "occupation"]
        }

        for file_name, columns in categories.items():
            query = f"SELECT {', '.join(columns)} FROM users"
            cursor.execute(query)
            rows = cursor.fetchall()

            with open(file_name, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(columns)
                writer.writerows(rows)
            print(f"Données exportées vers {file_name}")

        connection.close()

    @staticmethod
    def ajouter_utilisateur():
        username = input("Entrez le nom d'utilisateur: ")
        password = input("Entrez le mot de passe: ")
        while not DatBase.is_safe_password(password):
            print("Le mot de passe n'est pas sûr. Il doit avoir au moins 8 caractères, un chiffre, une majuscule et un symbole.")
            password = input("Entrez un mot de passe sûr: ")
        email = input("Entrez l'adresse email: ")
        while not DatBase.is_valid_email(email):
            print("L'email n'est pas valide. Veuillez réessayer.")
            email = input("Entrez une adresse email valide: ")
        age = int(input("Entrez l'âge: "))
        occupation = input("Entrez la profession: ")

        user_data = {"username": username, "password": password, "age": age, "email": email, "occupation": occupation}
        db_file = "user_data.db"
        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            occupation TEXT NOT NULL
        )
        ''')
        connection.commit()

        cursor.execute('''
        INSERT OR REPLACE INTO users (username, password, age, email, occupation)
        VALUES (:username, :password, :age, :email, :occupation)
        ''', user_data)
        connection.commit()

        connection.close()
        print("Utilisateur ajouté avec succès.")

    @staticmethod
    def afficher_utilisateurs():
        db_file = "user_data.db"
        if not os.path.exists(db_file):
            print("Aucune base de données trouvée.")
            return

        connection = sqlite3.connect(db_file)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()

        if rows:
            print("\nListe des utilisateurs:")
            print("-" * 80)
            print(f"{'Nom d\'utilisateur':<20}{'Mot de passe':<20}{'Âge':<10}{'Email':<30}{'Profession':<20}")
            print("-" * 80)
            for row in rows:
                print(f"{row[0]:<20}{row[1]:<20}{row[2]:<10}{row[3]:<30}{row[4]:<20}")
            print("-" * 80)
        else:
            print("Aucun utilisateur enregistré.")

        connection.close()