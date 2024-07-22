from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QSpacerItem, QSizePolicy, QTableWidget, QTableWidgetItem, QVBoxLayout, QHeaderView, QFrame
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor
from PyQt6.QtCore import Qt, QSize
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
from Modell.UtilityModules.DashboardUtilities import DashboardUtilities
from Modell.UtilityModules.StyleSheetUtilities import StyleSheetUtilities

CSS_PATH = 'Persistence/style/dashboard_style.css'

class DashboardWindow(QMainWindow):
    """
    Class for handling the dashboard window. It creates and manages the UI.
    """
    
    # Constructor

    def __init__(self, main_menu_callback,user_id, geometry):
        super().__init__()
        self.user_id = user_id
        self.main_menu_callback = main_menu_callback
        self.setWindowTitle("Crayon")
        self.setAutoFillBackground(True)
        self.half_screen_width = QApplication.primaryScreen().size().width() // 2
        self.init_ui()
        StyleSheetUtilities.load_stylesheet(self, CSS_PATH)
        self.setGeometry(geometry)
        self.show()
        
    # UI-managing functions
    
    def init_ui(self):
        """ Instantiates a Dahboardwindow object, sets the UI and stylesheets. """
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        self.create_header()
        self.create_scroll_area()
        
    def create_header(self):
        """ Creates the header that includes the title and the back button. """
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#ECECE7"))
        self.setPalette(palette)
        self.header_layout = QHBoxLayout()
        title_label = QLabel("Tanári Dashboard")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_font = QFont("Segoe UI", 36, QFont.Weight.Bold)
        title_label.setStyleSheet("color: black;") 
        title_label.setFont(title_font)
        self.header_layout.addWidget(title_label)
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.header_layout.addSpacerItem(spacer)
        self.header_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum))
        back_button = QPushButton()
        back_button.setObjectName("backButton")
        back_button.setIcon(QIcon("Assets/back_icon.png"))
        back_button.clicked.connect(self.go_back)
        back_button.setObjectName("backButton")
        back_button.setIconSize(QSize(self.half_screen_width/20, self.half_screen_width/20))
        self.header_layout.addWidget(back_button)
        self.layout.addLayout(self.header_layout)
        horizontal_line = QFrame()
        horizontal_line.setFrameShape(QFrame.Shape.HLine)
        horizontal_line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(horizontal_line)
        
    def create_scroll_area(self):
        """ Creates a scroll area, containing widgets, histograms and data tables. """
        test_data = self.fetch_histogram_data("test")
        homework_data = self.fetch_histogram_data("homework")
        self.layout.addWidget(self.create_histogram_widget(test_data,homework_data))
        all_data = DashboardUtilities.fetch_data()
        tests_summary_table_widget = self.create_summary_widget(all_data[0], "Test Results")
        homeworks_summary_table_widget = self.create_summary_widget(all_data[1],  "Homework Results")
        self.h_layout = QHBoxLayout()
        self.h_layout.addWidget(tests_summary_table_widget)
        self.h_layout.addWidget(homeworks_summary_table_widget)
        self.layout.addLayout(self.h_layout)
                    
    # Data/Statistics management 
    
    def fetch_histogram_data(self, type):
        """ Queries the data according to exercise type (test/homework) to refresh the histogram. """
        if type == "test":
            data = DashboardUtilities.fetch_data()[0]
        else:
            data = DashboardUtilities.fetch_data()[1]
        needed_data = [item[3] for item in data]
        return needed_data
    
    def create_summary_widget(self, summary_data, title_text):
        """ Creates a widget that summarizes the statistical data of both the tests and homeworks. """
        container_widget = QWidget()
        layout = QVBoxLayout(container_widget)
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18pt; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)
        num_rows = len(summary_data)
        num_columns = 4  
        table_widget = QTableWidget(num_rows, num_columns)
        table_widget.setHorizontalHeaderLabels(['Felhasználó', 'Típus', 'Teszt Neve', 'Eredmény'])
        table_widget.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        for row, record in enumerate(summary_data):
            for column, item in enumerate(record):
                table_widget.setItem(row, column, QTableWidgetItem(str(item)))
        for column in range(num_columns):
            table_widget.horizontalHeader().setSectionResizeMode(column, QHeaderView.ResizeMode.Stretch)

        layout.addWidget(table_widget)
        return container_widget
    
    def create_histogram_widget(self,test_data, homework_data):
        """ Creates a widget for the histogram of the test/homework scores. """
        container_widget = QWidget()
        widget_layout = QVBoxLayout(container_widget)
        figure = Figure()
        canvas = FigureCanvas(figure)
        canvas.setContentsMargins(10, 10, 10, 10)
        canvas.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        toolbar = NavigationToolbar(canvas, container_widget)
        matplotlib.rcParams['font.family'] = 'Segoe UI'
        matplotlib.rcParams['text.color'] = '#333333'
        figure.clear()
        figure.patch.set_facecolor('none')  
        plt.style.use('seaborn-whitegrid') 
         
        ax1 = figure.add_subplot(121)  
        ax1.hist(test_data, bins=20, alpha=0.9, color='royalblue', label='Teszt Pontok', edgecolor='white')
        ax1.set_title('Teszt Pontok Megoszlása', fontsize=14, fontweight='regular')
        ax1.set_xlabel('Pontok', fontsize=12)
        ax1.set_ylabel('Emberek', fontsize=12)
        ax1.legend(frameon=True, framealpha=0.8, shadow=False, fontsize=10)
        ax1.set_facecolor('none')  
        ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax1.yaxis.set_major_locator(MaxNLocator(integer=True))

        ax2 = figure.add_subplot(122)  
        ax2.hist(homework_data, bins=20, alpha=0.9, color='limegreen', label='Házifeladat Pontok', edgecolor='white')
        ax2.set_title('Házifeladat Pontok Megoszlása', fontsize=14, fontweight='regular')
        ax2.set_xlabel('Pontok', fontsize=12)
        ax2.set_ylabel('Emberek', fontsize=12)
        ax2.legend(frameon=True, framealpha=0.8, shadow=False, fontsize=10)
        ax2.set_facecolor('none')  
        ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax2.yaxis.set_major_locator(MaxNLocator(integer=True))

        canvas.draw()
        widget_layout.addWidget(toolbar)
        widget_layout.addWidget(canvas)
        return container_widget
    
    # Eventhandlers
    
    def go_back(self):
        """ Kezeli a vissza gomb eseményét. """
        geometry = self.geometry()
        if callable(self.main_menu_callback):
            self.main_menu_callback(geometry)
            self.close()
    
    
        
    
    
    
    
        

    
   