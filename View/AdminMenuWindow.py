from PyQt6.QtWidgets import QMainWindow,QApplication, QVBoxLayout, QPushButton, QLineEdit, QLabel, QWidget, QScrollArea, QHBoxLayout, QSpacerItem, QSizePolicy, QComboBox, QMessageBox
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, QSize
import re
from Modell.UtilityModules.AdminMenuWindowUtils import AdminMenuWindowUtils
from Modell.UtilityModules.StyleSheetUtilities import StyleSheetUtilities

CSS_PATH ="Persistence/style/admin_menu_style.css"

class AdminMenuWindow(QMainWindow):
    """
    This class is responsible for the administration window. It provides a GUI for user (and user data) management.
    """
    
    # Construktor

    def __init__(self, back_to_login_callback):
        super().__init__()
        self.__user_buttons = []
        self.__back_to_login_callback = back_to_login_callback
        self.__selected_user = None
        self.setWindowTitle("Crayon")
        self.__init_ui()
        self.__load_users()
        self.showMaximized()

    # UI Setup
    
    def __init_ui(self):
        """ Initializes the UI and loads the settings for the UI."""
        self.__half_screen_width = QApplication.primaryScreen().size().width() // 2
        StyleSheetUtilities.load_stylesheet(self, CSS_PATH)
        self.__central_widget = QWidget(self)
        self.setCentralWidget(self.__central_widget)
        layout = QVBoxLayout()
        self.__setup_header(layout)
        self.__setup_user_list(layout)
        self.__setup_user_management(layout)
        self.__central_widget.setLayout(layout)

    def __setup_header(self, layout):
        """ Sets teh header of the UI. """
        header_layout = QHBoxLayout()
        back_button = QPushButton()
        back_button.setIcon(QIcon("Assets/back_icon.png"))
        back_button.setIconSize(QSize(self.__half_screen_width/20, self.__half_screen_width/20))
        back_button.setObjectName("backButton")
        back_button.clicked.connect(self.__on_back_clicked)
        header_layout.addWidget(back_button)
        header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        title_label = QLabel("Adminisztrátori Ablak")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 24, QFont.Weight.Bold)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        header_layout.addSpacerItem(QSpacerItem(back_button.width(), 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(header_layout)

    def __setup_user_list(self, layout):
        """ Sets the user list. """
        self.__scroll_area = QScrollArea()
        self.__user_list_widget = QWidget()
        self.__user_list_layout = QVBoxLayout()
        self.__user_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.__user_list_widget.setLayout(self.__user_list_layout)
        self.__scroll_area.setWidgetResizable(True)
        self.__adminmenuwindow_utils = AdminMenuWindowUtils()
        self.__adminmenuwindow_utils.successfully_added_event.connect(self.__handle_succesful_adding)
        self.__adminmenuwindow_utils.unsuccesfully_added_event.connect(self.__handle_unsuccesful_adding)
        self.__adminmenuwindow_utils.no_teacher_event.connect(self.__no_teacher_handling)
        self.__scroll_area.setWidget(self.__user_list_widget)
        layout.addWidget(self.__scroll_area)

    def __setup_user_management(self, layout):
        """ Sets the user management gadget, text input areas and the add/delete buttons. """
        management_layout = QHBoxLayout()
        self.__username_input = QLineEdit()
        self.__username_input.setPlaceholderText("Felhasználóinév")
        self.__password_input = QLineEdit()
        self.__password_input.setPlaceholderText("Jelszó")
        self.__role_input = QComboBox()
        self.__role_input.addItems(["Admin", "Teacher", "Student"])
        self.__add_user_button = QPushButton("Hozzáadás")
        self.__add_user_button.setObjectName("addButton")
        self.__add_user_button.clicked.connect(self.__add_user)
        self.__delete_user_button = QPushButton("Törlés")
        self.__delete_user_button.setObjectName("deleteButton")
        self.__delete_user_button.clicked.connect(self.__delete_user)
        self.__delete_user_button.setEnabled(False)
        management_layout.addWidget(self.__username_input)
        management_layout.addWidget(self.__password_input)
        management_layout.addWidget(self.__role_input)
        management_layout.addWidget(self.__add_user_button)
        management_layout.addWidget(self.__delete_user_button)
        layout.addLayout(management_layout)

    # Functions for handling user interactions
    
    def __on_back_clicked(self):
        """ Handles return callback. """
        self.close()
        self.__back_to_login_callback()
    
    def __load_users(self):
        """ Loads/Relaoads the users. """
        users = AdminMenuWindowUtils.fetch_users()
        self.__update_user_list(users)

    def __update_user_list(self, users):
        """ Updates the user list. """
        self.__clear_layout()

        for username, role in users:
            user_layout = QHBoxLayout()
            user_button = QPushButton(username)
            user_button.setStyleSheet("QPushButton { text-align: left; padding: 5px; border-radius: 2px; border: 1px solid #000000; }  \
                                      QPushButton:checked { background-color: #d0d0d0; }")
            user_button.setCheckable(True)
            user_button.clicked.connect(lambda checked, username=username: self.__select_user(username))
            role_label = QLabel(role)
            role_label.setStyleSheet("QLabel { padding: 5px; border: 1px solid #000000; }")
            user_layout.addWidget(user_button)
            user_layout.addWidget(role_label)
            wrapper_widget = QWidget()
            wrapper_widget.setLayout(user_layout)
            self.__user_list_layout.addWidget(wrapper_widget)
            self.__user_buttons.append((user_button, username))
            
        self.__scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop)

    def __clear_layout(self):
        """ Deletes the records on the adminwindow. Used for the refresh mechanism."""
        self.__user_buttons.clear()
        while self.__user_list_layout.count():
            child = self.__user_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def __add_user(self):
        """ Adds a new user to the database and refreshes it """
        username = self.__username_input.text()
        password = self.__password_input.text()
        role = self.__role_input.currentText()
    
        if not username or not password or not role:
            QMessageBox.warning(self, "Warning", "All fields must be filled!")
            return
        if len(username) > 40:
            QMessageBox.warning(self, "Warning", "The length of the user name must not exceed 40 characters!")
            return
        if len(password) > 40:
            QMessageBox.warning(self, "Warning", "The length of the password must not exceed 40 characters!")
            return
        if (not self.__is_valid_text(username)) or (not self.__is_valid_text(password)):
            QMessageBox.warning(self, "Warning", "Invalid character. Only the characters in the latin1 alphabet and numbars may be entered.")
            return
        self.__adminmenuwindow_utils.add_user_db(username, password, role)

    def __delete_user(self):
        """ Deletes the user, and updates the database. """
        if not self.__selected_user:
            return
        self.__adminmenuwindow_utils.delete_user_db(self.__selected_user)
       
    def __select_user(self, username):
        """ Selects a user from the database and enables the deletion mechanism. """
        self.__selected_user = None if self.__selected_user == username else username
        self.__highlight_selected_user()
        self.__delete_user_button.setEnabled(bool(self.__selected_user))
        self.__update_delete_button_style()

    def __highlight_selected_user(self):
        """ Highlighting the selected user. """
        for button, username in self.__user_buttons:
            if username == self.__selected_user:
                button.setChecked(True)
            else:
                button.setChecked(False)

    def __update_delete_button_style(self):
        """ Refreshes the deletion button. """
        if self.__delete_user_button.isEnabled():
            self.__delete_user_button.setObjectName("deleteButtonEnabled")
        else:
            self.__delete_user_button.setObjectName("deleteButtonDisabled")
        StyleSheetUtilities.load_stylesheet(self, CSS_PATH)
        
    def __is_valid_text(self,text):
        """ Helper function. Decides whether the input is valid. """
        alphabet = r'^[a-zA-Z0-9áéíóöőúüűÁÉÍÓÖŐÚÜ Ű]+$'
        return bool(re.match(alphabet, text))
        
    # Eventhandlers
    
    def __handle_succesful_adding(self):
        """ Successful addition of a user """
        self.__load_users()
        self.__username_input.clear()
        self.__password_input.clear()
        self.__role_input.setCurrentIndex(0)
        
    def __handle_unsuccesful_adding(self):
        """ Unsuccesfull addition of a user. """
        QMessageBox.warning(self, "Warning", "Invalid Addition/Deletion!")
        
    def __no_teacher_handling(self):
        """ Unsuccesful addition of a student, when no teacher is present in the class. """
        QMessageBox.warning(self, "Warning", "Students must not be added to the class, until a new teacher is present!")
        

