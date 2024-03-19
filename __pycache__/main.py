# File path: /path/to/your/improved_pyqt_app.py

import sqlite3
from PyQt6.QtWidgets import QApplication, QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt
from utility_modules.password_handling import check_password  # Import the check_password function


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crayon")
        self.setGeometry(100, 100, 280, 150)  # Adjust the size as needed

        # Set the font to be used in the widgets
        font = QFont("Arial", 10)
        font.setBold(True)

        # Set the application's palette for the background color
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#87CEEB"))
        self.setPalette(palette)

        # Central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Title label inside a white rectangle
        title_label = QLabel("Crayon")
        title_label.setFont(QFont("Arial", 16, weight=QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("background-color: white; padding: 10px;")
        layout.addWidget(title_label)

        # Username input
        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("Felhasználói név")
        self.username_input.setFont(font)
        layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("Jelszó")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFont(font)
        layout.addWidget(self.password_input)

        # Login button with a nicer style
        login_button = QPushButton("Login", self)
        login_button.setFont(font)
        login_button.setStyleSheet("background-color: #FFFFFF; color: #000000; padding: 5px;")
        login_button.clicked.connect(self.on_login_clicked)
        layout.addWidget(login_button)

        # Adjust layout spacing
        layout.setSpacing(10)

    def on_login_clicked(self):
        username = self.username_input.text()
        provided_password = self.password_input.text()

        # Connect to the SQLite database
        conn = sqlite3.connect('database/users.db')  # Update the path to your actual users.db file
        cursor = conn.cursor()

        # Retrieve the user's hashed password from the database
        cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
        result = cursor.fetchone()

        if result:
            stored_password_hash = result[0]
            # No need to encode provided_password again as it's already a string that will be encoded in check_password
            if check_password(stored_password_hash, provided_password):
                print(f"Login successful for username: {username}")
                # Here you can proceed with opening the next window or session
            else:
                print("Login failed: Incorrect password.")
        else:
            print("Login failed: Username does not exist.")

        conn.close()

if __name__ == "__main__":
    app = QApplication([])
    login_window = LoginWindow()
    login_window.showMaximized()  # Show the window maximized by default
    app.exec()
