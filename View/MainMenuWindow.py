from PyQt6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, QToolButton, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import Qt, QSize
from Modell.UtilityModules.FlowLayout import FlowLayout
from View.HomeWorksWindow import HomeWorksWindow
from View.SubjectWindow import SubjectWindow
from View.TestsWindow import TestsWindow
from Modell.UtilityModules.StyleSheetUtilities import StyleSheetUtilities
from View.DashboardWindow import DashboardWindow
from PyQt6.QtCore import QObject, pyqtSignal, QRect

CSS_PATH = "Persistence/style/main_menu_style.css"

class MainMenuWindow(QMainWindow):
    """
    Ez az osztály kezeli a főmenü felhasználói felületét.
    """
    
    # Konstruktor

    def __init__(self, user_role, user_id, ocr_utils=None):
            super().__init__()
            self.__user_role = user_role
            self.__screen = QApplication.primaryScreen().geometry()
            self.__user_id = user_id
            self.__buttons = []
            self.__ocr_utils = ocr_utils
            self.__init_ui()
    
    # Felület inicializálására szolgáló függvények
    
    def __init_ui(self):
        """ Setupolja a felhasználói felületet."""
        self.setWindowTitle("Crayon")
        StyleSheetUtilities.load_stylesheet(self, CSS_PATH)
        self.setAutoFillBackground(True)
        self.__setup_layouts()
        self.__setup_buttons()
        self.__add_layout_spacers()

    def __setup_layouts(self):
        """ Beállítja a scroll area-t és a központi widgetet. """
        self.__scroll_area = QScrollArea(self)
        self.__scroll_area.setWidgetResizable(True)
        self.__central_widget = QWidget()
        self.__scroll_area.setWidget(self.__central_widget)
        self.setCentralWidget(self.__scroll_area)
        self.__main_layout = QVBoxLayout(self.__central_widget)
        self.__main_layout.setContentsMargins(10, 10, 10, 10)
        self.__main_layout.setSpacing(10)
        self.__h_layout = QHBoxLayout()
        self.__flow_layout_widget = QWidget()
        self.__flow_layout = FlowLayout(self.__flow_layout_widget)
        self.__h_layout.addWidget(self.__flow_layout_widget)
        self.__main_layout.addLayout(self.__h_layout)

    def __setup_buttons(self):
        """ Inicializálja, és beállítja a gombokat"""
        side_length = min(self.__screen.width() / 3, self.__screen.height() / 3)
        button_size = QSize(side_length, side_length) 
        icon_side_length = side_length * 0.7 
        subjects_button = QToolButton()
        subjects_button.setText("Tanórák")
        subjects_button.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        subjects_button.setIcon(QIcon("Assets/tanorak_icon.svg"))
        subjects_button.setIconSize(QSize(icon_side_length, icon_side_length))  
        subjects_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        subjects_button.clicked.connect(self.__show_subjects_window)
        subjects_button.setFixedSize(button_size)
        self.__flow_layout.addWidget(subjects_button)
        self.__buttons.append(subjects_button)
        tests_button = QToolButton()
        tests_button.setText("Dolgozatok")
        tests_button.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        tests_button.setIcon(QIcon("Assets/dolgozatok_icon.svg"))
        tests_button.setIconSize(QSize(icon_side_length, icon_side_length))  
        tests_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        tests_button.clicked.connect(self.__show_tests_window)
        tests_button.setFixedSize(button_size)
        self.__flow_layout.addWidget(tests_button)
        self.__buttons.append(tests_button)
        homeworks_button = QToolButton()
        homeworks_button.setText("Házi Feladatok")
        homeworks_button.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        homeworks_button.setIcon(QIcon("Assets/hazi_feladatok_icon.svg"))
        homeworks_button.setIconSize(QSize(icon_side_length, icon_side_length))  
        homeworks_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        homeworks_button.clicked.connect(self.__show_homeworks_window)
        homeworks_button.setFixedSize(button_size)
        self.__flow_layout.addWidget(homeworks_button)
        self.__buttons.append(homeworks_button)
        
        if self.__user_role == "Teacher":
            dashboard_button = QToolButton()
            dashboard_button.setText("Eredmények")
            dashboard_button.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            dashboard_button.setIcon(QIcon("Assets/eredmenyek_icon.svg"))
            dashboard_button.setIconSize(QSize(icon_side_length, icon_side_length))  
            dashboard_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            dashboard_button.clicked.connect(self.__show_dashboard_window)
            dashboard_button.setFixedSize(button_size)
            self.__flow_layout.addWidget(dashboard_button)
            self.__buttons.append(dashboard_button)
        exit_button = QToolButton()
        exit_button.setText("Kilépés")
        exit_button.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        exit_button.setIcon(QIcon("Assets/exit_icon.svg"))
        exit_button.setIconSize(QSize(icon_side_length, icon_side_length))   
        exit_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        exit_button.clicked.connect(self.close)
        exit_button.setFixedSize(button_size)
        self.__flow_layout.addWidget(exit_button)
        self.__buttons.append(exit_button)

    def __add_layout_spacers(self):
        """ Térközöket ad hozzá a layoutokhoz az esztétikus megjelenés érdekében. """
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.__main_layout.addSpacerItem(spacer)
        self.__h_layout.addSpacerItem(spacer)
        self.__main_layout.addLayout(self.__h_layout)
        self.__main_layout.addSpacerItem(spacer)

    # Eseménykezelő függvények
    
    def __show_subjects_window(self):
        """ Tantárgyak menüre való kattintás eseménykezelője"""
        if not hasattr(self, 'subject_window') or not self.__subject_window.isVisible():
            geometry = self.geometry()
            self.__subject_window = SubjectWindow(show_main_menu_callback= lambda geo =geometry: self.__show_main_menu(geo), user_role=self.__user_role, user_id=self.__user_id, geometry = geometry, ocr_utils = self.__ocr_utils)
        self.__subject_window.show()
        self.close()

    def __show_tests_window(self):
        """ Tesztek menüre való kattintás eseménykezelője"""
        if not hasattr(self, 'tests_window') or not self.__tests_window.isVisible():
            geometry = self.geometry()
            self.__tests_window = TestsWindow(main_menu_callback= lambda geo = geometry:self.__show_main_menu_tests(geo), user_role=self.__user_role, user_id=self.__user_id, geometry = geometry, ocr_utils = self.__ocr_utils)
        self.__tests_window.show()
        self.close()

    def __show_homeworks_window(self):
        """ Házi feladatok menüre való kattintás eseménykezelője"""
        if not hasattr(self, '__homework_window') or not self.__homework_window.isVisible():
            geometry = self.geometry()
            self.__homework_window = HomeWorksWindow(main_menu_callback= lambda geo = geometry:self.__show_main_menu_homework(geo), user_role=self.__user_role, user_id=self.__user_id,geometry = geometry, ocr_utils = self.__ocr_utils)
        self.__homework_window.show()
        self.close()

    def __show_dashboard_window(self):
        """ Tanári dashboard menüre való kattintás eseménykezelője"""
        if not hasattr(self, '__dashboard_window') or not self.__dashboard_window.isVisible():
            geometry = self.geometry()
            self.__dashboard_window = DashboardWindow(main_menu_callback= lambda geo = geometry : self.__show_main_menu_dashboard(geo), user_id=self.__user_id, geometry = geometry)
        self.__dashboard_window.show()
        self.close()

    # Callback függvények
    
    def __show_main_menu(self, geometry):
        """ Tantárgyak menüből való visszatérés callback-je."""
        if hasattr(self, '__subject_window') and self.__subject_window.isVisible():
            self.__subject_window.close()
        if self.isMaximized() or self.isMinimized():
            self.showNormal() 
        self.setGeometry(geometry)
        self.show()
        
    def __show_main_menu_tests(self, geometry):
        """ Teszt menüből való visszatérés callback-je."""
        if hasattr(self, '__tests_window') and self.__tests_window.isVisible():
            self.__tests_window.close()
        if self.isMaximized() or self.isMinimized():
            self.showNormal() 
        self.setGeometry(geometry)
        self.show()

    def __show_main_menu_homework(self, geometry):
        """ Házi feladatok menüből való visszatérés callback-je."""
        if hasattr(self, '__homework_window') and self.__homework_window.isVisible():
            self.__homework_window.close()
        if self.isMaximized() or self.isMinimized():
            self.showNormal() 
        self.setGeometry(geometry)
        self.show()
        
    def __show_main_menu_dashboard(self, geometry):
        """ Tanári dashboard menüből való visszatérés callback-je."""
        if hasattr(self, '__dashboard_window') and self.__dashboard_window.isVisible():
            self.__dashboard_window.close()
        if self.isMaximized() or self.isMinimized():
            self.showNormal() 
        self.setGeometry(geometry)
        self.show()
        
   
