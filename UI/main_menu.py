# main_menu.py
from PyQt6.QtWidgets import QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtGui import QFont, QPalette, QColor
from PyQt6.QtCore import Qt
from .tanorak import TanorakWindow

class MainMenu(QMainWindow):
    
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crayon")
        self.setGeometry(100, 100, 400, 500)  # Adjust the size and position as needed
        
        # Initialize the UI components
        self.setup_ui()

      
    def setup_ui(self):
        
         # Set the font to be used in the buttons
        button_font = QFont("Arial", 12)
        button_font.setBold(True)

        # Central widget and layout
        central_widget = QWidget(self)
        layout = QVBoxLayout(central_widget)  # layout is now defined

        # Title label inside a white rectangle
        title_label = QLabel("Crayon")
        title_label.setFont(QFont("Arial", 24, weight=QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("background-color: white; margin-bottom: 20px; padding: 10px;")
        layout.addWidget(title_label)

        # Create individual buttons with unique actions
        self.tanorak_button = QPushButton("Tanórák")
        self.dolgozatok_button = QPushButton("Dolgozatok")
        self.hazi_feladatok_button = QPushButton("Házi Feladatok")
        self.eredmenyek_button = QPushButton("Eredmények")
        self.beallitasok_button = QPushButton("Beállítások")

        # Set properties for each button and add to layout
        for button in [self.tanorak_button, self.dolgozatok_button,
                       self.hazi_feladatok_button, self.eredmenyek_button,
                       self.beallitasok_button]:
            button.setFont(button_font)
            button.setStyleSheet("margin: 5px; padding: 10px;")
            layout.addWidget(button)

        # Connect buttons to their respective slot functions
        self.tanorak_button.clicked.connect(self.show_tanorak)
        # Define and connect the other buttons to their respective functions as well
        # self.dolgozatok_button.clicked.connect(self.show_dolgozatok)
        # self.hazi_feladatok_button.clicked.connect(self.show_hazi_feladatok)
        # self.eredmenyek_button.clicked.connect(self.show_eredmenyek)
        # self.beallitasok_button.clicked.connect(self.show_beallitasok)

        # Set the central widget and layout
        self.setCentralWidget(central_widget)
        
        
    def show_tanorak(self):
        self.tanorak_window = TanorakWindow()
        self.tanorak_window.show()
        self.close()  # Close the main menu
        
    def show_dolgozatok(self):
        # Code to show the Dolgozatok section
        pass

    def show_hazi_feladatok(self):
        # Code to show the Házi Feladatok section
        pass

    def show_eredmenyek(self):
        # Code to show the Eredmények section
        pass

    def show_beallitasok(self):
        # Code to show the Beállítások section
        pass