from PyQt6.QtWidgets import QApplication
from UI.login import LoginWindow
from UI.main_menu import MainMenu
from UI.tanorak import TanorakWindow

class AppController:
    def __init__(self):
        self.app = QApplication([])
        self.login_window = LoginWindow(success_callback=self.show_main_menu)
        #self.main_menu = None  # Placeholder for the main menu
        self.main_menu = MainMenu()
        self.tanorak_window = TanorakWindow()
        # Connect the TanorakWindow's go_back_signal to the show_main_menu method
        self.tanorak_window.go_back_signal.connect(self.show_main_menu)


    def show_main_menu(self):
        #self.main_menu = MainMenu()
        #self.main_menu.show()
        if self.tanorak_window.isVisible():
            self.tanorak_window.hide()
        self.main_menu.show()

    def run(self):
        self.login_window.show()
        self.app.exec()

if __name__ == "__main__":
    controller = AppController()
    controller.run()
