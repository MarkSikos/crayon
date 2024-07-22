import sqlite3, traceback, os
from Modell.UtilityModules.PasswordHandler import PasswordHandler
from Modell.UtilityModules.Exceptions import DatabaseException

class Initializer():
    """ 
    Az adatbázis nem létezése esetén (első futtatáskor), az adatbázis inicializálásáért felelős osztály.
    """
    
    def create_database(self):
        """ Az adatbázis inicializálásáért felelős függvény"""
        os.makedirs('Persistence', exist_ok=True)
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash BLOB NOT NULL,
                role TEXT NOT NULL
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
                subject_id INTEGER PRIMARY KEY,
                subject_name TEXT NOT NULL
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS note (
                user_id INTEGER NOT NULL,
                note_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                note_name TEXT NOT NULL,
                picture TEXT NOT NULL,
                image_id INTEGER NOT NULL,
                PRIMARY KEY (note_id, image_id, user_id),
                FOREIGN KEY(subject_id) REFERENCES subjects(subject_id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS tests (
                test_id INTEGER PRIMARY KEY,
                test_name TEXT NOT NULL, 
                test_date DATE
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_data (
                user_id INTEGER NOT NULL,
                test_data_id INTEGER PRIMARY KEY AUTOINCREMENT,
                test_id INTEGER NOT NULL,
                question TEXT,
                answer TEXT,
                picture TEXT NOT NULL,
                image_id INTEGER NOT NULL,
                FOREIGN KEY(test_id) REFERENCES tests(test_id),
                FOREIGN KEY(user_id) REFERENCES users(id)   
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS homeworks (
                homework_id INTEGER PRIMARY KEY,
                homework_name TEXT NOT NULL, 
                homework_date DATE
                
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS homework_data (
                user_id INTEGER NOT NULL,
                homework_data_id INTEGER PRIMARY KEY AUTOINCREMENT,
                homework_id INTEGER NOT NULL,
                question TEXT,
                answer TEXT,
                picture TEXT NOT NULL,
                image_id INTEGER NOT NULL,
                FOREIGN KEY(homework_id) REFERENCES homeworks(homework_id),
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS results (
                result_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                test_name TEXT NOT NULL,
                exercise_id INTEGER NOT NULL,
                score INTEGER NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
            """)
            
            conn.commit()
            self.add_admin()
            
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
        
    def add_admin(self):
        """ Az első adminisztrátor hozzáadásáért felelős függvény."""
        try:
            conn = sqlite3.connect("Persistence/database.db")
            cursor = conn.cursor()
            
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", ("Admin", PasswordHandler.hash_password("Admin"), "Admin"))
            conn.commit()
            
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()

 
