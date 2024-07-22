import sqlite3, traceback
from Modell.UtilityModules.Exceptions import DatabaseException

class DashboardUtilities():
    """ 
    A tanári dashboarddal kapcsolatos háttérlogikáért felelős Singleton osztály.
    """
    # Konstruktor
    
    _instance = None
    
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.__instance_initialized = False
        return cls._instance

    def __init__(self):
        if not self.__instance_initialized:
            super().__init__()
            self.__instance_initialized = True
            
    # A logikát megvalósító függvények
    
    @staticmethod
    def fetch_data():
        """ A feladatok adatainak az adatbázisból való lehívásáért felelős függvény."""
        conn = None
        try:
            conn = sqlite3.connect('Persistence/database.db')
            cursor = conn.cursor()
            cursor.execute("""SELECT user_name, type, test_name, score FROM results WHERE type = 'test'""")
            test_data = cursor.fetchall()
            cursor.execute("""SELECT user_name, type, test_name, score FROM results WHERE type = 'homework'""")
            homework_data = cursor.fetchall()
            return [test_data, homework_data]
        except sqlite3.Error as e:
            traceback.print_exc()
            raise DatabaseException from e
        finally:
            if conn:
                conn.close()

    
    