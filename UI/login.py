# File path: /path/to/your/login.py

import sqlite3
from PyQt6.QtWidgets import QMainWindow, QLineEdit, QPushButton, QVBoxLayout, QWidget, QLabel, QGraphicsOpacityEffect, QApplication, QGraphicsDropShadowEffect, QHBoxLayout
from PyQt6.QtGui import QFont, QPalette, QColor, QFontDatabase, QIcon, QPixmap

from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, Qt
from utility_modules.password_handling import check_password  # Adjust this import path as necessary
class LoginWindow(QMainWindow):
    def __init__(self, success_callback=None):
        super().__init__()
        self.setWindowTitle("Crayon Oktatási Szoftver")

        self.success_callback = success_callback

        # Get the screen size
        screen = QApplication.primaryScreen().geometry()
        screenWidth = screen.width()
        screenHeight = screen.height()

        # Set the window size to match the screen size
        self.setGeometry(0, 0, screenWidth*0.2, screenHeight*0.4)
        self.setFixedSize(self.width(), self.height())

        
        font_family = "Segoe UI"
        font = QFont(font_family, 10)  # Adjust size as needed

        # Set the application's palette for the background color
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#87CEEB"))
        self.setPalette(palette)

        # Set central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Title label
        title_label = QLabel("Belépés")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.ExtraBold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("margin-bottom: 20px;")  # Add margin for space below the title
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignTop)  # Add title label to the top of the layout
        



        # Username input
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Felhasználói név")
        self.username_input.setFont(font)
        self.username_input.setFixedWidth(screenWidth * 0.15)
        
        username_layout = QHBoxLayout()
        username_icon_label = QLabel(self)
        username_icon_label.setPixmap(QPixmap('assets/username_light.png').scaledToHeight(20)) # Assuming you want the icon size to match text height
        username_layout.addWidget(username_icon_label)
        username_layout.addWidget(self.username_input)
            
        layout.addLayout(username_layout)
        

        # Password input
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Jelszó")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFont(font)
        self.password_input.setFixedWidth(screenWidth * 0.15)
        
        password_layout = QHBoxLayout()
        password_icon_label = QLabel(self)
        password_icon_label.setPixmap(QPixmap('assets/password_light.png').scaledToHeight(20))  # Same assumption as above
        password_layout.addWidget(password_icon_label)
        password_layout.addWidget(self.password_input)
        
        layout.addLayout(password_layout)
        #layout.addWidget(self.password_input)

        # Login button with a nicer style
        login_button = QPushButton("Belépés")
        login_button.setFont(font)
        login_button.setStyleSheet("background-color: #78CFA8; \
                                   color: #FFFFFF; padding: 10px; \
                                   border-radius:10px; \
                                       border: none;")
        login_button.setFixedWidth(screenWidth * 0.18)
        login_button.clicked.connect(self.on_login_clicked)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch(25)
        button_layout.addWidget(login_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        
        
        #layout.addWidget(login_button)

        # Adjust layout spacing
        layout.setSpacing(10)
        
        self.centerOnScreen()

        # Set drop shadow effect
        #shadow_effect = QGraphicsDropShadowEffect(blurRadius=10, xOffset=3, yOffset=3)
        #central_widget.setGraphicsEffect(shadow_effect)

        # Setup fade-in animation
        #self.setupFadeInAnimation()
    
    def centerOnScreen(self):
        # Get the size of the screen
        screen = QApplication.primaryScreen().geometry()
        screenWidth = screen.width()
        screenHeight = screen.height()

        # Size of the window
        windowWidth = screenWidth * 0.2  # Adjust the size as needed
        windowHeight = screenHeight * 0.4  # Adjust the size as needed

        # Calculate the center position
        centerX = (screenWidth - windowWidth) // 2
        centerY = (screenHeight - windowHeight) // 2

        # Move the window to the center
        self.setGeometry(centerX, centerY, windowWidth, windowHeight)

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