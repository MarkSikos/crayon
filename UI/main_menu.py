from PyQt6.QtWidgets import QMainWindow, QPushButton, QWidget, QApplication, QLabel, QVBoxLayout, QSpacerItem, QSizePolicy, QHBoxLayout, QScrollArea, QToolButton
from PyQt6.QtGui import QFont, QPalette, QColor, QPixmap, QBrush, QIcon
from PyQt6.QtCore import Qt, QSize

from .FlowLayout import FlowLayout  # Make sure this matches your project structure

class MainMenu(QMainWindow):
    def __init__(self, show_tanorak_callback=None):
        super().__init__()
        self.show_tanorak_callback = show_tanorak_callback
        self.setWindowTitle("Crayon")
        self.setAutoFillBackground(True)
        
        self.buttons = []
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ECECE7"))
        self.setPalette(palette)

        self.scroll_area = QScrollArea(self)  # Create a QScrollArea.
        self.scroll_area.setWidgetResizable(True)  # Make the scroll area's widget resizable

        self.central_widget = QWidget()  # This widget will contain your layout
        self.scroll_area.setWidget(self.central_widget)  # Set the widget that the scroll area displays
        self.setCentralWidget(self.scroll_area)  # Set the scroll area as the central widget of the window


        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Adjust margins if necessary
        main_layout.setSpacing(10)  # Adjust spacing if necessary
        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        main_layout.addSpacerItem(spacer)

        #title_label = QLabel("Crayon")
        #title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.ExtraBold))
        
        #title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #main_layout.addWidget(title_label)
        
        # Create a horizontal layout to add spacer
        h_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)  # Adjust the size as needed
        h_layout.addSpacerItem(spacer)
        
        flow_layout_widget = QWidget()
        flow_layout = FlowLayout(flow_layout_widget)

        

        screen = QApplication.primaryScreen().geometry()
        side_length = min(screen.width() / 3, screen.height() / 3)
        button_size = QSize(side_length, side_length)  # Calculate size based on screen dimensions

        buttons_info = [
            ("Tanórák", self.show_tanorak, "assets/tanorak_icon.svg"),
            ("Dolgozatok", self.show_dolgozatok, "assets/dolgozatok_icon.svg"),
            ("Házi Feladatok", self.show_hazi_feladatok, "assets/hazi_feladatok_icon.svg"),
            ("Eredmények", self.show_eredmenyek, "assets/eredmenyek_icon.svg"),
            ("Beállítások", self.show_beallitasok, "assets/beallitasok_icon.svg")
        ]

        for text, slot, icon_path in buttons_info:
            button = QToolButton()
            button.setText(text)
            button.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            icon_side_length = side_length * 0.7  # Keep the icon size calculation
            button.setIcon(QIcon(icon_path))
            button.setIconSize(QSize(icon_side_length, icon_side_length))  # Resize icon to 70%
            button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            button.setStyleSheet("""
                QToolButton {
                    background-color: #007BFF;  /* Blue background */
                    color: white;
                    border-radius: 15px;  /* Increased corner radius */
                    padding-top: 20px;  /* Increase top padding to push the icon lower */
                    padding-bottom: 10px;  /* Adjust bottom padding as needed */
                }
                QToolButton::hover {
                    background-color: #0056b3;  /* Darker blue on hover */
                }
            """)
            button.clicked.connect(slot)
            button.setFixedSize(button_size)
            self.buttons.append(button)
            flow_layout.addWidget(button)

        h_layout.addWidget(flow_layout_widget)
        h_layout.addSpacerItem(spacer)
        
        
        main_layout.addLayout(h_layout)
        main_layout.addSpacerItem(spacer)




    def show_tanorak(self):
        if self.show_tanorak_callback:
            self.show_tanorak_callback()
            
    def show_dolgozatok(self): pass
    def show_hazi_feladatok(self): pass
    def show_eredmenyek(self): pass
    def show_beallitasok(self): pass
