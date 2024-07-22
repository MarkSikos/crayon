import sqlite3
import traceback,os
from PyQt6.QtGui import QImage
from PyQt6.QtCore import QObject, pyqtSignal
from Modell.UtilityModules.PasswordHandler import PasswordHandler
from Modell.UtilityModules.Exceptions import DatabaseException
from Modell.UtilityModules.ConfigUtils import ConfigUtils

IMAGE_DIR = 'Persistence/image_dump'

class AdminMenuWindowUtils(QObject):
    """ 
    Az adminisztációs feladatok logikájáért felelős osztály.
    """
    
    # Események
    
    successfully_added_event = pyqtSignal()
    unsuccesfully_added_event = pyqtSignal()    
    no_teacher_event = pyqtSignal()
    
    # A logika megvalósításáért felelős függvények
    
    def add_user_db(self,username,password, role):
        """ Egy felhasználó hozzáadása az adatbázishoz."""
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            
            if role == "Student":
                cursor.execute("""SELECT id FROM users WHERE role = 'Teacher' """)
                teacher_user_id = cursor.fetchone()
                if teacher_user_id is None:
                    self.no_teacher_event.emit()
                    return
            
            cursor.execute("SELECT * FROM users WHERE username = ?",(username,))
            if cursor.fetchone():
                self.unsuccesfully_added_event.emit()
                return
            
            if role == "Teacher":
                cursor.execute("SELECT * FROM users WHERE role = 'Teacher'")
                if cursor.fetchone():
                    self.unsuccesfully_added_event.emit()
                    return
                            
            hashed_password = PasswordHandler.hash_password(password)
            cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, hashed_password, role))
            user_id = cursor.lastrowid
            conn.commit()
            
            if role == "Student":
                cursor.execute("""SELECT id FROM users WHERE role = 'Teacher' """)
                teacher_user_id = cursor.fetchone()
        
                if teacher_user_id is None:
                    self.unsuccesfully_added_event.emit()
                    return
                    
                teacher_user_id = teacher_user_id[0]
                cursor.execute(""" SELECT test_id, test_name, test_date FROM tests """)
                teacher_tests = cursor.fetchall()
                
                for teacher_test_id, _, _ in teacher_tests:
                    cursor.execute("SELECT question, answer, picture, image_id , test_id, user_id FROM test_data WHERE test_id = ? AND user_id = ?", (teacher_test_id,teacher_user_id,))
                    test_data_records = cursor.fetchall()
                    for question, answer, picture_path, image_id, test_id , _ in test_data_records:
                        new_image_path = None
                        teacher_image = QImage()
                        teacher_image.load(picture_path)
                        height = teacher_image.height()
                        width = teacher_image.width()
                        if image_id == 0:
                            new_image_path = ConfigUtils.create_and_save_big_image(width,height)
                        else:
                            new_image_path = ConfigUtils.create_small_image()    
                        cursor.execute("INSERT INTO test_data (user_id, test_id, question, answer, picture, image_id) VALUES (?, ?, ?, ?, ?, ?)", 
                                    (user_id, test_id, question, answer, new_image_path, image_id))
                cursor.execute(""" SELECT homework_id, homework_name, homework_date FROM homeworks """)
                teacher_homeworks = cursor.fetchall()
                
                for teacher_homework_id, _, _ in teacher_homeworks:
                    cursor.execute("SELECT question, answer, picture, image_id , homework_id, user_id FROM homework_data WHERE homework_id = ? AND user_id = ?", (teacher_homework_id,teacher_user_id,))
                    homework_data_records = cursor.fetchall()
                    for question, answer, picture_path, image_id, homework_id , _ in homework_data_records:
                        new_image_path = None
                        teacher_image = QImage()
                        teacher_image.load(picture_path)
                        height = teacher_image.height()
                        width = teacher_image.width()
                        if image_id == 0:
                            new_image_path = ConfigUtils.create_and_save_big_image(width,height)
                        else:
                            new_image_path = ConfigUtils.create_small_image() 
                        cursor.execute("INSERT INTO homework_data (user_id, homework_id, question, answer, picture, image_id) VALUES (?, ?, ?, ?, ?, ?)", 
                                    (user_id, homework_id, question, answer, new_image_path, image_id))
                conn.commit()
                self.successfully_added_event.emit()
                
            else:
                self.successfully_added_event.emit()
                
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
            
    def delete_user_db(self,selected_user):
        """ Egy felhasználó adatbázisból való törléséért felelős függvény. Amennyiben az utolsó felhasználót töröljük, 
        a bennmaradó adatok törlésre kerülnek.""" 
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, role FROM users WHERE username = ?", (selected_user,))
            user_info = cursor.fetchone()
            if user_info:
                user_id, selected_user_role = user_info
                if selected_user_role == 'Admin':
                    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'Admin'")
                    admin_count = cursor.fetchone()[0]
                    if admin_count <= 1:
                        self.unsuccesfully_added_event.emit()
                        return
                cursor.execute("SELECT picture FROM test_data WHERE user_id = ?", (user_id,))
                images = cursor.fetchall()
                AdminMenuWindowUtils.__delete_pictures(images)
                cursor.execute("DELETE FROM test_data WHERE user_id = ?", (user_id,))
                
                cursor.execute("SELECT picture FROM homework_data WHERE user_id = ?", (user_id,))
                images = cursor.fetchall()
                AdminMenuWindowUtils.__delete_pictures(images)
                cursor.execute("DELETE FROM homework_data WHERE user_id = ?", (user_id,))
                
                cursor.execute("SELECT picture FROM note WHERE user_id = ?", (user_id,))
                images = cursor.fetchall()
                AdminMenuWindowUtils.__delete_pictures(images)
                
                cursor.execute("DELETE FROM note WHERE user_id = ?", (user_id,))
                cursor.execute("DELETE FROM results WHERE user_id = ?", (user_id,))               
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                if cursor.rowcount > 0:
                    conn.commit()
                    selected_user = None  
                    self.successfully_added_event.emit()
                else:
                    self.unsuccesfully_added_event.emit()
                    return
                
                cursor.execute("SELECT id FROM users")
                entries = cursor.fetchall()
                if entries and len(entries) == 1:
                    cursor.execute("DELETE FROM subjects")
                    cursor.execute("DELETE FROM tests")
                    cursor.execute("DELETE FROM homeworks")
                    conn.commit()
                    
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
            
    @staticmethod       
    def fetch_users():
        """ Felhasználói adatoknak az adatbázisból való kinyeréséért felelős függvény. """
        users = []
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT username, role FROM users ORDER BY role, username")
            users = cursor.fetchall()
            
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()
        return users
    
    @staticmethod
    def __delete_pictures(images):
        """ Segédfüggvény, a felhasználók törlése esetén, az ő tesztjeikhez tartozó képeknek a fájlrendszerből való törléséért felelős függvény."""
        for (image_path,) in images:
            if os.path.exists(image_path):
                os.remove(image_path)

            
        

            
        