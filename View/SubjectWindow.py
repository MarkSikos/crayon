
from PyQt6.QtWidgets import   QInputDialog, QMessageBox
import re
from .NoteWindow import NoteWindow
from Modell.UtilityModules.StyleSheetUtilities import StyleSheetUtilities
from Modell.Logic.SubjectManager import SubjectManager
from View.ListWindow import ListWindow

CSS_PATH = "Persistence/style/list_window_style.css"

class SubjectWindow(ListWindow):
    """
    A SubjectWindow osztály kezeli a tantárgyak megjelenítésére és kezelésére szolgáló felhasználói felületet.
    """
    
    # Konstruktor
    
    def __init__(self, show_main_menu_callback, user_role, user_id, geometry, ocr_utils):
        super().__init__()
        self._show_main_menu_callback = show_main_menu_callback
        self._user_role = user_role
        self._user_id = user_id
        self._input_subject_name = None
        self._subject_manager = SubjectManager()
        self._subject_manager.subject_added_succesfully.connect(lambda: self._populate(False))
        self._subject_manager.subject_added_unsuccesfully.connect(self._handle_unsuccessful_subject_adding)
        self._subject_manager.subject_removed_succesfully.connect(lambda: self._populate(False))
        self._subject_manager.subject_removed_unsuccesfully.connect(self._handle_unsuccesful_removal)
        self._subject_manager.subject_removal_recursively.connect(self._handle_subject_removal_recursively)
        self.__init_ui()
        StyleSheetUtilities.load_stylesheet(self, CSS_PATH)
        self.setGeometry(geometry)
        self._ocr_utils = ocr_utils

    def __init_ui(self):
        """ Setupolja a felhasználói felületet. """
        self.setWindowTitle("Crayon") 
        self._create_header("Tantárgyak")
        self._create_scroll_area()
        self._create_buttons(False, self._user_role)
        self._populate(False)

    # Fő funkcionalitásért felelős függvények
    
    def _add(self):
        """ Új tantárgy hozzáadását indító függvény. """
        name, ok = QInputDialog.getText(self, "Új tantárgy", "Tantárgy neve:")
        if ok and name:
            if not self.__is_valid_text(name):
                QMessageBox.warning(self, "Hiba", "A bemeneti mezőben csak a magyar ábécé betűi és számok szerepelhetnek.")
                return
            if len(name) > 40:
                QMessageBox.warning(self, "Hiba", "A tantárgy neve maxumum 40 karakter hosszú lehet.")
                return
            self._subject_manager.add_subject(name)
        else:
            if ok and not name:
                QMessageBox.warning(self, "Hiba", "A tantárgy neve nem maradhat üresen.")
            
            
    def _remove(self):
        """ Tantárgy eltávolításának elindításáért felelős függvény.  """
        subject_name, ok = QInputDialog.getText(self, "Tantárgy eltávolítása", "Adja meg a tantárgy nevét:")
        if ok and subject_name:
            if not self.__is_valid_text(subject_name):
                QMessageBox.warning(self, "Hiba", "A bemeneti mezőben csak a magyar ábécé betűi és számok szerepelhetnek.")
                return
            if len(subject_name) > 40:
                QMessageBox.warning(self, "Hiba", "A tantárgy neve maxumum 40 karakter hosszú lehet.")
                return
            self._subject_manager.remove_subject(subject_name, )
            self._input_subject_name = subject_name
        else:
            if ok and not subject_name:
                QMessageBox.warning(self, "Hiba", "A tantárgy neve nem maradhat üresen.")
                
    def __is_valid_text(self,text):
        """ Segédfüggvény, eldönti hogy minden karakter magyar ábécén belüli-e, vagy szám."""
        alphabet = r'^[a-zA-Z0-9áéíóöőúüűÁÉÍÓÖŐÚÜŰ ]+$'
        return bool(re.match(alphabet, text))
    
    # Eseménykezelő függvények
    
    def _handle_subject_removal_recursively(self):
        """ Rekurzív törlés eseménykezelője. """
        reply = QMessageBox.question(self, "Rekurzív törlés", "Léteznek a tantárgyhoz kapcsolódó jegyzetek. Akarja rekurzívan törölni a tárgyhoz tartozó összes jegyzetet?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self._subject_manager.remove_recuresively()
            
    def _handle_unsuccessful_subject_adding(self):
        """ Sikertelen hozzáadás eseménykezelője"""
        QMessageBox.warning(self, "Hiba", "A tantárgy már létezik.")
                
    def _handle_unsuccesful_removal(self):
        """ Sikertelen eltávolítás eseménykezelője. """
        QMessageBox.warning(self, "Hiba","Nem létezik tantárgy ilyen névvel.")   

    def _on_subject_clicked(self, subject_id):
        """ Egy tantárgy kiválasztása esetén a NoteWindow ablak megnyitása. """
        self.close()
        geometry = self.geometry()
        self.__note_window = NoteWindow(subject_id, self._user_role, self._user_id, lambda geo = geometry: self._show_subject_window(geo), geometry, self._ocr_utils)
        self.__note_window.show()

    def _show_subject_window(self, geometry):
        """ Ennek az ablaknak az újramegjelenítése. """
        if hasattr(self, '__note_window') and self.__note_window.isVisible():
            self.__note_window.close()
        if self.isMaximized() or self.isMinimized():
            self.showNormal() 
        self.setGeometry(geometry)
        self.show()

    def _on_back_clicked(self):
        """ Vissza gombra kattintva visszatérés az előző menübe. """
        if callable(self._show_main_menu_callback):
            self._show_main_menu_callback(self.geometry())
            self.close()
        
