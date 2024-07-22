from PyQt6.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QMessageBox, QFrame, QLabel, QToolButton, QSizePolicy
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt, QSize
from Modell.Logic.DrawingArea import DrawingArea
from Modell.UtilityModules.Exercise import ExerciseConfig
from Modell.Logic.ImageManager import ImageManager
from View.EditorWindow import EditorWindow
from Modell.Logic.OCRUtils import OCRUtils
from Modell.Logic.ExerciseManager import ExerciseManager
from Modell.UtilityModules.StyleSheetUtilities import StyleSheetUtilities

CSS_PATH = "Persistence/style/editor_window_style.css"

class ExerciseWriter(EditorWindow):
    """
    This class manages the UI of the ExerciseWriter that is responsible for the handling of tasks. 
    """
    
    # Constructor
    
    def __init__(self, test_id, test_name, user_role, user_id,  go_back_callback, exercise_type, geometry, ocr_utils):
        super().__init__(go_back_callback=go_back_callback)
        self._drawing_areas = list()
        self._exercise_id = test_id
        self._OCR = ocr_utils
        self._OCR.recognition_started.connect(self._update_label_title)
        self._test_name = test_name
        self._title_label = self._test_name
        self._user_id = user_id
        self._saved = True
        self._exercise_type = exercise_type
        self._table = "test" if self._exercise_type == ExerciseConfig.TEST else "homework"
        self._go_back_callback = go_back_callback
        self._half_screen_width = QApplication.primaryScreen().size().width() / 2
        self._half_screen_height = QApplication.primaryScreen().size().height() / 2
        self.__init_ui()
        self.setGeometry(geometry)
        self.show()
        
    # UI initialization
    
    def __init_ui(self):
        """ Creates the UI. """
        self.setWindowTitle("Crayon")
        StyleSheetUtilities.load_stylesheet(self,CSS_PATH)
        self._result_label = QLabel(" There are no evaluated answers yet. ")
        self._result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._result_label.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        self._setup_central_widget()
        self._add_title_label()
        self._check_button = QToolButton()
        self._check_button.setIcon(QIcon("Assets/check_icon.png"))
        self._check_button.setIconSize(QSize(self._half_screen_width/20, self._half_screen_width/20))
        self._add_controls([self._check_button])     
        self._check_button.clicked.connect(lambda: self._check_manager(ExerciseManager.get_exercise_paths(self._exercise_id, self._table, self._user_id), ExerciseManager.get_exercise_answers(self._exercise_id, self._table, self._user_id)))
        line1 = QFrame()
        line2 = QFrame()
        line3 = QFrame()
        line1.setFrameShape(QFrame.Shape.HLine)
        line2.setFrameShape(QFrame.Shape.HLine)
        line3.setFrameShape(QFrame.Shape.HLine)
        line1.setFrameShadow(QFrame.Shadow.Sunken)
        line2.setFrameShadow(QFrame.Shadow.Sunken)
        line3.setFrameShadow(QFrame.Shadow.Sunken)
        self._main_layout.addWidget(line1)
        self._question_title = QLabel("Kérdések")
        self._question_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._question_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        self._main_layout.addWidget(self._question_title)
        self._main_layout.addWidget(line2)
        self._add_scroll_area()
        self._main_layout.addWidget(line3)
        self._add_large_drawing_area()
        
    def _add_scroll_area(self):
        """ Creates a ScrollArea. """
        scroll_area = QScrollArea()
        scroll_area.setMinimumHeight(300)
        scroll_area.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_area.setWidget(scroll_widget)
        scroll_layout = QVBoxLayout(scroll_widget)
        self.__load_questions(scroll_layout)
        self._main_layout.addSpacing(40)
        self._main_layout.addWidget(scroll_area)
        self._main_layout.addSpacing(40)

    def _add_large_drawing_area(self):
        """ Adds a DrawingArea to the UI. """
        self._large_drawing_area = self.__load_large_drawing_area()
        self._drawing_areas.append(self._large_drawing_area)
        self._large_drawing_area.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        v_layout = QVBoxLayout()
        h0_layout = QHBoxLayout()
        evaluation_label = QLabel("Evaluation Status")
        evaluation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        evaluation_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        h0_layout.addWidget(evaluation_label)
        notes_label = QLabel("Comments")
        notes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        notes_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        h0_layout.addWidget(notes_label)
        h1_layout = QHBoxLayout()
        h1_layout.addWidget(self._result_label)
        h1_layout.addWidget(self._large_drawing_area)
        v_layout.addLayout(h0_layout)
        v_layout.addLayout(h1_layout)
        self._main_layout.addLayout(v_layout)
        
    def __load_large_drawing_area(self):
        """ Loads and/or initializes the bigger DrawingArea at the bottom, with the URL from the database. """
        result = ImageManager.get_large_image(self._table, self._exercise_id, self._user_id)
        if not result or not result[0]:
            raise ValueError("The picture does not exist.")
        large_drawing_area = DrawingArea(result[0], 
                           lambda path, image_id=0: ImageManager.save_new_image_to_exercise(path, self._exercise_id, self._user_id, self._table, image_id),
                           image_id=0)
        large_drawing_area.drawing_ended.connect(self._handle_exercise_edited)
        large_drawing_area.setFixedSize(self._half_screen_width * 0.8, self._half_screen_height * 0.8)
        large_drawing_area.drawing_active.connect(lambda da=large_drawing_area: self._set_last_active_drawing_area(da))
        return large_drawing_area

    def __load_questions(self, layout):
        """ Gathers the questions from the database for the tests/homeworks. """
        question_data = ImageManager.get_question_data(self._table,self._exercise_id, self._user_id)
        self.__append_questions(question_data, layout)
            
    def __append_questions(self,question_data, layout):
        """ Adds the questions and the DrawingAreas to the scrollLayout."""
        if question_data: 
            for question, _, image_path, image_id in question_data:
                question_layout = QHBoxLayout()  
                question_label = QToolButton()
                question_label.setMinimumWidth(self._half_screen_width*0.7)
                question_label.setText(question)
                question_label.setStyleSheet("QToolButton { background-color: white; border-radius: 10px; \
                                                 padding: 6px; font-family: Segoe UI; font-size: 16px; }")
                question_layout.addWidget(question_label)
                drawing_area = DrawingArea(image_path, lambda path, image_id =image_id: ImageManager.save_new_image_to_exercise(path,self._exercise_id, self._user_id, self._table, image_id ), image_id)
                drawing_area.drawing_active.connect(lambda da=drawing_area: self._set_last_active_drawing_area(da))
                drawing_area.drawing_ended.connect(self._handle_exercise_edited)
                self._drawing_areas.append(drawing_area)
                question_layout.addWidget(drawing_area, Qt.AlignmentFlag.AlignRight)               
                layout.addLayout(question_layout)  
                layout.addSpacing(20)
        else:
            no_questions_label = QLabel("No questions were added to this test. ")
            no_questions_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_questions_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
            layout.addWidget(no_questions_label)
    
    def _save_all_drawings(self):
        """ Starts the saving process for all drawingArea-s. """
        for drawing_area in self._drawing_areas:
            drawing_area.save_changes()
        self._saved = True
             
    def _check_manager(self,paths, answers):
        """ Responsible for the communication with teh OCR Module."""
        self._save_all_drawings()
        self._result_label.setText("Evaluation in Progress...")
        result_label_text = ""
        image_counter = 1
        correct_result_counter = 0
    
        for i in range(len(paths)):
            result_text = f" {image_counter}. question - Answer could not be processed. The correct answer: {answers[i][0]}"
            result = self._OCR.recognize_text_test(paths[i], answers[i])
            flattened = self.__flatten(result)
            if None in flattened: 
                if not all(item is None for item in flattened):
                    if answers[i][0] in flattened:
                        result_text = f" {image_counter}. question - Correct answer! The answer is indeed {answers[i][0]}"
                        correct_result_counter = correct_result_counter + 1
                else:  
                 result_text = f" {image_counter}. question - Answer could not be processed. The correct answer: {answers[i][0]}"
            else:
                string_only_list = [item for item in flattened if isinstance(item, str)]
                flattened = [s.lower() for s in string_only_list]
                if answers[i][0] in flattened:
                    result_text = f" {image_counter}. question - Correct answer! The answer is indeed {answers[i][0]}"
                    correct_result_counter = correct_result_counter + 1
                else:
                    result_text = f" {image_counter}. question - Incorrect answer! The answer is: {answers[i][0]}"
            result_label_text += (result_text + "\n")
            image_counter = image_counter + 1
            
        if(self._table == "homework"):
            self._result_label.setText(result_label_text)
        else:
            self._result_label.setText("The evaluation completed.")
         
        ExerciseManager.add_results(self._table, self._user_id, self._test_name, self._exercise_id, correct_result_counter)
        
    def __flatten(self,nested_list):
        """ _check_manager függvény segédfüggvénye. Egy nem definált listát flattenel, rekurzív módon. """
        flattened_list = []
        for item in nested_list:
            if isinstance(item, list):
                flattened_list.extend(self.__flatten(item))
            else:
                flattened_list.append(item)
        return flattened_list
        
    # Eventhandlers
        
    def _handle_exercise_edited(self):
        """ Egy feladat el nem mentettségét beállító eseménykezelő."""
        self._saved = False
        
    def _update_label_title(self):
        """ Egy feladat kiértékelésének label-jét beállító eseménykezelő. """
        self._result_label.setText("A kiértékelés folyamatban van")
      
    def closeEvent(self, event):
        """ A closeEvent felüldefiniálása, megakadályozza hogy mentés nélkül kilépjünk. """
        if not self._saved:
            reply = QMessageBox.question(self, 'Mentés', "El akarja menteni a változásokat?", 
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,  QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self._save_all_drawings()
                event.accept()  
            elif reply == QMessageBox.StandardButton.No:
                event.accept()  
            else:
                event.ignore()
        else:
            event.accept()
        

        
        

        
        
        
    