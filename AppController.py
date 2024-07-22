import sys, os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from View.LoginWindow import LoginWindow
from View.MainMenuWindow import MainMenuWindow
from View.AdminMenuWindow import AdminMenuWindow
from Modell.UtilityModules.Exceptions import InvalidUserTitleException
from Modell.UtilityModules.Initializer import Initializer
from Modell.Logic.OCRUtils import OCRUtils

class AppController:
    """
    This class is responsible for the initialization of the Application and for handling windows.
    """

    # Construktor
    def __init__(self):
        """ Initialization of the app, setting icons"""
        # Private változók
        self.__app = QApplication(sys.argv)
        self.__app.setWindowIcon(QIcon("Assets/crayon_logo.png"))
        self.__login_window = LoginWindow(success_callback=self.__login_success)
        self.__ocr_utils =  OCRUtils()
        
    # Privately Accessable Methods

    def __login_success(self, user_role, user_id):
        """ Handling successfull login, displaying the corresponding username."""
        self.__user_role = user_role
        self.__user_id = user_id
        self.__show_main_menu()

    def __show_login_window(self):
        """ Displaying login window."""
        if hasattr(self, '__login_window') and self.__login_window:
            self.__login_window.show()
        else:
            self.__login_window = LoginWindow(success_callback=self.__login_success)
            self.__login_window.show()

    def __show_main_menu(self):
        """ Displaying main menu."""
        if self.__user_role == "Admin":
            if not hasattr(self, '__admin_menu') or not self.__admin_menu.isVisible():
                self.__admin_menu = AdminMenuWindow(back_to_login_callback=self.__show_login_window)
            self.__admin_menu.show()
        elif self.__user_role in ["Teacher", "Student"]:
            if not hasattr(self, '__main_menu') or not self.__main_menu.isVisible():
                self.__main_menu = MainMenuWindow(user_role=self.__user_role, user_id=self.__user_id, ocr_utils = self.__ocr_utils)
                if hasattr(self, "__default_geometry"):
                    self.__main_menu.setGeometry(self.__default_geometry)
                    self.__main_menu.show()
                else:
                    self.__main_menu.showMaximized()
            else:
                self.__main_menu.show()
        else:
            raise InvalidUserTitleException("Helytelen titulus.")
        
    # Publicly accessable methods

    def run(self):
        """ Running the application, checking the availablilty of the database and displaying the login window upon finding the database."""
        if os.path.exists("Persistence/database.db"):
            self.__login_window.show()
            self.__app.exec()
        else:
            self.__initializer = Initializer()
            self.__initializer.create_database()
            self.__admin_menu = AdminMenuWindow(self.__show_login_window)
            self.__admin_menu.show()
            self.__app.exec()
            
if __name__ == "__main__":
    controller = AppController()
    controller.run()
