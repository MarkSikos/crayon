# File path: /path/to/your/login.py

import sqlite3
from PyQt6.QtWidgets import QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel, QGraphicsOpacityEffect, QApplication, QGraphicsDropShadowEffect
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from utility_modules.password_handling import check_password  # Adjust this import path as necessary
class LoginWindow(QMainWindow):
    def __init__(self, success_callback=None):
        super().__init__()
        self.success_callback = success_callback

        # Get the screen size
        screen = QApplication.primaryScreen().geometry()
        screenWidth = screen.width()
        screenHeight = screen.height()

        # Set the window size to match the screen size
        self.setGeometry(0, 0, screenWidth*0.2, screenHeight*0.4)

        self.setWindowTitle("Belépés")

        # Set the font to be used in the widgets
        font = QFont("Lucida", 12)

        # Set the application's palette for the background color
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#87CEEB"))
        self.setPalette(palette)

        # Set central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Felhasználói név")
        self.username_input.setFont(font)
        self.username_input.setFixedWidth(screenWidth * 0.2)
        layout.addWidget(self.username_input)

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Jelszó")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFont(font)
        self.password_input.setFixedWidth(screenWidth * 0.2)
        layout.addWidget(self.password_input)

        # Login button with a nicer style
        login_button = QPushButton("Belépés")
        login_button.setFont(font)
        login_button.setStyleSheet("background-color: #78CFA8; color: #FFFFFF; padding: 10px; border: none;")
        login_button.setFixedWidth(screenWidth * 0.2)
        login_button.clicked.connect(self.on_login_clicked)
        layout.addWidget(login_button)

        # Adjust layout spacing
        layout.setSpacing(10)

        # Set drop shadow effect
        #shadow_effect = QGraphicsDropShadowEffect(blurRadius=10, xOffset=3, yOffset=3)
        #central_widget.setGraphicsEffect(shadow_effect)

        # Setup fade-in animation
        self.setupFadeInAnimation()

    def on_login_clicked(self):
        username = self.username_input.text()
        provided_password = self.password_input.text()

        # Connect to the SQLite database
        conn = sqlite3.connect('persistence/users.db')  # Ensure the path matches your project structure
        cursor = conn.cursor()

        # Retrieve the user's hashed password from the database
        cursor.execute("SELECT password_hash FROM users WHERE username=?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            stored_password_hash = result[0]
            if check_password(stored_password_hash, provided_password):
                print(f"Login successful for username: {username}")
                if self.success_callback:
                    self.success_callback()
                    self.close()
            else:
                print("Login failed: Incorrect password.")
        else:
            print("Login failed: Username does not exist.")


    def setupFadeInAnimation(self):
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)

        self.fade_in_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in_animation.setDuration(500)  # Duration in milliseconds (500ms for a quick fade-in)
        self.fade_in_animation.setStartValue(0.0)  # Start fully transparent
        self.fade_in_animation.setEndValue(1.0)  # End fully opaque
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)  # Smooth transition
        self.fade_in_animation.start()