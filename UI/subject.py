import os
import json
from PyQt6.QtWidgets import (
    QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, 
    QScrollArea, QMessageBox
)
from PyQt6.QtCore import Qt
from .image import ImageViewWindow

class SubjectWindow(QMainWindow):
    def __init__(self, subject_name, go_back_callback):
        super().__init__()
        self.subject_name = subject_name
        self.go_back_callback = go_back_callback
        self.setWindowTitle(subject_name)
        self.setGeometry(100, 100, 400, 500)  # Adjust size as needed

        # Main layout
        layout = QVBoxLayout()

        # Subject title label
        title_label = QLabel(self.subject_name)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        # Scrollable area setup
        self.scroll_area = QScrollArea()
        self.scroll_area_widget_contents = QWidget()
        self.scroll_area_layout = QVBoxLayout(self.scroll_area_widget_contents)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_area_widget_contents)
        layout.addWidget(self.scroll_area)

        # Add PNG files to the scrollable area
        self.populate_files()

        # Back button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.on_back_clicked)
        layout.addWidget(back_button)

        # Set the central widget and layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def populate_files(self):
        # Clear the current files list layout
        while self.scroll_area_layout.count():
            item = self.scroll_area_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # List all PNG files in the subject's folder
        subject_folder = os.path.join('persistence/subjects', self.subject_name)
        if os.path.exists(subject_folder):
            for filename in os.listdir(subject_folder):
                if filename.lower().endswith('.png'):
                    file_button = QPushButton(filename)
                    file_button.clicked.connect(lambda checked, f=filename: self.on_file_clicked(f))
                    self.scroll_area_layout.addWidget(file_button)
        else:
            QMessageBox.warning(self, "Folder Not Found", "The folder for this subject does not exist.")

    def on_file_clicked(self, file_name):
        # Instead of showing a message box, create and display the ImageViewWindow
        image_path = os.path.join('persistence/subjects', self.subject_name, file_name)
        self.image_view_window = ImageViewWindow(image_path, self.show_subject_window)
        self.image_view_window.show()
        self.hide()
    def on_back_clicked(self):
        self.go_back_callback()
        
    def show_subject_window(self):
        # This function will be called by the ImageViewWindow to show SubjectWindow again
        if hasattr(self, 'image_view_window') and self.image_view_window.isVisible():
            self.image_view_window.close()
        self.show()
