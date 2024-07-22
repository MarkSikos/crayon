
import sqlite3
from PyQt6.QtGui import QGuiApplication
import traceback
import os
from Modell.UtilityModules.ConfigUtils import ConfigUtils
from Modell.UtilityModules.Exceptions import DatabaseException
from PyQt6.QtCore import QObject, pyqtSignal

IMAGE_DIR = 'Persistence/image_dump'

class SubjectManager(QObject):
    """ A tantárgyak és jegyzetek kezeléséért felelős függvény. """
    
    # Események
    
    subject_added_succesfully = pyqtSignal()
    subject_added_unsuccesfully = pyqtSignal()
    subject_removed_unsuccesfully = pyqtSignal()
    subject_removal_recursively = pyqtSignal()
    subject_removed_succesfully = pyqtSignal()
    note_deleted_succesfully = pyqtSignal()
    note_deleted_unsuccesfully = pyqtSignal()
    note_added_succesfully = pyqtSignal()
    note_added_unsuccesfully = pyqtSignal()
    
    # Konstruktor 
    
    def __init__(self):
        super().__init__()
        self.__recursive_subject_id = None
    
    # A logikát megvalósító függvények
    
    def add_subject(self,name):
        """ Eg tantárgy hozzáadásáért felelős függvény"""
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM subjects WHERE subject_name = ?", (name,))
            if cursor.fetchone():
                self.subject_added_unsuccesfully.emit()
                return
            else:
                cursor.execute("INSERT INTO subjects (subject_name) VALUES (?)", (name,))
                conn.commit()
                self.subject_added_succesfully.emit()
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
                
    def remove_subject(self,subject_name):
        """ Eg tantárgy törléséért felelős függvény"""
        connection_open = True
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT subject_id FROM subjects WHERE subject_name = ?", (subject_name,))
            subject = cursor.fetchone()
            if not subject:
                self.subject_removed_unsuccesfully.emit()
                return

            subject_id = subject[0]  # Assuming subject_id is the first column
            cursor.execute("SELECT * FROM note WHERE subject_id = ?", (subject_id,))
            if cursor.fetchone():
                conn.close()
                connection_open = False
                self.__recursive_subject_id = subject_id
                self.subject_removal_recursively.emit()
                return
            else:
                cursor.execute("DELETE FROM subjects WHERE subject_id = ?", (subject_id,))
            conn.commit()
            self.subject_added_succesfully.emit()
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if connection_open and conn:
                conn.close()
        
    def remove_recuresively(self):
        """Rekurzív jegyezettörlésért felelős függvény. """
        if self.__recursive_subject_id is not None:
            try:
                conn = sqlite3.connect('Persistence/database.db')
                cursor = conn.cursor()
                cursor.execute("SELECT picture FROM note WHERE subject_id = ?", (self.__recursive_subject_id,))
                images = cursor.fetchall()
                SubjectManager.__delete_pictures(images)     
                cursor.execute("DELETE FROM note WHERE subject_id = ?", (self.__recursive_subject_id,))
                cursor.execute("DELETE FROM subjects WHERE subject_id = ?", (self.__recursive_subject_id,))
                conn.commit()
                self.subject_removed_succesfully.emit()
                
            except sqlite3.Error as e:
                traceback.print_exc()
                raise DatabaseException from e
            finally:
                if conn:
                    conn.close()
        else:
            raise DatabaseException()
            
    @staticmethod   
    def load_subjects():
        """ Tantárgyak neveinek az adatbázisból való kinyeréséért felelős függvény. """
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT subject_name FROM subjects")
            subjects = cursor.fetchall()
            subject_names = [subject[0] for subject in subjects]
            return subject_names
        
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
                
    @staticmethod
    def get_subjects():
        """ Tantárgyak adatainak az adatbázisból való kinyeréséért felelős függvény. """
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT subject_id, subject_name FROM subjects")
            subjects = cursor.fetchall()
            return subjects

        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
            
    @staticmethod
    def get_notes(subject_id, user_id):
        """ Jegyzetek adatainak az adatbázisból való kinyeréséért felelős függvény. """
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute(""" SELECT MIN(note_id), note_name FROM note WHERE subject_id = ? AND user_id = ? GROUP BY note_name """, (subject_id,user_id,))
            notes = cursor.fetchall()
            return notes
        
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
                
    @staticmethod    
    def get_subject_name( subject_id):
        """ Egy megfelelő tantárgy nevének az adatbázisból való kinyeréséért felelős függvény. """
        try:
            conn = sqlite3.connect('Persistence/database.db')  
            cursor = conn.cursor()
            
            cursor.execute("SELECT subject_name FROM subjects WHERE subject_id = ?", (subject_id,))
            result = cursor.fetchone()
            if result:
                return result[0]  
            else:
                return ""  
            
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e 
        finally:
            if conn:
                conn.close()

    def delete_note(self,name, subject_id, user_id):
        """ Egy jegyzet adatainak az adatbázisból való törléséért felelős függvény. A jegyzethez tartozó képeket is törli a fájlrendszerből."""
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            
            cursor.execute("select picture FROM note WHERE note_name = ? AND subject_id = ? AND user_id = ?", (name, subject_id, user_id))
            images = cursor.fetchall()
            cursor.execute("DELETE FROM note WHERE note_name = ? AND subject_id = ? AND user_id = ?", (name, subject_id, user_id))
            
            if cursor.rowcount > 0:
                SubjectManager.__delete_pictures(images)
                conn.commit()
                self.note_deleted_succesfully.emit()
            else:
                self.note_deleted_unsuccesfully.emit()
                return
            
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()

    def add_note(self,name,subject_id, user_id):
        """ Egy jegyzet hozzáadásáért felelős függvény. """
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM note WHERE note_name = ? AND subject_id = ? AND user_id = ?", (name, subject_id, user_id))
            if cursor.fetchone():
                self.note_added_unsuccesfully.emit()
                return

            cursor.execute("SELECT MAX(image_id) FROM note WHERE subject_id = ? AND note_name = ? AND user_id = ?", (subject_id, name, user_id))
            max_image_id = cursor.fetchone()[0]
            new_image_id = 1 if max_image_id is None else max_image_id + 1

            cursor.execute("SELECT MAX(note_id) FROM note WHERE user_id = ?", (user_id,))
            max_note_id = cursor.fetchone()[0]
            new_note_id = 1 if max_note_id is None else max_note_id + 1
            
            screen = QGuiApplication.primaryScreen().geometry()
            cursor.execute("INSERT INTO note (user_id, note_id, note_name, subject_id, picture, image_id) VALUES (?, ?, ?, ?, ?, ?)", 
                        (user_id, new_note_id, name, subject_id, ConfigUtils.create_and_save_big_image(screen.width(), screen.height()), new_image_id))
            
            cursor.execute("INSERT INTO note (user_id, note_id, note_name, subject_id, picture, image_id) VALUES (?, ?, ?, ?, ?, ?)", 
                        (user_id, new_note_id, name, subject_id, ConfigUtils.create_small_image("""screen.width(), screen.height()"""), -1))
            conn.commit()
            self.note_added_succesfully.emit()
            
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
   
    @staticmethod
    def get_subject_id(subject_name):
        """ Egy tárgy id-jének lekérdezéséért felelős függvény (a tárgy neve alapján)."""
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT subject_id FROM subjects WHERE subject_name = ?", (subject_name,))
            subject = cursor.fetchone()
            return subject
            
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
                
    @staticmethod
    def __delete_pictures(images):
        """ Segédfüggvény, a képek fájlrendszerből való törléséért felel."""
        for (image_path,) in images:
            if os.path.exists(image_path):
                os.remove(image_path)
