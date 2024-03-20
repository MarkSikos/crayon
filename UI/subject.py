from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QScrollArea, QMessageBox, QInputDialog
from PyQt6.QtGui import QImage, QPainter, QColor, QIcon, QGuiApplication  # Add QGuiApplication here
from PyQt6.QtCore import Qt, QPoint
import os
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
        

        add_folder_button = QPushButton("New Folder")
        add_folder_button.clicked.connect(self.add_new_folder)
        layout.addWidget(add_folder_button)
        
        # Back button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.on_back_clicked)
        layout.addWidget(back_button)

        # Set the central widget and layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        
        
        
        self.populate_folders()

    def populate_files(self):
        print("populating files")
        # Clear the current files list layout
        while self.scroll_area_layout.count():
            item = self.scroll_area_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # List all folders in the subject's folder
        subject_folder = os.path.join('persistence/subjects', self.subject_name)
        if os.path.exists(subject_folder):
            for entry in os.listdir(subject_folder):
                folder_path = os.path.join(subject_folder, entry)
                if os.path.isdir(folder_path):
                    folder_button = QPushButton(entry)
                    folder_button.clicked.connect(lambda checked, f=entry: self.on_folder_clicked(f))
                    self.scroll_area_layout.addWidget(folder_button)
        else:
            QMessageBox.warning(self, "Folder Not Found", "The folder for this subject does not exist.")

    def on_folder_clicked(self, folder_name):
        print("on folder clicked")
        folder_path = os.path.join('persistence/subjects', self.subject_name, folder_name)
        # Assuming ImageViewWindow is imported correctly at the top
        self.image_view_window = ImageViewWindow(folder_path, self.show_subject_window)
        self.image_view_window.show()
        self.hide()  # Optionally hide the SubjectWindow if desired
    def on_back_clicked(self):
        self.go_back_callback()
        
    def show_subject_window(self):
        # This function will be called by the ImageViewWindow to show SubjectWindow again
        if hasattr(self, 'image_view_window') and self.image_view_window.isVisible():
            self.image_view_window.close()
        self.show()


    def populate_folders(self):
        
        print("populate folders")
        while self.scroll_area_layout.count():
            item = self.scroll_area_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        subject_folder = os.path.join('persistence/subjects', self.subject_name)
        if os.path.exists(subject_folder):
            for entry in sorted(os.listdir(subject_folder)):
                folder_path = os.path.join(subject_folder, entry)
                if os.path.isdir(folder_path):
                    folder_button = QPushButton(entry)
                    folder_button.clicked.connect(lambda checked, f=entry: self.on_folder_clicked(f))
                    self.scroll_area_layout.addWidget(folder_button)

    def add_new_folder(self):
        name, ok = QInputDialog.getText(self, "New Folder", "Folder name:")
        if ok and name:
            new_folder_path = os.path.join('persistence/subjects', self.subject_name, name)
            if not os.path.exists(new_folder_path):
                os.makedirs(new_folder_path)
                # Create a new PNG file inside the folder
                self.create_initial_png(new_folder_path, name)
                QMessageBox.information(self, "Success", f"'{name}' folder and initial PNG file created.")
                self.populate_folders()  # Refresh the folders list
            else:
                QMessageBox.warning(self, "Exists", "Folder already exists.")

    def create_initial_png(self, folder_path, folder_name):
        # Ensure QGuiApplication is correctly initialized in your main app before calling this

        # Get the screen size
        screen = QGuiApplication.primaryScreen().geometry()  # Use .geometry() to get the QRect of the screen
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)

        # Create a new QImage with a white background
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)

        # Save the image to the folder
        file_name = "sheet_00.png"
        file_path = os.path.join(folder_path, file_name)
        image.save(file_path)
