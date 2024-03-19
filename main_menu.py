from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Main Menu")
        self.setGeometry(100, 100, 400, 300)  # Adjust the size as needed

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        label = QLabel("Welcome to the Main Menu!", self)
        layout.addWidget(label)
