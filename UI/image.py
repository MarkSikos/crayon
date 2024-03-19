from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QPushButton, QSlider, QColorDialog, QMessageBox
from PyQt6.QtGui import QPixmap, QImage, QPainter
from PyQt6.QtCore import Qt
from .drawing import DrawingArea  # Adjust the import as necessary based on your project structure

class ImageViewWindow(QMainWindow):
    def __init__(self, image_path, go_back_callback):
        super().__init__()
        self.image_path = image_path
        self.go_back_callback = go_back_callback
        self.setWindowTitle("Image View")
        self.setGeometry(100, 100, 800, 800)  # Adjust size as needed

        # Main layout
        layout = QVBoxLayout()

        # Custom drawing area
        self.drawing_area = DrawingArea(self.image_path)
        layout.addWidget(self.drawing_area)

        # Brush size slider
        self.brush_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.brush_size_slider.setMinimum(1)
        self.brush_size_slider.setMaximum(50)
        self.brush_size_slider.setValue(5)  # Default brush size
        self.brush_size_slider.valueChanged.connect(self.change_brush_size)
        layout.addWidget(self.brush_size_slider)

        # Color picker button
        self.color_button = QPushButton("Pick Color")
        self.color_button.clicked.connect(self.pick_color)
        layout.addWidget(self.color_button)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_drawing)
        layout.addWidget(save_button)

        # Back button
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.on_back_clicked)
        layout.addWidget(back_button)

        # Set the central widget
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def change_brush_size(self, size):
        self.drawing_area.brushSize = size

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.drawing_area.brushColor = color

    def save_drawing(self):
        # Create a QPainter to draw the temp_image onto the original_image
        painter = QPainter(self.drawing_area.original_image)
        painter.drawImage(0, 0, self.drawing_area.temp_image)
        painter.end()

        # Save the merged image back to the file
        self.drawing_area.original_image.save(self.image_path)
        QMessageBox.information(self, "Saved", "Your drawing has been saved.")

        # Optionally, clear the temp_image if you want to continue drawing from the saved state
        self.drawing_area.temp_image.fill(Qt.GlobalColor.transparent)
        self.drawing_area.update()
        
        
    def on_back_clicked(self):
        self.go_back_callback()
