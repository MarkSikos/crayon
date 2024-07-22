import sqlite3
import traceback
import os
from Modell.UtilityModules.Exceptions import DatabaseException
from Modell.UtilityModules.ConfigUtils import ConfigUtils
from PyQt6.QtCore import QObject, pyqtSignal

class ExerciseConfigWindowManager(QObject):
    """
    A tesztlétrehozó ablak logikájáért felelős osztály.
    """
    
    # Események
    exercise_created_succesfully = pyqtSignal()
    exercise_created_unsuccesfully = pyqtSignal()
    
    # Logikáért felelős függvények
    
    @staticmethod
    def get_next_id(table):
        """ Az adatbázisból lekéri a legmagasabb exercise_id értéket, és egyet hozzáadva meghatározza a következőt. """
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT MAX({table}_id) FROM {table}s")
            max_id = cursor.fetchone()[0]
            return (max_id if max_id is not None else 0) + 1
        
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
            
    def create_exercise(self,editing, table, exercise_name, exercise_date, exercise_id, questions, answers, user_id, height, width):
        """ Elkészíti és elmenti az előállított feladatot. """
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE role <> 'Admin'")
            users = cursor.fetchall()
            
            if editing:
                cursor.execute(f"SELECT * FROM {table}s WHERE {table}_name = ? AND {table}_id <> ? ", (exercise_name, exercise_id,))
                entries = cursor.fetchone()
                if entries:
                    self.exercise_created_unsuccesfully.emit()
                    return
                
                cursor.execute(f"UPDATE {table}s SET {table}_name = ?, {table}_date = ? WHERE {table}_id = ?", (exercise_name, exercise_date, exercise_id))
                cursor.execute(f"SELECT picture FROM {table}_data WHERE {table}_id = ? ", (exercise_id, ))   
                images = cursor.fetchall()
                ExerciseConfigWindowManager.__delete_pictures(images)
                cursor.execute(f"DELETE FROM {table}_data WHERE {table}_id = ? ", (exercise_id, ))
                cursor.execute(f"DELETE FROM results WHERE type = ? AND test_name = ? AND exercise_id = ?",(table, exercise_name, exercise_id,))   
            else:
                cursor.execute(f"SELECT * FROM {table}s WHERE {table}_name = ? ", (exercise_name, ))
                entries = cursor.fetchone()
                if entries:
                    self.exercise_created_unsuccesfully.emit()
                    return
                new_exercise_id = ExerciseConfigWindowManager.get_next_id(table)
                cursor.execute(f"INSERT INTO {table}s ( {table}_id, {table}_name, {table}_date) VALUES ( ?, ?, ?)", 
                            ( new_exercise_id, exercise_name, exercise_date))
            for user in users:
                user_id = user[0]
                cursor.execute(f"INSERT INTO {table}_data (user_id, {table}_id, question, answer, picture, image_id) VALUES (?,?, ?, ?, ?, ?)", (user_id,new_exercise_id if not editing else exercise_id,"explanation", "explanation", ConfigUtils.create_and_save_big_image(width, height), 0))
                
                for i, (question, answer) in enumerate(zip(questions, answers)):
                    cursor.execute(f"INSERT INTO {table}_data (user_id, {table}_id, question, answer, picture, image_id) VALUES (?, ?, ?, ?, ?, ?)", 
                                (user_id, new_exercise_id if not editing else exercise_id, question, answer, ConfigUtils.create_small_image(), i + 1))
            conn.commit()
            self.exercise_created_succesfully.emit()
            
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
            
    def load_existing_data(table,exercise_id,user_id):
        """ Módosítás esetén a betöltendő adatokat lekérő függvény."""
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT {table}_name, {table}_date FROM {table}s WHERE {table}_id=? ", (exercise_id,))
            exercise_info = cursor.fetchone()
            cursor.execute(f"SELECT question, answer, image_id FROM {table}_data WHERE {table}_id=? AND image_id != 0 AND user_id  = ? ORDER BY image_id ASC", (exercise_id,user_id,))
            question_data = cursor.fetchall()
            return [exercise_info, question_data]
        
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
            
    @staticmethod
    def __delete_pictures(images):
        """ Segédfüggvény, a képek fájlrendszerből való törléséért felelős."""
        for (image_path,) in images:
            if os.path.exists(image_path):
                os.remove(image_path)

            
    