from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton, QScrollArea, QHBoxLayout, QToolButton, QSpacerItem, QSizePolicy, QApplication, QFrame
from PyQt6.QtGui import QIcon, QFont, QPalette, QColor
from PyQt6.QtCore import Qt, QSize
from Modell.Logic.SubjectManager import SubjectManager
from abc import abstractmethod

class ListWindow(QMainWindow):
    """
    Absztrakt osztály a lista típusú ablakok kezelésére.
    """
    
    # Konstruktor
    
    def __init__(self):
        super().__init__()
        self._subject_id= None
        self._user_role = None
        self._user_id = None
        self._half_screen_width = QApplication.primaryScreen().size().width() // 2
        self._layout = QVBoxLayout()
        central_widget = QWidget()
        central_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        central_widget.setLayout(self._layout)
        self.setCentralWidget(central_widget)
    
    # UI-t setupolo függvények
    
    def _create_header(self, title_text):
        """Fejléc létrehozása."""
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ECECE7"))
        self.setPalette(palette)
        self._header_layout = QHBoxLayout()
        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Segoe UI", 36, QFont.Weight.Bold))
        self._header_layout.addWidget(title_label)
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self._header_layout.addSpacerItem(spacer)
        self._header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum))
        back_button = QPushButton()
        back_button.setObjectName("backButton")
        back_button.setIcon(QIcon("Assets/back_icon.png"))
        back_button.clicked.connect(self._on_back_clicked)
        back_button.setIconSize(QSize(self._half_screen_width/20, self._half_screen_width/20))
        back_button.setObjectName("backButton")
        self._header_layout.addWidget(back_button)  
        horizontal_line = QFrame()
        horizontal_line.setFrameShape(QFrame.Shape.HLine)
        horizontal_line.setFrameShadow(QFrame.Shadow.Sunken)
        self._layout.addLayout(self._header_layout)
        self._layout.addWidget(horizontal_line)

    def _create_scroll_area(self):
        """Scrollarea létrehozása az elemek megjelenítéséhez."""
        self._scroll_area = QScrollArea()
        scroll_area_widget_contents = QWidget()
        self._scroll_area_layout = QVBoxLayout()
        scroll_area_widget_contents.setLayout(self._scroll_area_layout)
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setWidget(scroll_area_widget_contents)
        self._layout.addWidget(self._scroll_area)
        self._scroll_area_layout.setSpacing(5)

    def _create_buttons(self, is_note, role):
        """Gombok létrehozása."""
        self._add_subject_button = QToolButton()
        self._add_subject_button.setText("Hozzáadás")
        self._add_subject_button.clicked.connect(self._add)
        self._add_subject_button.setObjectName("addSubjectButton")
        self._remove_subject_button = QToolButton()
        self._remove_subject_button.setText("Törlés")
        self._remove_subject_button.clicked.connect(self._remove)
        self._remove_subject_button.setObjectName("removeSubjectButton")
        if not is_note and role == "Student":
            return
        else:
            self._layout.addWidget(self._add_subject_button)
            self._layout.addWidget(self._remove_subject_button)
        
    def _populate(self, is_note):
        """Elemeknek a scrollarea-ra való betöltéséért felelős függvény. """
        while self._scroll_area_layout.count():
            item = self._scroll_area_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        if is_note :
            items = SubjectManager.get_notes(self._subject_id, self._user_id)
        else:
            items = SubjectManager.get_subjects()
        if items:
            for id, name in items:
                folder_button = QToolButton()
                folder_button.setIcon(QIcon("Assets/jegyzet.svg"))  
                folder_button.setText(name)
                folder_button.setFont(QFont("Segoe UI", 16, QFont.Weight.Normal))
                folder_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
                folder_button.setAutoRaise(True)
                button_height_fixed = self._half_screen_width // 8
                folder_button.setFixedHeight(button_height_fixed)
                icon_size = QSize(button_height_fixed * 0.8, button_height_fixed * 0.8)
                folder_button.setIconSize(icon_size)
                if is_note:
                    folder_button.clicked.connect(lambda checked, n_id=id: self._on_folder_clicked(n_id))
                else:
                    folder_button.clicked.connect(lambda checked, s=id: self._on_subject_clicked(s))
                folder_button.setObjectName("subjectButton")
                self._scroll_area_layout.addWidget(folder_button)
                self._adjust_button_widths()
        else:
            self._adjust_button_widths()
        self._scroll_area_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    def _adjust_button_widths(self):
        """ A gombok dinamikus méretezéséért felelős függvény. """
        size_policy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._add_subject_button.setSizePolicy(size_policy)
        self._remove_subject_button.setSizePolicy(size_policy)
        for i in range(self._scroll_area_layout.count()):
            widget = self._scroll_area_layout.itemAt(i).widget()
            if widget:  
                widget.setSizePolicy(size_policy)
                
    # Absztrakt függvények (implementálni kell alosztályban)
    
    @abstractmethod
    def _add(self):
        """Absztrakt függvény új elem hozzáadására."""
        raise NotImplementedError("Nincs implementálva")

    @abstractmethod
    def _remove(self):
        """Absztrakt függvény elem eltávolítására."""
        raise NotImplementedError("Még nincs implementálva")

    @abstractmethod
    def _on_back_clicked(self):
        """Absztrakt függvény a visszalépés gomb eseménykezelésére."""
        raise NotImplementedError("Még nincs implementálva")
        
    