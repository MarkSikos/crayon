from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSlider, QColorDialog, QMessageBox, QScrollArea,  QSpacerItem, QSizePolicy
from PyQt6.QtGui import QImage, QPainter, QColor, QGuiApplication
from PyQt6.QtCore import Qt
import os
import glob
from .drawing import DrawingArea  # Ensure correct import path

class ImageViewWindow(QMainWindow):
    def __init__(self, folder_path, go_back_callback):
        super().__init__()
        self.folder_path = folder_path
        self.setWindowTitle("Image View")
        self.setGeometry(100, 100, 1200, 800)  # Adjust size as needed

        self.drawing_areas = []

        self.setup_ui(go_back_callback)
        self.load_images()
        
        self.go_back_callback = go_back_callback
        
    def setup_ui(self, go_back_callback):
        
        self.tool_size_slider = QSlider(Qt.Orientation.Horizontal)
        self.brush_button = QPushButton("Brush")
        self.eraser_button = QPushButton("Eraser")
        self.color_button = QPushButton("Pick Color")
        self.undo_button = QPushButton("Undo")
        self.select_button = QPushButton("Select") 
        #self.save_button = QPushButton("Save")
        #self.back_button = QPushButton("Back")
        
        self.brush_button.clicked.connect(lambda: self.set_tool_for_all('brush'))
        self.eraser_button.clicked.connect(lambda: self.set_tool_for_all('eraser'))
        self.select_button.clicked.connect(self.select_tool)
        self.tool_size_slider.valueChanged.connect(self.adjust_tool_size_for_all)
        self.color_button.clicked.connect(self.pick_color_for_all)
        self.undo_button.clicked.connect(self.undo_last_action)
        #self.save_button.clicked.connect(self.save_all_drawings)
        
        # Horizontal layout for the control buttons and the slider
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self.brush_button)
        controls_layout.addWidget(self.eraser_button)
        controls_layout.addWidget(self.color_button)
        controls_layout.addWidget(self.undo_button)
        controls_layout.addWidget(self.select_button)
        
        #controls_layout.addWidget(self.save_button)  # Save button next to the others
        #controls_layout.addWidget(self.back_button)  # Back button next to the others
        controls_layout.addWidget(self.tool_size_slider)  # Adjusted position for the slider

        self.save_button = QPushButton("Save All Changes")
        self.save_button.clicked.connect(self.save_all_drawings)
        controls_layout.addWidget(self.save_button)
        
        self.back_button = QPushButton("Back")
        self.back_button.clicked.connect(lambda: go_back_callback())
        controls_layout.addWidget(self.back_button)
        
        self.add_button = QPushButton("Add new page")
        self.add_button.clicked.connect(self.add_new_png)
        controls_layout.addWidget(self.add_button)
        
        
        
        
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # Scroll Area setup
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()  # This widget will contain the scroll_layout
        self.scroll_layout = QVBoxLayout(self.scroll_widget)  # Define scroll_layout here
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        self.main_layout.addWidget(self.scroll_area)

        # Control buttons layout
        #controls_layout = QHBoxLayout()
        # Initialize and add buttons like save_button, back_button, etc. to controls_layout
        # Example:
        #self.back_button = QPushButton("Back")
        #self.back_button.clicked.connect(lambda: self.go_back_callback())
        #controls_layout.addWidget(self.back_button)

        # Add controls_layout to main_layout
        self.main_layout.addLayout(controls_layout)

    def select_tool(self):
        if hasattr(self, 'last_active_drawing_area'):
            self.last_active_drawing_area.setTool('select')
            
    def change_tool_size(self, size):
        if self.drawing_area.current_tool:
            self.drawing_area.tool_sizes[self.drawing_area.current_tool] = size

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.drawing_area.brushColor = color

    def save_drawing(self):
        painter = QPainter(self.drawing_area.original_image)
        painter.drawImage(0, 0, self.drawing_area.temp_image)
        painter.end()
        self.drawing_area.original_image.save(self.image_path)
        QMessageBox.information(self, "Saved", "Your drawing has been saved.")
        self.drawing_area.temp_image.fill(Qt.GlobalColor.transparent)
        self.drawing_area.update()

    def on_back_clicked(self):
        self.go_back_callback()


    def load_images(self):
        self.clear_layout(self.scroll_layout)
        png_files = glob.glob(os.path.join(self.folder_path, '*.png'))
        #self.drawing_areas.clear() 
        self.drawing_areas.clear() # !!
        for image_path in png_files:
            drawing_area = DrawingArea(image_path)
            drawing_area.activeSignal.connect(self.set_last_active_drawing_area)
        
            self.drawing_areas.append(drawing_area)
            self.scroll_layout.addWidget(drawing_area)

            # Add an empty QWidget with a fixed height as a spacer
            spacer_widget = QWidget()
            spacer_widget.setFixedHeight(20)  # Adjust the height for desired spacing
            self.scroll_layout.addWidget(spacer_widget)

            
    def save_all_drawings(self):
        for drawing_area in self.drawing_areas:
            drawing_area.save_changes()
        QMessageBox.information(self, "Saved", "All changes to the images have been saved.")
            
        
    def add_new_png(self):
        # Define how to create and name the new PNG file
        print("add new png")
        
        #El kell menteni !!
        self.save_all_drawings()
        new_file_path = self.create_new_png(self.folder_path, "sheet")
        # Load the newly created PNG file
        self.load_images()  # Reload to include the new file
        QMessageBox.information(self, "PNG Added", f"New PNG file created: {new_file_path}")

    def create_new_png(self, folder_path, base_name):
        counter = 1
        while os.path.exists(os.path.join(folder_path, f"{base_name}_{counter:02d}.png")):
            counter += 1
        new_file_path = os.path.join(folder_path, f"{base_name}_{counter:02d}.png")

        screen = QGuiApplication.primaryScreen().geometry()  # Use .geometry() to get the QRect of the screen
        width = int(screen.width() * 0.8)
        height = int(screen.height() * 0.8)

        # Create a new QImage with a white background
        image = QImage(width, height, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        image.save(new_file_path)

        return new_file_path
    
    def set_tool_for_all(self, tool):
        for drawing_area in self.drawing_areas:
            drawing_area.setTool(tool)

    def adjust_tool_size_for_all(self, size):
        for drawing_area in self.drawing_areas:
            drawing_area.adjustToolSize(size)

    def pick_color_for_all(self):
        color = QColorDialog.getColor(parent=self)
        if color.isValid():
            for drawing_area in self.drawing_areas:
                drawing_area.brushColor = color
                drawing_area.update()  # Force update to apply the color change

    def clear_layout(self,layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
    def set_last_active_drawing_area(self, drawing_area):
        self.last_active_drawing_area = drawing_area

    def undo_last_action(self):
        if hasattr(self, 'last_active_drawing_area'):
            self.last_active_drawing_area.undo()