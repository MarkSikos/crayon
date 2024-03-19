from PyQt6.QtWidgets import QApplication
from login import LoginWindow
from main_menu import MainMenu

class AppController:
    def __init__(self):
        self.app = QApplication([])
        self.login_window = LoginWindow(success_callback=self.show_main_menu)
        self.main_menu = None  # Placeholder for the main menu

    def show_main_menu(self):
        self.main_menu = MainMenu()
        self.main_menu.show()

    def run(self):
        self.login_window.show()
        self.app.exec()

if __name__ == "__main__":
    controller = AppController()
    controller.run()
