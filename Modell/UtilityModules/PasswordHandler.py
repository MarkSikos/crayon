import sqlite3
import bcrypt
import traceback
from PyQt6.QtCore import QObject, pyqtSignal
from Modell.UtilityModules.Exceptions import DatabaseException

class PasswordHandler(QObject):
    """
    A felhasználó beléptetésének logikájáért felelős Singleton osztály.
    """
    
    # Konstruktor
    
    __instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls)
            cls.__instance.__instance_initialized = False
        return cls.__instance

    def __init__(self):
        if not self.__instance_initialized:
            super().__init__()
            self.__instance_initialized = True
    
    # Események
    
    successful_login = pyqtSignal()
    unsuccessful_login = pyqtSignal()
    
    # A logikáért felelős függvények
    
    @staticmethod
    def hash_password(plain_text_password):
        """ Egy jelszó hasheléséért felelős függvény"""
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(plain_text_password.encode('utf-8'), salt)
        return hashed_password

    @staticmethod
    def check_password(stored_password, provided_password):
        """ Egy jelszó ellenőrzéséért felelős függvény"""
        return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password)

    def login(self,username, provided_password):
        """ A belépést kezelő függvény"""
        if not username or not provided_password:
            self.unsuccessful_login.emit()
            return        
        try:
            conn = sqlite3.connect('Persistence/database.db')  
            cursor = conn.cursor()
            
            cursor.execute("SELECT password_hash, role FROM users WHERE username=?", (username,))
            result = cursor.fetchone()
            # Ellenőrizzük hogy van e megfelelő nevű felhasználó
            if result:
                stored_password_hash, _ = result
                if PasswordHandler.check_password(stored_password_hash, provided_password):
                    cursor.execute("SELECT id, password_hash, role FROM users WHERE username = ?", (username,))
                    result = cursor.fetchone()
                    # Ellenőrizzük hogy megfelelően tárolva van -e a jelszó Hash értéke (illetve az adatbázis integritását)
                    if result:
                        _, stored_password_hash, _ = result
                        # Leellenőrizzük hogy helyes -e a jelszó (Hash értékek összehasonlításával)
                        if PasswordHandler.check_password(stored_password_hash, provided_password):
                            # Sikeres belépés
                            self.successful_login.emit()
                        else:
                            self.unsuccessful_login.emit()
                    else:
                        self.unsuccessful_login.emit()
                else:
                    self.unsuccessful_login.emit()
            else:
                self.unsuccessful_login.emit()
                
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException() from e
        finally:
            if conn:
                conn.close()
        
    def fetch_user_data(self,username):
        """ A felhasználó szükséges belépési adatainak az adatbázisból való kinyerését valósytja meg. """       
        try:
            conn = sqlite3.connect('Persistence/database.db')  
            cursor = conn.cursor()
            cursor.execute("SELECT id, role FROM users WHERE username = ?", (username,))
            id, role = cursor.fetchone()
            return [True,id, role]
        
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException() from e
        finally:
            if conn:
                conn.close()
        
            
        
        