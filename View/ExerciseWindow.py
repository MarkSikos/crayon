from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QScrollArea, QToolButton, QMessageBox, QSpacerItem, QSizePolicy, QFrame, QInputDialog
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
from PyQt6.QtCore import Qt, QSize
from abc import abstractmethod
from Modell.UtilityModules.FlowLayout import FlowLayout
from Modell.Logic.ExerciseManager import ExerciseManager
from View.ExerciseConfigWindow import ExerciseConfigWindow 
from Modell.UtilityModules.StyleSheetUtilities import StyleSheetUtilities
import datetime, re

MAX_BUTTON_HEIGHT = 40
CSS_PATH = 'Persistence/style/exercise_window_style.css'

class ExerciseWindow(QMainWindow):
    """
    The ExerciseWindow class is a base class for the test and homework window classes. 
    """
    
    # Constuctor
    
    def __init__(self, main_menu_callback=None, user_role=None, user_id=None):
        super().__init__()
        self._user_role = None
        self._user_id = None
        self._main_menu_callback = None
        self._theme_settings = None
        self._exercise_manager = ExerciseManager()
        self._exercise_manager.successful_deletion.connect(lambda: self._load(self.geometry()))
        self._exercise_manager.unsuccessful_deletion.connect(self.handle_unsuccesful_delete)
        self.setWindowTitle("Crayon")
        self.setAutoFillBackground(True)
        self._half_screen_width = QApplication.primaryScreen().size().width() // 2
        self._table = ""
        StyleSheetUtilities.load_stylesheet(self,CSS_PATH)
        
    # Creating the UI
    
    def _init_ui(self):
        """ Sets up the UI."""
        self._create_header()
        self._create_scroll_area()
        self._create_footer()
        
    def _create_header(self):
        """ Creates the header."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ECECE7"))
        self.setPalette(palette)
        self._header_layout = QHBoxLayout()
        title_label = QLabel("Feladatok")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 36, QFont.Weight.Bold)
        title_label.setStyleSheet("color: black;") # Nem lehet CSS-ben megtagelni, így egyszerűség kedvéért ideírtam
        title_label.setFont(title_font)
        self._header_layout.addWidget(title_label)
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._header_layout.addSpacerItem(spacer)
        self._header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum))
        back_button = QPushButton()
        back_button.setObjectName("backButton")
        back_button.setIcon(QIcon("Assets/back_icon.png"))
        back_button.clicked.connect(self._go_back)
        back_button.setIconSize(QSize(self._half_screen_width/20, self._half_screen_width/20))
        self._header_layout.addWidget(back_button)
    
    def _create_scroll_area(self):
        """ Create a ScrollArea. """
        self._scroll_area = QScrollArea(self)  
        self._scroll_area.setWidgetResizable(True) 
        self._central_widget = QWidget()  
        self._scroll_area.setWidget(self._central_widget)  
        self.setCentralWidget(self._scroll_area)  
        self._main_layout = QVBoxLayout(self._central_widget)
        self._main_layout.setContentsMargins(10, 10, 10, 10)  
        self._main_layout.setSpacing(10)  
        self._spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._main_layout.addSpacerItem(self._spacer)
        self._main_layout.addLayout(self._header_layout)
        horizontal_line = QFrame()
        horizontal_line.setFrameShape(QFrame.Shape.HLine)
        horizontal_line.setFrameShadow(QFrame.Shadow.Sunken)
        self._main_layout.addWidget(horizontal_line)
        self._flow_layout_widget = QWidget()
        self._flow_layout = FlowLayout()  
        self._flow_layout_widget.setLayout(self._flow_layout) 
        self._h_layout = QHBoxLayout()  
        self._load(self.geometry())
        self._h_layout.addWidget(self._flow_layout_widget)
        self._main_layout.addLayout(self._h_layout)
        
    def _create_footer(self):
        """ Create a footer for the teacher users taht includes the options for adding/deleting/modifying a test. """
        self._add_button = QToolButton()
        self._add_button.setText("Új teszt")
        self._add_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._add_button.clicked.connect(self._open_config)
        self._delete_button = QToolButton()
        self._delete_button.setText("Törlés")
        self._delete_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._delete_button.clicked.connect(self._delete)
        self._edit_button = QToolButton()
        self._edit_button.setText("Módosítás")
        self._edit_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self._edit_button.clicked.connect(self._edit)
        self._add_button.setObjectName("addButton")
        self._delete_button.setObjectName("deleteButton")
        self._edit_button.setObjectName("editButton")
        self._add_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._delete_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._edit_button.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self._add_button.setMaximumHeight(MAX_BUTTON_HEIGHT)
        self._delete_button.setMaximumHeight(MAX_BUTTON_HEIGHT)
        self._edit_button.setMaximumHeight(MAX_BUTTON_HEIGHT)
        self._footer_layout = QHBoxLayout()
        spacer_item = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self._main_layout.addSpacerItem(spacer_item)
        if self._user_role == 'Teacher':
            self._footer_layout.addWidget(self._add_button)
            self._footer_layout.addWidget(self._delete_button)
            self._footer_layout.addWidget(self._edit_button)
        self._main_layout.addLayout(self._footer_layout)
        
    def _populate_layout(self, data):
        """ Adds the elements to the scrollArea dinamycally. """
        screen = QApplication.primaryScreen().geometry()
        side_length = min(screen.width() / 4, screen.height() / 4)
        icon_side_length = side_length * 0.7 
        
        for row in data:
            if self._user_role == 'Teacher':
                user_id, test_id, username, test_name, test_date = row
                display_text = f"{test_name} ({test_date}) - {username}"
            else:
                test_id, user_id, test_name, test_date = row
                display_text = f"{test_name}"
                test_date = datetime.datetime.strptime(test_date, '%Y-%m-%d').date()
                if self._table == "homework":
                    if test_date <  datetime.date.today():
                        continue
                if self._table == "test" and test_date !=  datetime.date.today():
                    continue
            button = QToolButton()
            button.setText(display_text)
            button.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
            if self._user_role == 'Student':
                if self._table == "homework" :
                    button.setIcon(QIcon("Assets/hazi_feladatok_icon.svg"))
                else:
                    button.setIcon(QIcon("Assets/dolgozatok_icon.svg"))
                button.setIconSize(QSize(icon_side_length, icon_side_length))  
                button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            button.setObjectName("customButton")
            button.clicked.connect(lambda ch, t_id=test_id, t_name=test_name, user_role="Student", user_id=user_id: self._on_clicked(t_id, t_name, user_role, user_id))
            self._flow_layout.addWidget(button)

    # Eseménykezelő függvények 
       
    def _open_config(self):
        """ Opens the test configuration window"""
        geometry = self.geometry()
        if not hasattr(self,"_config_window") or not self._config_window.isVisible():
            self._config_window = ExerciseConfigWindow(refresh_callback= lambda geo = geometry :self._load(geo), user_id= self._user_id, exercise_type= self._exercise_config, geometry = geometry)
        self._config_window.show()
        self.close()
            
    def handle_unsuccesful_delete(self):
        """ Eventhandler of an unsuccesful deletion. """
        QMessageBox.warning(self,"Warning","Unsuccesfull deletion, invalid name.")
        
    def _go_back(self):
        """ Eventhandler for the back button. """
        geometry = self.geometry()
        if callable(self._main_menu_callback):
            self._main_menu_callback(geometry)
            self.close()

    # Functions, responsible for UI logic
    
    def _load(self, geometry):
        """ Loads the data from the database and updates the UI with the data gathered. """
        self._clear_layout()
        data =ExerciseManager.load_into_database(self._user_role,self._user_id, self._table)
        self._populate_layout(data)
        if not self.isVisible():
            if self.isMaximized() or self.isMinimized():
                self.showNormal() 
            self.setGeometry(geometry)
            self.show()
    
    def _delete(self):
        """ Deletes the selected test/homework from the database and refreshes the scrollArea. """
        test_name, ok = QInputDialog.getText(self, "Delete", "Please give the name of the test/homework to delete!")
        if ok and test_name:
            if len(test_name) > 40:
                QMessageBox.warning(self, "Warning", "The title of the test must not exceed 40 characters!")
                return
            if not self.__is_valid_text(test_name) :
                QMessageBox.warning(self, "Warning", "The title must only contain latin1 characters or numbers!")
                return
            self._exercise_manager.delete( test_name,self._table)
        else:
            if ok and not test_name:
                if self._table == "homework":
                    QMessageBox.warning(self, "Warning", "The homeworkname must not be empty.")
                else:
                    QMessageBox.warning(self, "Warning", "The name of the test must not be empty!")
              
    def _edit(self):
        """ Opens the test/homework editor window """
        test_name, ok = QInputDialog.getText(self, "Edit", "Type the name of the test/homework to edit!")
        if ok and test_name:
            if len(test_name) > 40:
                QMessageBox.warning(self, "Warning", "The title of the test must not exceed 40 characters!")
                return
            if not self.__is_valid_text(test_name) :
                QMessageBox.warning(self, "Warning", "The title must only contain latin1 characters or numbers!")
                return
            result = ExerciseManager.edit(test_name, self._table)
            if result:
                test_id = result[0]
                geometry= self.geometry()
                self._testConfigWindow = ExerciseConfigWindow(refresh_callback= lambda geo = geometry :self._load(geo), exercise_id=test_id, editing=True, geometry = geometry, user_id=self._user_id, exercise_type= self._exercise_config)
                self._testConfigWindow.load_existing_data()
                self._testConfigWindow.show()
                self.close()
            else:
                QMessageBox.warning(self, "Warning", "No test/homework exists under the given title.")
        else:
            if ok and not test_name:
                if self._table == "homework":
                    QMessageBox.warning(self, "Warning", "The name of the homework must not be empty.")
                else:
                    QMessageBox.warning(self, "Warning", "The name of the test must not be empty.")
                
    def _apply_theme_settings(self):
        """ Apply the style settings. """
        for button in self._buttons:
            button.setObjectName("commonButton")

    def _clear_layout(self):
        """ Clears all widgets from the scrollArea. Used to refresh the window. """
        while self._flow_layout.count():
            widget = self._flow_layout.itemAt(0).widget()
            if widget:
                self._flow_layout.removeWidget(widget)
                widget.deleteLater()
                
    def __is_valid_text(self,text):
        """ Helper function. Used to validate input."""
        alphabet = r'^[a-zA-Z0-9áéíóöőúüűÁÉÍÓÖŐÚÜ Ű]+$'
        return bool(re.match(alphabet, text))
                
    # Absztrakt függvények
        
    @abstractmethod
    def _on_clicked( self, test_id=None, test_name=None, user_role=None, user_id=None ):
        """ Abstract function, eventhandler of clicking. """
        raise NotImplementedError("Nem lett a függvény implementálva.")
            
            
    


    
    
    