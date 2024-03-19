import json
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
    QScrollArea, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt

class TanorakWindow(QMainWindow):
    def __init__(self, show_main_menu_callback=None):
        super().__init__()
        self.show_main_menu_callback = show_main_menu_callback
        self.setWindowTitle("Tanórák")
        self.setGeometry(100, 100, 400, 500)  # Adjust size as needed

        # Main layout for the window
        layout = QVBoxLayout()

        # Title label
        title_label = QLabel("Tanórák")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Scrollable area setup
        self.scroll_area = QScrollArea()
        scroll_area_widget_contents = QWidget()
        self.scroll_area_layout = QVBoxLayout()
        scroll_area_widget_contents.setLayout(self.scroll_area_layout)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(scroll_area_widget_contents)
        layout.addWidget(self.scroll_area)

        # Add subject button
        self.add_subject_button = QPushButton("+")
        self.add_subject_button.clicked.connect(self.add_subject)
        layout.addWidget(self.add_subject_button)

        # Back button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.on_back_clicked)
        layout.addWidget(back_button)

        # Set the central widget and layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        # Load and display subjects from file
        self.subjects = self.load_subjects()
        self.populate_subjects()

    def add_subject(self):
        name, ok = QInputDialog.getText(self, "New Subject", "Subject name:")
        if ok and name:
            self.subjects.append(name)
            self.save_subjects()
            self.populate_subjects()

    def populate_subjects(self):
        # Clear the current subjects list
        while self.scroll_area_layout.count():
            item = self.scroll_area_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Add subjects to the scrollable area as buttons
        for subject in self.subjects:
            subject_button = QPushButton(subject)
            subject_button.setFixedHeight(40)  # Set a fixed height for each button
            # Connect each button to a method (e.g., opening a detail view for the subject)
            subject_button.clicked.connect(lambda checked, s=subject: self.on_subject_clicked(s))
            self.scroll_area_layout.addWidget(subject_button)
            self.scroll_area_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)  # Align items to bottom

    def on_subject_clicked(self, subject):
        QMessageBox.information(self, "Subject Selected", f"You selected: {subject}")

    def load_subjects(self):
        try:
            with open('database/subjects.json', 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_subjects(self):
        with open('database/subjects.json', 'w') as file:
            json.dump(self.subjects, file)

    def on_back_clicked(self):
        if self.show_main_menu_callback:
            self.show_main_menu_callback()
