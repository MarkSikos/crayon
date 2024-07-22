import sqlite3
from PyQt6.QtWidgets import QMessageBox
from Modell.UtilityModules.Exceptions import DatabaseException
import traceback
from PyQt6.QtCore import pyqtSignal, QObject

class ImageManager(QObject):
    """ A jegyzetek és feladatok képeinek és egyéb adatainak kezelésének a logikájáért felelős osztály."""
    
    # Események
    image_saved = pyqtSignal()
    
    # A logikát megvalósító függvények
    
    @staticmethod
    def get_note_name(note_id, user_id):
        """ A jegyzet címét az adatbázisból lekérő függvény. """
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT note_name FROM note WHERE note_id = ? AND user_id = ?", (note_id,user_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                raise DatabaseException from e
            
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
            
    @staticmethod      
    def fetch_images_from_db( note_id, user_id):
        """ Az adatbázisból egy jegyzethez tartozó képek elérési útját (és id-jét) lekérő függévny."""
        images = []
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT image_id, picture FROM note WHERE note_id = ? AND user_id = ?", (note_id, user_id,))
            images = cursor.fetchall()

        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
        return images
    
    def save_new_image_to_note(self,path, note_id, user_id,subject_id,note_name, image_id=None):
        """ Egy kép adatainak elmentéséért felelős függvény. """
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            
            if image_id is not None:
                cursor.execute("UPDATE note SET picture = ? WHERE note_id = ? AND image_id = ? AND user_id = ?", 
                            (path, note_id, image_id, user_id))
            else:
                cursor.execute("SELECT MAX(image_id) FROM note WHERE note_id = ? AND user_id = ? AND subject_id = ?",
                           (note_id, user_id, subject_id))
                result = cursor.fetchone()
                if result and result[0] is not None:
                    new_image_id = result[0] + 1
                else:
                    new_image_id = 0  
                cursor.execute("INSERT INTO note (user_id, note_id, subject_id, note_name, picture, image_id) VALUES (?, ?, ?, ?, ?, ?)", (user_id, note_id, subject_id, note_name, path, new_image_id))
            conn.commit()
            self.image_saved.emit()
            
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
            
    @staticmethod
    def save_new_image_to_exercise(path, test_id, user_id, table, image_id=None):
        """ Egy feladathoz tartozó új kép adatainak az elmentéséért felelős függvény. """
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            if image_id is not None:
                cursor.execute(f"UPDATE {table}_data SET picture = ? WHERE {table}_id = ? AND image_id = ? AND user_id = ?", 
                            (path, test_id, image_id, user_id))
            else:
                cursor.execute(f"SELECT MAX(image_id) FROM {table}_data WHERE {table}_id = ? AND user_id = ?", (test_id, user_id))
                max_image_id = cursor.fetchone()[0]
                new_image_id = 1 if max_image_id is None else max_image_id + 1
                cursor.execute(f"INSERT INTO {table}_data (user_id, {table}_id, question, answer, picture, image_id) VALUES (?, ?, ?, ?, ?, ?)", 
                            (user_id, test_id, "", "", path, new_image_id))
            conn.commit()
            
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
            
    @staticmethod   
    def get_large_image(table, test_id, user_id):
        """ Nagyméretű kép adatainak lekérése az adatbázisból. """
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute(f"SELECT picture FROM {table}_data WHERE {table}_id = ? AND image_id = 0 AND user_id = ?", (test_id, user_id,))
            result = cursor.fetchone()
            conn.close()
            return result
        
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
            
    @staticmethod    
    def get_question_data(table, test_id, user_id):
        """ Egy feladat kérdéseihez tartozó adatok lekérése az adatbázisból. """
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT question, answer, picture, image_id FROM {table}_data WHERE {table}_id = ? AND image_id != 0 AND user_id = ?
                ORDER BY image_id ASC """, (test_id,user_id,))
            question_data = cursor.fetchall()
            return question_data
        
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
            
    @staticmethod
    def fetch_drawing_areas(table,test_id, user_id):
        """ Egy feladat adatainak lekérése az adatbázisból."""
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute(f""" SELECT picture, image_id FROM {table}_data WHERE {table}_id = ? AND image_id != 0 AND user_id = ?
                ORDER BY image_id ASC """, (test_id,user_id,))
            images = cursor.fetchall()
            return images
        
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
        
