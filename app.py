import sys
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon
from UI.login import LoginWindow
from UI.main_menu import MainMenu
from UI.tanorak import TanorakWindow

class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setWindowIcon(QIcon("assets/crayon_logo.png"))
        self.setupTrayIcon()
        self.login_window = LoginWindow(success_callback=self.show_main_menu)

    def setupTrayIcon(self):
        self.tray_icon = QSystemTrayIcon(QIcon('assets/crayon_logo_32x32.png'), self.app)
        tray_menu = QMenu()
        exit_action = tray_menu.addAction("Exit")
        exit_action.triggered.connect(self.app.quit)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def show_main_menu(self):
        self.main_menu = MainMenu(show_tanorak_callback=self.show_tanorak)
        self.main_menu.show()

    def show_tanorak(self):
        self.tanorak_window = TanorakWindow(show_main_menu_callback=self.show_main_menu)
        self.tanorak_window.show()

    def run(self):
        self.login_window.show()
        self.app.exec()
        
        
if __name__ == "__main__":
    controller = AppController()
    controller.run()
