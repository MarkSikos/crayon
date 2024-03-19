import json
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
    QScrollArea, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtSignal

class TanorakWindow(QMainWindow):
    
    go_back_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tanórák")
        self.setGeometry(100, 100, 400, 500)  # Adjust size as needed

        # Main layout
        layout = QVBoxLayout()

        # Title label
        title_label = QLabel("Tanórák")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Scrollable area setup
        self.scroll_area = QScrollArea()
        self.scroll_area_widget_contents = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_widget_contents)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        layout.addWidget(self.scroll_area)

        # Add subject button
        self.add_subject_button = QPushButton("+")
        self.add_subject_button.clicked.connect(self.add_subject)
        layout.addWidget(self.add_subject_button)

        # Back button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.go_back_signal.emit)
        layout.addWidget(back_button)

        # Set the central widget and layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Load subjects from file
        self.subjects = self.load_subjects()
        self.populate_subjects()

    def add_subject(self):
        name, ok = QInputDialog.getText(self, "New Subject", "Subject name:")
        if ok and name:
            self.subjects.append(name)
            self.save_subjects()
            self.populate_subjects()

    def populate_subjects(self):
        # Clear the current subjects list layout
        while self.scroll_area_layout.count():
            item = self.scroll_area_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Add subjects to the scrollable area
        for subject in self.subjects:
            subject_label = QLabel(subject)
            self.scroll_area_layout.addWidget(subject_label)

    def load_subjects(self):
        try:
            with open('database/subjects.json', 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_subjects(self):
        with open('database/subjects.json', 'w') as file:
            json.dump(self.subjects, file)
            
            
            
    

