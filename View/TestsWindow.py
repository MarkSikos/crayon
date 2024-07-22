from View.ExerciseWriter import ExerciseWriter
from View.ExerciseWindow import ExerciseWindow
from Modell.UtilityModules.Exercise import ExerciseConfig

class TestsWindow(ExerciseWindow):
    """
    Ez az osztály kezeli a teszt ablakot ahol a felhasználók kezelhetik a teszteket.
    Az Exercisewindow-ból származik.
    """
    
    # Konstruktor
    
    def __init__(self, main_menu_callback, user_role, user_id, geometry, ocr_utils ):
        super().__init__()
        self._user_role = user_role
        self._user_id = user_id
        self._main_menu_callback = main_menu_callback
        self._table = "test"
        self._buttons = []
        self._init_ui()
        self._exercise_config = ExerciseConfig.TEST
        self.setGeometry(geometry)
        self._ocr_utils = ocr_utils
        self.show()
        
    # Eseménykezelő és callback függvények
        
    def _show_test_window(self, geometry):
        """ Megjeleníti a teszt ablakot (ezt az ablakot). """
        if hasattr(self, 'test_writer_window') and self._test_writer_window.isVisible():
            self._test_writer_window.close()
        if self.isMaximized() or self.isMinimized():
            self.showNormal() 
        self.setGeometry(geometry)
        self.show()
    
    def _on_clicked(self, test_id, test_name, user_role, user_id ):
        """ A teszt elemre kattintva megnyitja az ExerciseWriter ablakot. """
        geometry = self.geometry()
        if not hasattr(self, "_test_writer_window") or not self._test_writer_window.isVisible():
            self._test_writer_window = ExerciseWriter(test_id=test_id, test_name=test_name, user_role=user_role, user_id= user_id, go_back_callback=lambda geo = geometry :  self._show_test_window(geo), exercise_type=self._exercise_config, geometry = geometry, ocr_utils = self._ocr_utils)
        self._test_writer_window.show()
        self.close()
    
        

    