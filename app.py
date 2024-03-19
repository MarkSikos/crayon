from PyQt6.QtWidgets import QApplication
from UI.login import LoginWindow
from UI.main_menu import MainMenu
from UI.tanorak import TanorakWindow

class AppController:
    def __init__(self):
        self.app = QApplication([])
        self.login_window = LoginWindow(success_callback=self.show_main_menu)
        self.main_menu = MainMenu(show_tanorak_callback=self.show_tanorak)
        self.tanorak_window = TanorakWindow(show_main_menu_callback=self.show_main_menu)

    def show_main_menu(self):
        self.tanorak_window.hide()
        self.main_menu.show()

    def show_tanorak(self):
        self.main_menu.hide()
        self.tanorak_window.show()

    def run(self):
        self.login_window.show()
        self.app.exec()

if __name__ == "__main__":
    controller = AppController()
    controller.run()
