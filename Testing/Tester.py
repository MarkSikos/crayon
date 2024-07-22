
import sqlite3, sys, os
import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QImage

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Modell.Logic.DrawingArea import DrawingArea
from Modell.Logic.ExerciseConfigWindowManager import ExerciseConfigWindowManager
from Modell.Logic.ExerciseManager import ExerciseManager
from Modell.Logic.ImageManager import ImageManager
from Modell.Logic.SubjectManager import SubjectManager
from Modell.UtilityModules.PasswordHandler import PasswordHandler
from Modell.UtilityModules.Exceptions import DatabaseException, FileSystemException
from Modell.UtilityModules.ConfigUtils import ConfigUtils
from Modell.UtilityModules.AdminMenuWindowUtils import AdminMenuWindowUtils
from Modell.UtilityModules.DashboardUtilities import DashboardUtilities
from Modell.UtilityModules.Initializer import Initializer
from Modell.UtilityModules.StyleSheetUtilities import StyleSheetUtilities

IMAGE_DIR = 'Persistence/image_dump'

###############################################################
####################### UNITTESZTELÉS #########################
###############################################################

""" 
    Az AdminmenuWindowUtils osztály tesztelése
"""
class TestAdminMenuWindowUtils(unittest.TestCase):

    def setUp(self):
        self.utils = AdminMenuWindowUtils()
        
    """
        Annak az esetnek a tesztelése, amikor egy diákot próbálunk hozzáadni, úgy hogy az osztálynak nincsen osztályfőnöke.
    """        
    @patch('sqlite3.connect')
    @patch.object(PasswordHandler, 'hash_password', return_value=b'hashelt jelszo')
    def test_add_student_no_teacher(self, mock_hash_password, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.side_effect = [None]
        
        utils = AdminMenuWindowUtils()
        utils.no_teacher_event = MagicMock()
        utils.unsuccesfully_added_event = MagicMock()
        utils.successfully_added_event = MagicMock()
        
        utils.add_user_db("new_student", "password", "Student")
        utils.no_teacher_event.emit.assert_called_once()
        utils.unsuccesfully_added_event.emit.assert_not_called()
        utils.successfully_added_event.emit.assert_not_called()

    """
        Annak az esetnek a tesztelése, amikor egy utolsó felhasználó törlése során ki kell üríteni az adatbázist.
    """
    @patch('sqlite3.connect')
    def test_delete_user_last_non_admin_user(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.side_effect = [(2, 'Student'), (1, ), (1,), ] # 2 felhasználó van, és szerepelnek adatok a táblákban
        mock_cursor.fetchall.side_effect = [ [], [], [] , [(1,)], ] # Azaz kiürült az adatbázis ,csak egy felhasználó maradt (Admin)

        mock_cursor.rowcount = 1  
        utils = AdminMenuWindowUtils()
        utils.successfully_added_event = MagicMock()
        utils.unsuccesfully_added_event = MagicMock()
        utils.delete_user_db("diak1")
        utils.successfully_added_event.emit.assert_called_once()
        utils.unsuccesfully_added_event.emit.assert_not_called()
        mock_cursor.execute.assert_any_call("DELETE FROM subjects")
        mock_cursor.execute.assert_any_call("DELETE FROM tests")
        mock_cursor.execute.assert_any_call("DELETE FROM homeworks")


    """
        Annak az esetnek a tesztelése, amikor egy már létező felhasználót próbálunk hozzáadni az adatbázishoz.
    """
    @patch('sqlite3.connect')
    @patch.object(PasswordHandler, 'hash_password', return_value=b'jelszo')
    def test_add_user_db_user_already_exists(self, mock_hash_password, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.side_effect = [(1,), None, None]
        self.utils.unsuccesfully_added_event = MagicMock()
        self.utils.add_user_db("letezo_felhasznalo", "jelszo", "Student")
        mock_cursor.execute.assert_any_call("SELECT * FROM users WHERE username = ?", ("letezo_felhasznalo",))
        self.utils.unsuccesfully_added_event.emit.assert_called_once()

    """
        Annak az esetnek a tesztelése, amikor egy szabályos felhasználót adunk hozzá az adatbázishoz.
    """
    @patch('sqlite3.connect')
    @patch('PyQt6.QtGui.QImage.load', return_value=True)
    @patch.object(PasswordHandler, 'hash_password', return_value=b'jelszo')
    @patch.object(ConfigUtils, 'create_and_save_big_image', return_value='uj_eleresi_ut')
    @patch.object(ConfigUtils, 'create_small_image', return_value='uj_eleresi_ut_kisebb')
    def test_add_user_db(self, mock_create_small_image, mock_create_and_save_big_image, mock_image_load, mock_hash_password, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.side_effect = [None, None, (1,)]
        mock_cursor.fetchall.side_effect = [[], [], []]

        self.utils = AdminMenuWindowUtils()
        self.utils.successfully_added_event = MagicMock()
        self.utils.unsuccesfully_added_event = MagicMock()
        self.utils.no_teacher_event = MagicMock()
        self.utils.add_user_db("uj_felhasznalo", "jelszo", "Teacher")
        mock_cursor.execute.assert_any_call("SELECT * FROM users WHERE username = ?", ("uj_felhasznalo",))
        mock_cursor.execute.assert_any_call("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", ("uj_felhasznalo", b'jelszo', "Teacher"))
        self.utils.successfully_added_event.emit.assert_called_once()
    """
        Annak az esetnek a tesztelése, amikor egy szabályos felhasználót törlünk az adatbázisból.
    """
    @patch('sqlite3.connect')
    def test_delete_user_db_success(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.side_effect = [(1, 'Student'), (0,), (0,), (0,), (0,)]
        mock_cursor.rowcount = 1

        self.utils.successfully_added_event = MagicMock()
        self.utils.delete_user_db("felhasznalo")
        mock_cursor.execute.assert_any_call("SELECT id, role FROM users WHERE username = ?", ("felhasznalo",))
        mock_cursor.execute.assert_any_call("DELETE FROM users WHERE id = ?", (1,))
        self.utils.successfully_added_event.emit.assert_called_once()

    """
        Annak az esetnek a tesztelése, amikor az utolsó adminisztrátor felhasználót próbáljuk törölni.
    """
    @patch('sqlite3.connect')
    def test_delete_user_db_prevent_last_admin_deletion(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.side_effect = [(1, 'Admin'), (1,)]
        
        self.utils.unsuccesfully_added_event = MagicMock()
        self.utils.delete_user_db("adminisztrator")
        mock_cursor.execute.assert_any_call("SELECT id, role FROM users WHERE username = ?", ("adminisztrator",))
        mock_cursor.execute.assert_any_call("SELECT COUNT(*) FROM users WHERE role = 'Admin'")
        self.utils.unsuccesfully_added_event.emit.assert_called_once()

""" 
    Az ConfigUtils osztály tesztelése
"""
class TestConfigUtils(unittest.TestCase):
    """
        Egy nagyméretű kép (100x500) elkészítése, és mentése, mockolt elérési útra.
    """
    @patch('os.path.join', return_value='Persistence/image_dump/mockolt_kep.png')
    def test_create_and_save_big_image(self, mock_join):
        width, height = 1000, 500
        image_path = ConfigUtils.create_and_save_big_image(width, height)
        self.assertEqual(image_path, 'Persistence/image_dump/mockolt_kep.png')

    """ 
        Egy kisméretű kép elkészítése és mentése.
    """
    def test_create_small_image(self):
        utils = ConfigUtils()
        image_path = utils.create_small_image(path='Persistence/image_dump/mockolt_kep1.png')
        self.assertEqual(image_path, 'Persistence/image_dump/mockolt_kep1.png')


""" 
    Az DashboardUtilities osztály tesztelése
"""

class TestDashboardUtilities(unittest.TestCase):
    """ 
        Teszteljük, hogy adatbázishiba fellépése esetén kiváltásra kerül-e az általunk definiált DatabaseException.
    """
    @patch('sqlite3.connect', side_effect=sqlite3.Error)
    def test_fetch_data_database_exception(self, mock_connect):
        with self.assertRaises(DatabaseException):
            DashboardUtilities.fetch_data()
        mock_connect.assert_called_once_with('Persistence/database.db')


""" 
    Az Initializer osztály tesztelése
"""
class TestInitializer(unittest.TestCase):

    def setUp(self):
        self.initializer = Initializer()

    """ 
        Teszteljük, hogy a kulcsfontosságú első adminisztrátor hozzáadódik-e az adatbázishoz.
    """
    @patch('sqlite3.connect')
    @patch.object(PasswordHandler, 'hash_password', return_value=b'hashelt_jelszo')
    def test_add_admin(self, mock_hash_password, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        self.initializer.add_admin()
        mock_cursor.execute.assert_called_once_with( "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", ("Admin", b'hashelt_jelszo', "Admin"))
        
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()
    
    
""" 
    Az PassworHandler osztály tesztelése
"""
class TestPasswordHandler(unittest.TestCase):

    def setUp(self):
        self.password_handler = PasswordHandler()

    """ 
        Teszteljük, hogy jó, illetve rossz jelszó esetén a függvény helyesen eldönti-e az egyezést, illetve különbséget.
    """
    def test_check_password(self):
        plain_text_password = "jelszo"
        hashed_password = PasswordHandler.hash_password(plain_text_password)
        self.assertTrue(PasswordHandler.check_password(hashed_password, plain_text_password))
        self.assertFalse(PasswordHandler.check_password(hashed_password, "rossz_jelszo"))

    """ 
        Teszteljük, hogy megfelelő belépési adatok esetén a belépés sikeres-e (azaz, hogy a megfelelő események kerülnek-e kiváltásra.
    """
    @patch('sqlite3.connect')
    def test_login_successful(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        hashed_password = PasswordHandler.hash_password("jo_jelszo")
        mock_cursor.fetchone.side_effect = [(hashed_password, 'role'),  (1, hashed_password, 'role')]
        self.password_handler.successful_login = MagicMock()
        self.password_handler.unsuccessful_login = MagicMock()
        self.password_handler.login("felhasznalo", "jo_jelszo")
        
        self.password_handler.successful_login.emit.assert_called_once()
        self.password_handler.unsuccessful_login.emit.assert_not_called()

    """ 
        Teszteljük, hogy helytelen jelszó esetén valóban nem tudunk-e belépni.
    """
    @patch('sqlite3.connect')
    def test_login_wrong_password(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        hashed_password = PasswordHandler.hash_password("helyes_jelszo")
        mock_cursor.fetchone.side_effect = [(hashed_password, 'role'), (1, hashed_password, 'role')]
        self.password_handler.successful_login = MagicMock()
        self.password_handler.unsuccessful_login = MagicMock()
        self.password_handler.login("felhasznalo", "helytelen_jelszo")

        self.password_handler.successful_login.emit.assert_not_called()
        self.password_handler.unsuccessful_login.emit.assert_called_once()
        
    """ 
        Teszteljük, hogy helytelen felhasználóinév esetén valóban nem tudunk-e belépni.
    """
    @patch('sqlite3.connect')
    def test_login_wrong_username(self, mock_connect):
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        mock_cursor.fetchone.return_value = None  # Nem találta a felhasználót
        self.password_handler.successful_login = MagicMock()
        self.password_handler.unsuccessful_login = MagicMock()
        self.password_handler.login("nemletezo_felhasznalo", "létezo_jelszo")
        self.password_handler.successful_login.emit.assert_not_called()
        self.password_handler.unsuccessful_login.emit.assert_called_once()

    """ 
        Teszteljük, hogy kitöltetlen mezők esetén be tudunk-e lépni.
    """
    @patch('sqlite3.connect')
    def test_login_empty_fields(self, mock_connect):
        self.password_handler.successful_login = MagicMock()
        self.password_handler.unsuccessful_login = MagicMock()
        self.password_handler.login("", "")
        self.password_handler.successful_login.emit.assert_not_called()
        self.password_handler.unsuccessful_login.emit.assert_called_once()
   

""" 
    Az StyleSheetUtilities osztály tesztelése
"""
class TestStyleSheetUtilities(unittest.TestCase):

    """ 
        Teszteljük, hogy helytelen elérési útvonal esetén kiváltásra kerül-e az általunk definiált FileSystemException.
    """
    @patch('builtins.open', side_effect=Exception("Nem letezo fajl."))
    def test_load_stylesheet_exception(self, mock_open):
        mock_window = MagicMock()
        with self.assertRaises(FileSystemException):
            StyleSheetUtilities.load_stylesheet(mock_window, "helytelen_fájl.css")
        mock_open.assert_called_once_with("helytelen_fájl.css", "r")
        mock_window.setStyleSheet.assert_not_called()


""" 
    Az DrawingArea osztály tesztelése
"""
class TestDrawingArea(unittest.TestCase):

    def setUp(self):
        self.image_path = "Persistence/image_dump/mockolt_kep3.png"
        self.save_new_image_callback = MagicMock()
        self.drawing_area = DrawingArea(self.image_path, self.save_new_image_callback)

    """ 
        Teszteljük, hogy az visszalépés funkció akkor is működik -e, ha „nincs hova visszalépni”, mivel még nem történt módosítás.
    """
    @patch('Modell.Logic.DrawingArea.QMessageBox.information')
    def test_undo_with_no_action(self, mock_messagebox):
        self.drawing_area.undo()
        mock_messagebox.assert_called_once_with(self.drawing_area, "Visszavonás", "Nem lehet tovább visszavonni!")
        
    """ 
        Teszteljük hogy a save_changes függvény ment-e.
    """
    @patch('PyQt6.QtGui.QImage.save')  
    def test_save_changes(self, mock_save):
        image_path = 'Persistence/image_dump/tsc.png'
        save_new_image_callback = MagicMock()
        image_id = 1
        drawing_area = DrawingArea(image_path, save_new_image_callback, image_id)
        drawing_area._DrawingArea__temp_image = MagicMock(spec=QImage)
        drawing_area.save_changes()
        drawing_area._DrawingArea__temp_image.save.assert_called_once_with(image_path, 'PNG')
        save_new_image_callback.assert_called_once_with(image_path, image_id)

""" 
    Az ExerciseConfigWindowManager osztály tesztelése
"""
class TestExerciseConfigWindowManager(unittest.TestCase):
        
    """ 
        Teszteljük hogy helyesen betülrődnek-e a már létező adatok (amiket a Mock-on keresztül beleadunk).
    """
    @patch('sqlite3.connect')
    def test_load_existing_data(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.side_effect = [('Test Exercise','2024-01-01')]
        mock_cursor.fetchall.side_effect = [[('Question 1',  'Answer 1', 1),('Question 2', 'Answer 2',2)]]
        result = ExerciseConfigWindowManager.load_existing_data('exercise', 1, 1)
        mock_cursor.execute.assert_any_call("SELECT exercise_name, exercise_date FROM exercises WHERE exercise_id=? ", (1, ))
        mock_cursor.execute.assert_any_call( "SELECT question, answer, image_id FROM exercise_data WHERE exercise_id=? AND image_id != 0 AND user_id  = ? ORDER BY image_id ASC", (1, 1) )
        self.assertEqual(result, [('Test Exercise', '2024-01-01'),[('Question 1', 'Answer 1', 1),('Question 2', 'Answer 2', 2)]])

    """ 
        Teszteljük hogy helyesen létrehozunk egy feladatot.
    """
    @patch('sqlite3.connect')
    @patch.object(ConfigUtils, 'create_and_save_big_image', return_value='Persistence/image_dump/kep1.png')
    @patch.object(ConfigUtils, 'create_small_image', return_value='Persistence/image_dump/kep2.png')
    def test_create_exercise_success(self, mock_create_small_image, mock_create_and_save_big_image, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.side_effect = [None, None]
        ExerciseConfigWindowManager.get_next_id = MagicMock(return_value=1)
        manager = ExerciseConfigWindowManager()
        manager.exercise_created_succesfully = MagicMock()
        manager.exercise_created_unsuccesfully = MagicMock()

        manager.create_exercise(False,'test', 'dolgozat', '2024-05-28', None, ['mi az, piros', 'mi az sárga'], ['alma', 'banan'],1,100,100)
        ExerciseConfigWindowManager.get_next_id.assert_called_once_with('test')
        manager.exercise_created_succesfully.emit.assert_called_once()
        manager.exercise_created_unsuccesfully.emit.assert_not_called()

    """ 
        Teszteljük hogy egy feladatot nem tudunk létrehozni, mert már létezik feladat olyan névvel.
    """
    @patch('sqlite3.connect')
    def test_create_exercise_name_exists(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value

        mock_cursor.fetchone.side_effect = [('meglévő dolgozat',)]
        manager = ExerciseConfigWindowManager()
        manager.exercise_created_succesfully = MagicMock()
        manager.exercise_created_unsuccesfully = MagicMock()
        manager.create_exercise(False,'test','meglévő dolgozat','2024-05-28', None, ['mi az, piros', 'mi az sárga'], ['alma', 'banan'],1,100,100)
        manager.exercise_created_succesfully.emit.assert_not_called()
        manager.exercise_created_unsuccesfully.emit.assert_called_once()

    """ 
        Teszteljük hogy a képmódosítás nem lehetséges rossz id esetén (azaz itt ha van id), ez az adatbázishibák miatt fontos, helyes
        működés esetén nem lehetséges.
    """
    @patch('sqlite3.connect')
    def test_edit_exercise_wrong_id(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.side_effect = [('létező házi rossz id-vel',)]
        manager = ExerciseConfigWindowManager()
        manager.exercise_created_succesfully = MagicMock()
        manager.exercise_created_unsuccesfully = MagicMock()
        manager.create_exercise(True,'homework', 'létező házi, rossz idvel', '2024-05-28',1,['2', 'd'],['d', 'd'],1,100,100)
        manager.exercise_created_succesfully.emit.assert_not_called()
        manager.exercise_created_unsuccesfully.emit.assert_called_once()


""" 
    Az ExerciseManager osztály tesztelése
"""
class TestExerciseManager(unittest.TestCase):

    """ 
        Teszteljük, hogy egy teszt törlése megfelelő tesztadatok létezése mellett valóban megtörténik -e.
    """
    @patch('sqlite3.connect')
    @patch.object(ExerciseManager, '_ExerciseManager__delete_pictures')
    def test_delete_success(self, mock_delete_pictures, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = (101,)
        mock_cursor.fetchall.return_value = [('kep1.png',), ('kep2.png',)]
        
        manager = ExerciseManager()
        manager.successful_deletion = MagicMock()
        manager.unsuccessful_deletion = MagicMock()
        manager.delete('dolgozat1', 'test')
        mock_delete_pictures.assert_called_once_with([('kep1.png',), ('kep2.png',)])
        self.assertTrue(manager.successful_deletion.emit.called)
        
    """ 
        Teszteljük, hogy egy teszt törlése, ha a tesztek nem léteznek, valóban nem történik-e meg.
    """    
    @patch('sqlite3.connect')
    def test_delete_failure(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = None
        manager = ExerciseManager()
        manager.successful_deletion = MagicMock()
        manager.unsuccessful_deletion = MagicMock()
        
        manager.delete('dolgozat1', 'test')
        self.assertTrue(manager.unsuccessful_deletion.emit.called)
        
    """ 
        Teszteljük, hogy a tesztek módosítás funkciója, a tesztek létezése mellett működik-e.
    """
    @patch('sqlite3.connect')
    def test_edit(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = (101,)
        result = ExerciseManager.edit('dolgozat1', 'test')
        self.assertEqual(result, (101,))
        
    """ 
        Teszteljük, hogy ha javítodolgozatot írunk, akkor updatelődik-e a dolgozateredmény.
    """  
    @patch('sqlite3.connect')
    def test_add_results_update(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.side_effect = [('nev1',), ('már meglévő dolgozat',)]
        ExerciseManager.add_results('test', 1, 'dolgozat', 1, 2)
        mock_cursor.execute.assert_any_call("UPDATE results SET score=? WHERE user_id=? AND exercise_id=? AND type=?", (2, 1, 1, 'test'))
        mock_conn.commit.assert_called_once()

    """ 
        Teszteljük, hogy ha új dolgozatírás esetén beszúrásra kerül-e a dolgozat eredménye. 
    """  
    @patch('sqlite3.connect')
    def test_add_results_insert(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.side_effect = [('nev1',), None]
        ExerciseManager.add_results('test', 1, 'dolgozat', 1, 2)
        mock_cursor.execute.assert_any_call("INSERT INTO results (user_name, user_id, type, test_name, exercise_id, score) VALUES (?, ?, ?, ?, ?, ?)", ('nev1', 1, 'test', 'dolgozat', 1, 2))
        mock_conn.commit.assert_called_once()

  
""" 
    Az ImageManager osztály tesztelése
"""
class TestImageManager(unittest.TestCase):

    """ 
        Teszteljük, hogy a program sikeresen visszaadja-e a képek elérési útját.
    """
    @patch('sqlite3.connect')
    def test_fetch_images_from_db(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchall.return_value = [(1, 'kep1.png'), (2, 'kep2.png')]
        result = ImageManager.fetch_images_from_db(1, 1)
        self.assertEqual(result, [(1, 'kep1.png'), (2, 'kep2.png')])


    """ 
        Teszteljük, hogy a program sikeresen beilleszti-e egy új kép adatait az adatbázisba.
    """
    @patch('sqlite3.connect')
    @patch('Modell.Logic.ImageManager.ImageManager.image_saved')
    def test_save_new_image_to_note(self, mock_image_saved, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = (2,)
        manager = ImageManager()
        manager.save_new_image_to_note('kep.png', 1, 1, 1, 'jegyzet_neve')
        mock_cursor.execute.assert_called_with("INSERT INTO note (user_id, note_id, subject_id, note_name, picture, image_id) VALUES (?, ?, ?, ?, ?, ?)",  (1, 1, 1, 'jegyzet_neve', 'kep.png', 3))
        mock_image_saved.emit.assert_called_once()

""" 
    Az SubjectManager osztály tesztelése
"""
class TestSubjectManager(unittest.TestCase):

    """ 
        Teszteljük, hogy a program sikeresen hozzátud adni-e az adatbázishoz egy megfelelő adatokkal rendelkező tantárgyat.
    """
    @patch('sqlite3.connect')
    def test_add_subject_success(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = None
        manager = SubjectManager()
        manager.subject_added_succesfully = MagicMock()
        manager.add_subject('Uj tantargy')
        mock_cursor.execute.assert_called_with("INSERT INTO subjects (subject_name) VALUES (?)", ('Uj tantargy',))
        manager.subject_added_succesfully.emit.assert_called_once()

    """ 
        Teszteljük, hogy a program helytelen tantárgynév esetén, azaz már létező tárgyat sikeresen nem ad-e hozzá az adatbázishoz.
    """
    @patch('sqlite3.connect')
    def test_add_subject_failure(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = True
        manager = SubjectManager()
        manager.subject_added_unsuccesfully = MagicMock()
        manager.add_subject('Letezo tantargy')
        manager.subject_added_unsuccesfully.emit.assert_called_once()

    """ 
        Teszteljük, hogy amennyiben egy tantárgyhoz tartoznak jegyzetek és rekurzívan kell törölni a hozzá tartozó jegyzeteket, azoknak a törlése megtörténik-e az adatbázisban.
    """
    @patch('sqlite3.connect')
    def test_remove_recursively_success(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        manager = SubjectManager()
        manager.subject_removed_succesfully = MagicMock()
        manager._SubjectManager__recursive_subject_id = 1
        manager.remove_recuresively()
        mock_cursor.execute.assert_any_call("DELETE FROM note WHERE subject_id = ?", (1,))
        mock_cursor.execute.assert_any_call("DELETE FROM subjects WHERE subject_id = ?", (1,))
        manager.subject_removed_succesfully.emit.assert_called_once()

    """ 
        Teszteljük, hogy megfelelő adatok esetén (még nem létező jegyzetnév), sikeresen hozzá tudunk-e adni jegyzetet az adatbázishoz.
    """
    @patch('sqlite3.connect')
    def test_add_note_success(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.side_effect = [None, (1,), (1,)]
        manager = SubjectManager()
        manager.note_added_succesfully = MagicMock()
        manager.add_note('Uj jegyzet', 1, 1)
        manager.note_added_succesfully.emit.assert_called_once()

    """ 
        Teszteljük, hogy nem megfelelő adatok esteén (már létező jegyzetnév), valóban nem történik-e meg a jegyzet hozzáadása az adatbázishoz.
    """
    @patch('sqlite3.connect')
    def test_add_note_failure(self, mock_connect):
        mock_conn = mock_connect.return_value
        mock_cursor = mock_conn.cursor.return_value
        mock_cursor.fetchone.return_value = True
        manager = SubjectManager()
        manager.note_added_unsuccesfully = MagicMock()
        manager.add_note('Letezo jegyzet', 1, 1)
        manager.note_added_unsuccesfully.emit.assert_called_once()


if __name__ == '__main__':
    app = QApplication(sys.argv)  
    unittest.main()
