from PyQt6.QtWidgets import QApplication, QVBoxLayout, QWidget, QToolButton,  QMessageBox, QScrollArea, QHBoxLayout, QLabel, QComboBox
from PyQt6.QtGui import  QGuiApplication, QIcon, QFont
from PyQt6.QtCore import Qt, QSize
from Modell.Logic.DrawingArea import DrawingArea  
from View.EditorWindow import EditorWindow
from Modell.Logic.ImageManager import ImageManager
from Modell.UtilityModules.StyleSheetUtilities import StyleSheetUtilities
from Modell.UtilityModules.ConfigUtils import ConfigUtils
from Modell.Logic.OCRUtils import OCRUtils

CSS_PATH = "Persistence/style/editor_window_style.css"
IMAGE_DIR = 'Persistence/image_dump'

class ImageViewWindow(EditorWindow):
    """
    Ez az osztály az kezeli a jegyzetszerkesztő ablakot.
    """
    
    # Konstruktor
    
    def __init__(self, note_id, subject_id, user_role, user_id, go_back_callback, geometry, ocr_utils):
        super().__init__(go_back_callback=go_back_callback)
        self._user_role = user_role
        self._user_id = user_id
        self._note_id = note_id
        self._subject_id = subject_id
        self._OCR = ocr_utils
        self._OCR.recognition_started.connect(self._update_label_title)
        self._saved = True
        self._note_name = ImageManager.get_note_name(note_id, user_id)
        self._title_label = self._note_name
        self._go_back_callback = go_back_callback
        self._drawing_areas = []
        self._bursh_size = 2
        self._eraser_size = 2
        self._half_screen_width = QApplication.primaryScreen().size().width() / 2
        self.__temp_image_path = None
        self.__image_manager = ImageManager()
        self._temp_drawing_area = None
        self.__init_ui()
        self._load_images()
        self.setGeometry(geometry)
        self.show()
        
    # Felhasználói felületet inicializáló függvények 
    
    def __init_ui(self):
        """ Setupolja az ablakot. """
        self.__image_manager.image_saved.connect(self.handle_image_saved)
        self.setWindowTitle("Crayon") 
        self._setup_central_widget()
        StyleSheetUtilities.load_stylesheet(self,CSS_PATH)
        self._add_title_label()        
        self._add_button = QToolButton()
        self._add_button.setIcon(QIcon("Assets/new_page_icon.png"))
        self._add_button.setIconSize(QSize(self._half_screen_width/20, self._half_screen_width/20))
        self._add_button.clicked.connect(self._add_new_png)
        self._check_button = QToolButton()
        self._check_button.setIcon(QIcon("Assets/check_icon.png"))
        self._check_button.setIconSize(QSize(self._half_screen_width/20, self._half_screen_width/20))
        self._check_button.clicked.connect(self._handle_ocr)     
        self._tool_selector = QComboBox()
        self._tool_selector.addItems(["Vonalak", "Pontok", "Üres"])
        self._tool_selector.setCurrentText("Üres")
        self._tool_selector.setWindowIcon(QIcon("Assets/selector.png"))
        self._tool_selector.setIconSize(QSize(self._half_screen_width/20, self._half_screen_width/20))
        self._tool_selector.setItemIcon(0,QIcon("Assets/lines.png"))
        self._tool_selector.setItemIcon(1,QIcon("Assets/dots.png"))
        self._tool_selector.setItemIcon(2,QIcon("Assets/empty.png"))
        self._tool_selector.currentTextChanged.connect(self._handle_drawing_mode_change)
        self._add_controls([self._tool_selector, self._add_button,self._check_button])
        self._add_scroll_area()
        
    def _add_scroll_area(self):
        """ Létrehozza és beállítja a Scrollareat. """
        self._layout = QHBoxLayout()
        self._scroll_area = QScrollArea()
        self._scroll_widget = QWidget()
        self._scroll_layout = QVBoxLayout(self._scroll_widget)
        self._scroll_area.setWidget(self._scroll_widget)
        self._scroll_area.setWidgetResizable(True)
        self._layout.addWidget(self._scroll_area)
        self._inner_layout = QVBoxLayout()
        self._result_label_title = QLabel("A kiértékelés státusza:")
        self._result_label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._result_label_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._inner_layout.addWidget(self._result_label_title)
        self._result_label = QLabel()
        self._result_label.setText("Nem kaptam még kiértékelendő szöveget.")
        self._inner_layout.addWidget(self._result_label)
        self._layout.addLayout(self._inner_layout)
        self._main_layout.addLayout(self._layout)

    # A fő funkcionalitásért felelő függvények
    
    def _update_ui_with_images(self, images):
        """ Frissíti a képeket. """
        result_label_text = self._result_label.text()
        self._clear_layout(self._scroll_layout)
        self._drawing_areas.clear()
        self._clear_layout(self._inner_layout)
        for image_id, image_path in images:
            drawing_area = DrawingArea(image_path, lambda path, image_id=image_id: self.__image_manager.save_new_image_to_note(path, self._note_id, self._user_id, self._subject_id, self._note_name, image_id), image_id)
            drawing_area.drawing_active.connect(lambda da=drawing_area: self._set_last_active_drawing_area(da))
            drawing_area.drawing_ended.connect(self._handle_image_edited)
            self._drawing_areas.append(drawing_area)
            if image_id != -1:
                self._scroll_layout.addWidget(drawing_area)
                spacer_widget = QWidget()
                spacer_widget.setFixedHeight(20)
                self._scroll_layout.addWidget(spacer_widget)
            else:
                self._evaluation_label = QLabel("Kiértékelő mező")
                self._evaluation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._evaluation_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
                self._inner_layout.addWidget(self._evaluation_label)
                self._inner_layout.addWidget(drawing_area)
                self._result_label = QLabel()
                self._result_label_title = QLabel("A kiértékelés státusza:")
                self._result_label_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self._result_label_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
                self._inner_layout.addWidget(self._result_label_title)
                self._result_label.setText(result_label_text)
                self._inner_layout.addWidget(self._result_label)
                self.__temp_image_path = image_path
                self._temp_drawing_area = drawing_area
        self.__set_tool_for_reload()

    def _load_images(self):
        """ Betölti a képeket az adatbázisból és frissíti a felhasználói felületet. """
        try:
            images = ImageManager.fetch_images_from_db(self._note_id, self._user_id)
            self._update_ui_with_images(images)
        except Exception as e:
            QMessageBox.critical(self, "Hiba", f"Hiba lépett fel a képek betöltésekor: {e}")

    def _save_all_drawings(self):
        """ Mentési műveletet indít az összes DrawingArea-n. """
        for drawing_area in self._drawing_areas:
            drawing_area.save_changes()
            
    def _add_new_png(self):
        """ Új .png kép létrehozását indítja el. """
        self._save_all_drawings()
        screen = QGuiApplication.primaryScreen().geometry()
        image_path = ConfigUtils.create_and_save_big_image(screen.width(), screen.height())
        self.__image_manager.save_new_image_to_note(image_path, self._note_id, self._user_id, self._subject_id, self._note_name, None)
        self._load_images()
        self._handle_drawing_mode_change( )
        
    def _handle_ocr(self):
        
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        QApplication.processEvents()
        self._check_manager()
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        

    def _check_manager(self):
        
        """Az OCR-el kapcsolatos feladatokért felel. """
        self._temp_drawing_area.save_changes() 
        result_text = f"Nem sikerült értlemeznem a szöveget."
        result = self._OCR.recognize_text([self.__temp_image_path])
        flattened = self.__flatten(result)
        if None in flattened:
            result_text = f"Nem sikerült értlemeznem a szöveget."
        else:
            elements = ", ".join(str(item) for item in flattened)
            result_text = f"Az általam készített ajánlás: "+ elements
        self._result_label.setText(result_text)
        
    def __flatten(self,nested_list):
        """A _check_manager segédfüggvénye. Regkurzívan flattenel egy listát."""
        flattened_list = []
        for item in nested_list:
            if isinstance(item, list):
                flattened_list.extend(self.__flatten(item))
            else:
                flattened_list.append(item)
        return flattened_list
    
    def __set_tool_for_reload(self):
        """ Beállítja az összes DrawingArea jelenlegi eszközét. """
        tool = self._get_current_tool()
        for drawing_area in self._drawing_areas:
            drawing_area.set_tool(tool)
        if tool == 'brush':
            for drawing_area in self._drawing_areas:
                drawing_area.adjust_tool_size(self._bursh_size)
            self._tool_size_slider.setValue(self._bursh_size)
        elif tool == 'eraser':
            self._tool_size_slider.setValue(self._eraser_size)
            for drawing_area in self._drawing_areas:
                drawing_area.adjust_tool_size(self._eraser_size)
        if self._current_color.isValid():
            for drawing_area in self._drawing_areas:
                drawing_area.set_brush_color(self._current_color)
                drawing_area.update()  
     
    # Eseménykezelő függvények
    
    def handle_image_saved(self):
        """ Egy sikeres képmentés eseménykezelője. """
        self._saved = True
        
    def _handle_image_edited(self):
        """ Egy kép szerkesztésének eseménykezelője (azaz beállítja hogy még nincsen elmentve). """
        self._saved = False
        
    def _handle_drawing_mode_change(self):
        """ A háttér mód megváltozásának eseménykezelője. """
        mode = self._tool_selector.currentText()
        for drawing_area in self._drawing_areas:
            if drawing_area.get_image_id() != -1:
                drawing_area.set_drawing_mode(mode)
               
    def closeEvent(self, event):
        """A closeEvent felüldefiniálása, ezáltal megakadályozzuk hogy mentés nélkül kilépjünk. """
        if not self._saved:
            reply = QMessageBox.question(self, 'Mentés', "El akarja menteni a változásokat a jegyzetben?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self._save_all_drawings()
                event.accept()  
            elif reply == QMessageBox.StandardButton.No:
                event.accept()  
            else:
                event.ignore()
        else:
            event.accept()
            
    def _update_label_title(self):
        """ A visszajelzési labelt beállító eseménykezelő. """
        self._result_label.setText("A kiértékelés folyamatban van")
        
          
        