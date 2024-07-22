from PyQt6.QtWidgets import QVBoxLayout, QWidget, QHBoxLayout, QInputDialog, QMessageBox
from View.ImageViewWindow import ImageViewWindow
from Modell.UtilityModules.StyleSheetUtilities import StyleSheetUtilities
from Modell.Logic.SubjectManager import SubjectManager
from View.ListWindow import ListWindow
import re

CSS_PATH = "Persistence/style/list_window_style.css"

class NoteWindow(ListWindow):
    """
    Az osztály a jegyzetek ablakot kezeli.
    """
    
    # Konstruktor

    def __init__(self, subject_id, user_role, user_id, subject_menu_callback, geometry, ocr_utils):
        super().__init__()
        self._subject_id = subject_id
        self._user_role = user_role
        self._user_id = user_id
        self._footer_layout = QHBoxLayout()
        self._subject_menu_callback = subject_menu_callback
        self._subject_manager = SubjectManager()
        self._subject_manager.note_deleted_succesfully.connect(lambda: self._populate(True))
        self._subject_manager.note_deleted_unsuccesfully.connect(self._handle_unsuccesfull_deletion)
        self._subject_manager.note_added_succesfully.connect(lambda: self._populate(True))
        self._subject_manager.note_added_unsuccesfully.connect(self._handle_unsuccesfull_addition)
        self.setWindowTitle(SubjectManager.get_subject_name(subject_id))
        self.__init_ui()
        self.setGeometry(geometry)
        self._ocr_utils = ocr_utils
        self.show()
        StyleSheetUtilities.load_stylesheet(self, CSS_PATH)

    def __init_ui(self):
        """ Felhasználói felület inicializálása. """
        self.setWindowTitle("Crayon")
        self._layout = QVBoxLayout()
        self._create_header("Jegyzetek")
        self._create_scroll_area()
        self._create_buttons(True, self._user_role)
        central_widget = QWidget()
        central_widget.setLayout(self._layout)
        self.setCentralWidget(central_widget)
        self._populate(True)
        
    # Fő funkcionalitásért felelős függvények

    def _add(self):
        """ Új jegyzet hozzáadását indító függvény. """
        name, ok = QInputDialog.getText(self, "Új jegyzet", "Jegyzet neve:")
        if ok and name:
            if not self.__is_valid_text(name):
                QMessageBox.warning(self, "Hiba", "A bemeneti mezőben csak a magyar ábécé betűi és számok szerepelhetnek.")
                return
            if len(name) > 40:
                QMessageBox.warning(self, "Hiba", "A jegyzet neve maxumum 40 karakter hosszú lehet.")
                return
            self._subject_manager.add_note(name,self._subject_id, self._user_id)
        else:
            if ok and not name:
                QMessageBox.warning(self, "Hiba", "A jegyzet neve nem maradhat üresen.")
            
    def _remove(self):
        """ Kiválasztott jegyzet törlését indító függvény. """
        name, ok = QInputDialog.getText(self, "Jegyzet törlése", "Jegyzet neve:")
        if ok and name:
            if not self.__is_valid_text(name):
                QMessageBox.warning(self, "Hiba", "A bemeneti mezőben csak a magyar ábécé betűi és számok szerepelhetnek.")
                return
            if len(name) > 40:
                QMessageBox.warning(self, "Hiba", "A tantárgy neve maxumum 40 karakter hosszú lehet.")
                return
            self._subject_manager.delete_note(name, self._subject_id, self._user_id)
        else:
            if ok and not name:
                QMessageBox.warning(self, "Hiba", "A jegyzet neve nem maradhat üresen.")
                
    def __is_valid_text(self,text):
        """ Segédfüggvény, eldönti hogy minden karakter magyar ábécén belüli-e, vagy szám."""
        alphabet = r'^[a-zA-Z0-9áéíóöőúüűÁÉÍÓÖŐÚÜ Ű]+$'
        return bool(re.match(alphabet, text))
            
    # Eseménykezelő függvények 
    
    def _handle_unsuccesfull_deletion(self):
        """ Sikertelen törlés eseménykezelője"""
        QMessageBox.critical(self,"Hiba", "A jegyzet nem található.")
           
    def _handle_unsuccesfull_addition(self):
        """Sikertelen hozzáadás eseménykezelője."""
        QMessageBox.warning(self, "Létező Jegyzet", "A tantárgyban már létezik jegyzet azonos névvel.")
 
    def __show_note_window(self, geometry):
        """ Jegyzetablaknak (ennek az ablaknak) a megjelenítése. """
        if hasattr(self, 'image_view_window') and self._image_view_window.isVisible():
            self._image_view_window.close()
        if self.isMaximized() or self.isMinimized():
            self.showNormal() 
        self.setGeometry(geometry)
        self.show()

    def _on_back_clicked(self):
        """ Visszalépés a főmenübe. """
        self._subject_menu_callback(self.geometry())
        self.close()
        
    def _on_folder_clicked(self, note_id):
        """ Jegyzet mappára kattintás eseménykezelője."""
        geometry = self.geometry()
        self._image_view_window = ImageViewWindow(note_id, self._subject_id, self._user_role, self._user_id, lambda geo = geometry :self.__show_note_window(geo), geometry, self._ocr_utils)
        self._image_view_window.show()
        self.close()

