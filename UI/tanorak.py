import json
import os
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
    QScrollArea, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from .subject import SubjectWindow

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
            # Append the new subject name to the subjects list
            self.subjects.append(name)
            # Save the updated subjects list to the JSON file
            self.save_subjects()
            # Repopulate the subjects in the UI
            self.populate_subjects()
            # Create a new folder for the subject inside the database folder
            self.create_subject_folder(name)

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
        # Instead of displaying a message, create and display the SubjectWindow
        # First, ensure to hide the current window
        self.hide()
        # Now create the SubjectWindow passing the subject name and the callback function
        self.subject_window = SubjectWindow(subject, self.show_tanorak_menu)
        self.subject_window.show()
        
        
    def show_tanorak_menu(self):
        # This function will be called by the SubjectWindow to show TanorakWindow again
        # Make sure to check if the SubjectWindow is open, and if so, close it
        if hasattr(self, 'subject_window') and self.subject_window.isVisible():
            self.subject_window.close()
        # Show the TanorakWindow again
        self.show()

    def load_subjects(self):
        try:
            with open('persistence/subjects.json', 'r') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_subjects(self):
        with open('persistence/subjects.json', 'w') as file:
            json.dump(self.subjects, file)
            
            
    def create_subject_folder(self, subject_name):
        # Define the path for the new folder
        folder_path = os.path.join('persistence/subjects', subject_name)
        # Check if the folder already exists to avoid overwriting it
        if not os.path.exists(folder_path):
            # Create the folder
            os.makedirs(folder_path)
            QMessageBox.information(self, "Folder Created", f"Folder for '{subject_name}' created successfully.")
        else:
            QMessageBox.warning(self, "Folder Exists", f"A folder for '{subject_name}' already exists.")

    def on_back_clicked(self):
        if self.show_main_menu_callback:
            self.show_main_menu_callback()
