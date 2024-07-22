import sqlite3
import traceback
import os
from Modell.UtilityModules.Exceptions import DatabaseException
from PyQt6.QtCore import QObject, pyqtSignal

class ExerciseManager(QObject):
    """ 
    A feladatok (tesztek és házi feladatok) háttérlogikájáért felelős osztály.
    """
    # Események
    
    successful_deletion = pyqtSignal()
    unsuccessful_deletion = pyqtSignal()
    
    # A logikáért felelős függvények.
    
    @staticmethod
    def load_into_database(user_role, user_id, table):
        """ A feladatok adatainak az adatbázisból való kinyeréséért felelős függvény."""
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            
            if user_role == 'Teacher':
                # formázás esetén előre elkészítem a stringet
                query = f"""
                    SELECT DISTINCT td.user_id, td.{table}_id,  u.username, t.{table}_name, t.{table}_date FROM {table}_data td
                    JOIN users u ON td.user_id = u.id
                    JOIN {table}s t ON td.{table}_id = t.{table}_id
                    ORDER BY t.{table}_date DESC, t.{table}_name, u.username """
                cursor.execute(query)
            else:
                query = f"""
                    SELECT DISTINCT td.{table}_id, td.user_id, t.{table}_name, t.{table}_date FROM {table}_data td
                    JOIN {table}s t ON td.{table}_id = t.{table}_id
                    WHERE td.user_id = ? ORDER BY t.{table}_date DESC, t.{table}_name
                """
                cursor.execute(query, (user_id,))
            data =  cursor.fetchall()
            return data
        
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
            
    def delete(self,test_name, table):
        """ Tesztadatok törléséért felelős függvény. """
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            
            cursor.execute(f"SELECT {table}_id FROM {table}s WHERE {table}_name=?", (test_name,))
            result = cursor.fetchone()
            if result:
                test_id = result[0]
                cursor.execute(f"DELETE FROM {table}s WHERE {table}_id=?", (test_id,))
                cursor.execute(f"SELECT picture FROM {table}_data WHERE {table}_id=?", (test_id,))
                images = cursor.fetchall()
                ExerciseManager.__delete_pictures(images)
                cursor.execute("DELETE FROM results WHERE exercise_id = ? AND type = ?", (test_id,table,))  
                cursor.execute(f"DELETE FROM {table}_data WHERE {table}_id=?", (test_id,))
                conn.commit()
                self.successful_deletion.emit()
            else:
                traceback.print_exc()
                self.unsuccessful_deletion.emit()
                
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
                
    def edit(test_name, table):
        """ Feladatok módosításakor betöltendő adatok előállításához használatos függvény. """
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT {table}_id FROM {table}s WHERE {table}_name=?", (test_name,))
            result = cursor.fetchone()
            return result
        
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
                
    @staticmethod
    def __delete_pictures(images):
        """ Segédfüggvény, a képek törlését végzi a fájlrendszerből."""
        for (image_path,) in images:
            if os.path.exists(image_path):
                os.remove(image_path)
                
    @staticmethod
    def get_exercise_paths(exercise_id, table, user_id):
        """ Egy feladathoz a hozzávaló tesztadatokból a képek elérési útjait lekérdező függvény."""
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT picture FROM {table}_data WHERE {table}_id=? AND image_id <> 0 AND user_id = ?", (exercise_id,user_id, ))
            result = cursor.fetchall()
            return result
            
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_exercise_answers(exercise_id, table, user_id):
        """ Egy feladathoz a hozzávaló tesztadatokból a válaszokat lekérdező függvény."""
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT answer FROM {table}_data WHERE {table}_id=? AND image_id <> 0 AND user_id = ?", (exercise_id,user_id, ))
            result = cursor.fetchall()
            return result
            
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def add_results(table, user_id, test_name, exercise_id, score):
        """ Egy feladat kitöltése után az eredményeket a results táblába betöltő függvény."""        
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT username FROM users WHERE id=?", (user_id,))
            username = cursor.fetchone()
            if username:
                cursor.execute("SELECT * FROM results WHERE user_id=? AND exercise_id=? AND type=?", (user_id, exercise_id, table))
                exists = cursor.fetchone()
                if exists:
                    cursor.execute("UPDATE results SET score=? WHERE user_id=? AND exercise_id=? AND type=?", (score, user_id, exercise_id, table))
                else:
                    cursor.execute("INSERT INTO results (user_name, user_id, type, test_name, exercise_id, score) VALUES (?, ?, ?, ?, ?, ?)", 
                                (username[0], user_id, table, test_name, exercise_id, score))
                conn.commit()
            else:
                raise DatabaseException from e
            
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
            
            