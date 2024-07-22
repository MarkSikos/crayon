from PyQt6.QtWidgets import QMainWindow, QLineEdit, QVBoxLayout, QWidget, QLabel, QApplication, QHBoxLayout, QToolButton, QMessageBox
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap
from PyQt6.QtCore import Qt
import re
from Modell.UtilityModules.PasswordHandler import PasswordHandler
from Modell.UtilityModules.StyleSheetUtilities import StyleSheetUtilities
CSS_PATH = "Persistence/style/login_window_style_sheet.css"

class LoginWindow(QMainWindow):
    """
    A Login ablakot megvalósító osztály.
    """
    
    # Konstruktor
    
    def __init__(self, success_callback=None):
        super().__init__()
        self.__success_callback = success_callback
        self.__screen = QApplication.primaryScreen().geometry()
        self.__init_ui()
        self.__input_password = None
        self.__input_username = None
        self.__password_handler = PasswordHandler()
        self.__password_handler.successful_login.connect(self.__handle_succesfull_login)
        self.__password_handler.unsuccessful_login.connect(self.__handle_unsuccesfull_login)
        self.__center_on_screen()
        
    # UI inicializáló függvények
        
    def __init_ui(self):
        """ A felhasználói felület elemeit beállító föggvény. """
        self.setWindowTitle("Crayon")
        StyleSheetUtilities.load_stylesheet(self, CSS_PATH)
        self.__configure_window()
        self.__setup_central_widget()
        self.__setup_logo()
        self.__setup_user_inputs()
        self.__setup_login_button()
        
    def __configure_window(self):
        """ Az ablak alapbeállításait beállító függvény. """
        self.setGeometry(0, 0, self.__screen.width()*0.2, self.__screen.height()*0.4)
        self.setFixedSize(self.width(), self.height())
        self.__apply_palette()

    def __apply_palette(self):
        """ A színpalettát alkalmazzó függvény. """
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ECECE7"))
        self.setPalette(palette)

    def __setup_central_widget(self):
        """ A central widgetet beállító függvény. """
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        self.__layout = QVBoxLayout(central_widget)
        self.__layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def __setup_logo(self):
        """ A logót konfiguráló függvény. """
        logo_label = QLabel(self)
        logo_pixmap = QPixmap('Assets/logo_removed.png')
        logo_label.setPixmap(logo_pixmap.scaledToWidth(self.width() * 0.8, Qt.TransformationMode.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.__layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignTop)

    def __setup_user_inputs(self):
        """ A felhasználói bemenetek (felhasználónév és jelszó) mezőit állítja be. """
        font = QFont("Segoe UI", 10)
        self.__setup_username_input(font)
        self.__setup_password_input(font)

    def __setup_username_input(self, font):
        """ A felhasználónév beviteli mezőjét állítja be. """
        self.__username_input = QLineEdit()
        self.__username_input.setPlaceholderText("Felhasználónév")
        self.__username_input.setFont(font)
        self.__username_input.setFixedWidth(self.__screen.width() * 0.15)
        username_layout = QHBoxLayout()
        username_icon_label = QLabel(self)
        username_icon_label.setPixmap(QPixmap('Assets/username_light.png').scaledToHeight(20))
        username_layout.addWidget(username_icon_label)
        username_layout.addWidget(self.__username_input)
        self.__layout.addLayout(username_layout)

    def __setup_password_input(self, font):
        """ A jelszó beviteli mezőjét állítja be. """
        self.__password_input = QLineEdit()
        self.__password_input.setPlaceholderText("Jelszó")
        self.__password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.__password_input.setFont(font)
        self.__password_input.setFixedWidth(self.__screen.width() * 0.15)
        password_layout = QHBoxLayout()
        password_icon_label = QLabel(self)
        password_icon_label.setPixmap(QPixmap('Assets/password_light.png').scaledToHeight(20))
        password_layout.addWidget(password_icon_label)
        password_layout.addWidget(self.__password_input)
        self.__layout.addLayout(password_layout)

    def __setup_login_button(self):
        """ A bejelentkezés gombot állítja be. """
        login_button = QToolButton()
        login_button.setText("Belépés")
        login_button.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        login_button.setFixedWidth(self.__screen.width() * 0.18)
        login_button.clicked.connect(self.__on_login_clicked)
        self.__username_input.returnPressed.connect(self.__on_login_clicked)
        self.__password_input.returnPressed.connect(self.__on_login_clicked)
        button_layout = QHBoxLayout()
        button_layout.addStretch(25)
        button_layout.addWidget(login_button)
        button_layout.addStretch()
        self.__layout.addLayout(button_layout)
        self.__layout.setSpacing(10)

    def __center_on_screen(self):
        """ Az ablakot a képernyő közepére helyezi. """
        windowWidth = self.__screen.width() * 0.2
        windowHeight = self.__screen.height() * 0.4
        centerX = (self.__screen.width() - windowWidth) // 2
        centerY = (self.__screen.height() - windowHeight) // 2
        self.setGeometry(centerX, centerY, windowWidth, windowHeight)
        
    def __is_valid_text(self,text):
        """ Segédfüggvény, eldönti hogy minden karakter magyar ábécén belüli-e, vagy szám."""
        alphabet = r'^[a-zA-Z0-9áéíóöőúüűÁÉÍÓÖŐÚÜ Ű]+$'
        return bool(re.match(alphabet, text))

    # Eseménykezelő függvények
    
    def __on_login_clicked(self):
        """ A bejelentkezés gomb eseménykezelője. """
        self.__input_username = self.__username_input.text()
        self.__input_password  = self.__password_input.text()
        if (self.__input_password and self.__input_username) and ((not self.__is_valid_text(self.__input_username)) or (not self.__is_valid_text(self.__input_password))):
            QMessageBox.warning(self, "Hiba", "A bemeneti mezőben csak a magyar ábécé betűi és számok szerepelhetnek.")
            return
        if self.__input_username and self.__input_password:
            if len(self.__input_username) > 40 or len(self.__input_password) > 40:
                QMessageBox.warning(self, "Hiba", "A bemeneti mezőben 40 karakter hosszú szöveg szerepelhet.")
                return
        self.__password_handler.login(self.__input_username, self.__input_password)
                   
    def __handle_succesfull_login(self):
        """Egy sikeres bejelentkezés eseménykezelője."""
        res = self.__password_handler.fetch_user_data(self.__input_username)
        self.__success_callback(res[2], res[1])
        self.close()
            
    def __handle_unsuccesfull_login(self):
        """Egy sikertelen bejelentkezés eseménykezelője."""
        self.__password_input.setStyleSheet("QLineEdit { background-color: #FFF0F0; }")
        self.__username_input.setStyleSheet("QLineEdit { background-color: #FFF0F0; }")
        
        
    
    
            
