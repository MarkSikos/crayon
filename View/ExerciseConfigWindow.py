from PyQt6.QtWidgets import QApplication, QToolButton, QPushButton,  QMainWindow, QVBoxLayout, QHBoxLayout, QLineEdit, QDateEdit, QScrollArea, QWidget, QMessageBox
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QGuiApplication, QIcon
from unidecode import unidecode
import re
from Modell.UtilityModules.ConfigUtils import ConfigUtils
from Modell.UtilityModules.Exercise import ExerciseConfig
from Modell.UtilityModules.StyleSheetUtilities import StyleSheetUtilities
from Modell.Logic.ExerciseConfigWindowManager import ExerciseConfigWindowManager

CSS_PATH = "Persistence/style/exercise_config_window_style.css"

class ExerciseConfigWindow(QMainWindow):
    """
    The ExerciseConfigWindow class manages the UI for configuring/setting and adding tests/homeworks.
    """
    
    # Constructor
    
    def __init__(self, refresh_callback, user_id, exercise_type, geometry, exercise_id=None, editing=False, ):
        super().__init__()
        self.__refresh_callback = refresh_callback
        self.__exercise_id = exercise_id
        self.__user_id = user_id
        self.__editing = editing
        self.__exercise_config_window_manager = ExerciseConfigWindowManager()
        self.__exercise_config_window_manager.exercise_created_succesfully.connect(self.__go_back)
        self.__exercise_config_window_manager.exercise_created_unsuccesfully.connect(self.__handle_unsuccesfull_creation)
        self.__exercise_type = exercise_type
        self.__table = "test" if self.__exercise_type == ExerciseConfig.TEST else "homework"
        self.__half_screen_width = QApplication.primaryScreen().size().width() / 2
        if exercise_id is None:
            self.__exercise_id = ExerciseConfigWindowManager.get_next_id(self.__table)
        StyleSheetUtilities.load_stylesheet(self,CSS_PATH)
        self.__init_ui()
        if self.__editing:
            self.load_existing_data()
        self.show()
        self.setGeometry(geometry)
           
    # UI-setup functions
            
    def __init_ui(self):
        """ Creates the main elements of the UI. """
        self.__create_central_widget()
        self.__create_buttons()
        self.__create_header_layout()
        self.setWindowTitle("Settings")
        
    def __create_central_widget(self):
        """ Creates the central widget to contain other elements. """
        self.__central_widget = QWidget()  
        self.setCentralWidget(self.__central_widget)  
        self.__layout = QVBoxLayout()  
        self.__central_widget.setLayout(self.__layout)  
        
    def __create_buttons(self):
        """ Creates the scrollarea, and sets the buttons. """
        self.__name_edit = QLineEdit()
        self.__name_edit.setPlaceholderText("Cím")
        self.__date_edit = QDateEdit(calendarPopup=True)
        self.__date_edit.setDate(QDate.currentDate())
        self.__date_edit.setDisplayFormat("yyyy-MM-dd")
        self.__add_question_button = QToolButton()
        self.__add_question_button.setText("Új kérdés")
        self.__add_question_button.clicked.connect(self.__add_question)
        self.__add_question_button.setObjectName("addQuestionButton")
        self.__question_list_layout = QVBoxLayout()
        self.__question_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.__question_list_widget = QWidget()
        self.__question_list_widget.setLayout(self.__question_list_layout)
        self.__submit_button = QToolButton()
        self.__submit_button.setText("Mentés")
        self.__submit_button.clicked.connect(self.__create_exercise)
        self.__back_button = QPushButton()
        self.__back_button.setObjectName("backButton")
        self.__back_button.setIcon(QIcon("Assets/back_icon.png"))
        self.__back_button.clicked.connect(self.__go_back)
        self.__back_button.setObjectName("backButton")
        self.__back_button.setIconSize(QSize(self.__half_screen_width/20, self.__half_screen_width/20))
        self.__scroll_area = QScrollArea()
        self.__scroll_area.setWidgetResizable(True)
        self.__scroll_area.setWidget(self.__question_list_widget)

    def __create_header_layout(self):
        """ Creates the header. """
        self.__header_layout = QHBoxLayout()
        self.__header_layout.addWidget(self.__name_edit)
        self.__header_layout.addWidget(self.__date_edit)
        self.__header_layout.addWidget(self.__add_question_button)
        self.__header_layout.addWidget(self.__submit_button)
        self.__header_layout.addWidget(self.__back_button)
        self.__layout.addLayout(self.__header_layout)
        self.__layout.addWidget(self.__scroll_area)
        
    def _clear_questions(self):
        """ Deletes the questions upon loading.  """
        for i in reversed(range(self.__question_list_layout.count())): 
            layout_item = self.__question_list_layout.itemAt(i)
            if layout_item.widget():
                layout_item.widget().deleteLater()
            elif layout_item.layout():
                for j in reversed(range(layout_item.layout().count())): 
                    widget_item = layout_item.layout().itemAt(j).widget()
                    if widget_item:
                        widget_item.deleteLater()
                layout_item.layout().deleteLater()
        
    def load_existing_data(self):
        """ Loads the previously saved data, if editing mode is active. """
        self._clear_questions()
        result = ExerciseConfigWindowManager.load_existing_data(self.__table,self.__exercise_id, self.__user_id)
        exercise_info = result[0]
        question_data = result[1]
        if exercise_info:
                self.__name_edit.setText(exercise_info[0])
                self.__date_edit.setDate(QDate.fromString(exercise_info[1], "yyyy-MM-dd"))
        for question, answer, image_id in question_data:
            if image_id != 0:  
                self.__add_question(question, answer)
                
    def _prepare_exercise_data(self):
        """ Loading saved data in editing mode."""
        questions = []
        answers = []
        for i in range(self.__question_list_layout.count()):
            layout = self.__question_list_layout.itemAt(i).layout()
            if layout:
                question_edit = layout.itemAt(0).widget()
                answer_edit = layout.itemAt(1).widget()
                if question_edit and answer_edit:
                    question_text = question_edit.text()
                    answer_text = answer_edit.text()
                    if question_text.strip() and answer_text.strip():
                        if answer_text != answer_text.replace(" ", ""):
                            QMessageBox.warning(self, "Hiba", "A válasz nem tartalmazhat space-t!")
                            return None, None
                        questions.append(question_text)
                        answers.append(answer_text)
                    else:
                        QMessageBox.warning(self, "Hiba", "Minden kérdést, és választ ki kell tölteni!")
                        return None, None
        return  questions, answers
            
    # Eseménykezelők, és a funkcionalitást megvalósító függvények
    
    def __add_question(self, question_text=None, answer_text=None):
        """ Add a new question. """
        question_layout = QHBoxLayout()
        question_edit = QLineEdit()
        question_edit.setPlaceholderText("Kérdés")
        if question_text: 
            question_edit.setText(question_text)
        answer_edit = QLineEdit()
        answer_edit.setPlaceholderText("Válasz")
        if answer_text:  
            answer_edit.setText(answer_text)
        self.__delete_button = QToolButton()
        self.__delete_button.setText("Törlés")
        self.__delete_button.setObjectName("deleteButton")
        self.__delete_button.clicked.connect(lambda: self.__delete_question(question_layout))
        question_layout.addWidget(question_edit, 1)
        question_layout.addWidget(answer_edit, 1)
        question_layout.addWidget(self.__delete_button)
        self.__question_list_layout.addLayout(question_layout)
        
    def __delete_question(self, question_layout):
        """ Delete a question from the layout. """
        while question_layout.count():
            item = question_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        question_layout.deleteLater()
        
    def __create_exercise(self):
        """ Responsible for the saving functionality, creates a test/homework. """
        exercise_name = self.__name_edit.text()
        exercise_date = self.__date_edit.date().toString("yyyy-MM-dd")
        
        if not exercise_name.strip():
            QMessageBox.warning(self, "Warning", "The title of the test is missing!")
            return
        if len(exercise_name) > 40:
            QMessageBox.warning(self, "Warning", "The test title must not exceed 40 characters!")
            return
        if not self.__is_valid_text(exercise_name):
            QMessageBox.warning(self, "Warning", "The test title should contain only latin1 characters or numbers!")
            return
        screen = QGuiApplication.primaryScreen().geometry()
        questions, answers = self._prepare_exercise_data()
        if questions is None or answers is None:
            return
        answers = [unidecode(word).lower() for word in answers]
        for text in answers:
            if len(text) > 40:
                QMessageBox.warning(self, "Warning", "Each answer has a max 40 characters limit!")
                return
            if not self.__is_valid_text(text):
                QMessageBox.warning(self, "Warning", "The answers should contain only latin1 characters or numbers!")
                return
        for text in questions:
            if len(text) > 100:
                QMessageBox.warning(self, "Warning", "The questions must not exceed 100 characters!")
                return
        self.__exercise_config_window_manager.create_exercise(self.__editing, self.__table, exercise_name, exercise_date, self.__exercise_id,questions, answers,  self.__user_id, screen.height(), screen.width() )
         
    def __is_valid_text(self,text):
        """ Helper function, validates the input."""
        alphabet = r'^[a-zA-Z0-9áéíóöőúüűÁÉÍÓÖŐÚÜ Ű]+$'
        return bool(re.match(alphabet, text))
         
    def __handle_unsuccesfull_creation(self):
        """ Eventhandler of the unsuccesful addition. """
        QMessageBox.warning(self, "Warning", "Two test with the same name cannot be created!")
        
    def __go_back(self):
        """ Eventhandler of the back button. """
        if callable(self.__refresh_callback):
            self.__refresh_callback(self.geometry())
        self.close()
    
