from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QSlider, QColorDialog, QMessageBox, QComboBox, QToolButton
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import Qt,  QSize
from abc import  abstractmethod

CSS_PATH = "Persistence/style/editor_window_style.css"

class EditorWindow(QMainWindow):
    """
    This class is responsible for the editorwindow, where the users may use image editing tools. 
    """
    
    # Constructor
    
    def __init__(self, go_back_callback):
        super().__init__()
        self._user_role = None
        self._user_id = None
        self._note_id = None
        self._subject_id = None
        self._note_name = None
        self._go_back_callback  = go_back_callback
        self._drawing_areas = []
        self._half_screen_width = 0
        self._title_label = None
        self._bursh_size = 2
        self._eraser_size = 2
        self._current_tool = 'brush'
        self._current_color = QColor(0, 0, 0)
        
    # UI-management functions
     
    def _setup_tool_buttons(self):
        """ Sets the button bindings. """
        self._brush_button = QToolButton()
        self._brush_button.setIcon(QIcon("Assets/pen_icon.png"))
        self._brush_button.setIconSize(QSize(self._half_screen_width/20,self._half_screen_width/20 ))
        self._eraser_button = QToolButton()
        self._eraser_button.setIcon(QIcon("Assets/eraser_icon.png"))
        self._eraser_button.setIconSize(QSize(self._half_screen_width/20, self._half_screen_width/20))
        self._color_button = QToolButton()
        self._color_button.setIcon(QIcon("Assets/color_icon.png"))
        self._color_button.setIconSize(QSize(self._half_screen_width/20, self._half_screen_width/20))
        self._undo_button = QToolButton()
        self._undo_button.setIcon(QIcon("Assets/undo_icon.png"))
        self._undo_button.setIconSize(QSize(self._half_screen_width/20, self._half_screen_width/20))
        self._tool_size_slider = QSlider(Qt.Orientation.Horizontal)
        self._tool_size_slider.setMinimum(2)  
        self._tool_size_slider.setMaximum(50) 
        self._tool_size_slider.setValue(2) 
        self._brush_button.clicked.connect(lambda: self._set_tool_for_all('brush'))
        self._eraser_button.clicked.connect(lambda: self._set_tool_for_all('eraser'))
        self._tool_size_slider.valueChanged.connect(self._adjust_tool_size_for_all)
        self._color_button.clicked.connect(self._pick_color_for_all)
        self._undo_button.clicked.connect(self._undo_last_action)
        self._back_button = QToolButton()
        self._back_button.setIcon(QIcon("Assets/back_icon.png"))
        self._back_button.setIconSize(QSize(self._half_screen_width/20, self._half_screen_width/20))
        self._back_button.clicked.connect(self._on_back_clicked)
   
    def _add_controls(self, additional_buttons = None):
        """ Adds the buttons to the layout. """
        self._setup_tool_buttons()
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(self._brush_button)
        controls_layout.addWidget(self._eraser_button)
        controls_layout.addWidget(self._color_button)
        controls_layout.addWidget(self._undo_button)
        controls_layout.addWidget(self._tool_size_slider)
        controls_layout.addWidget(self._back_button)
        if additional_buttons is not None:
            for button in additional_buttons:
                controls_layout.addWidget(button)
        self._main_layout.addLayout(controls_layout)
                
    def _add_title_label(self):
        """ Adds the central label. """
        title_label = QToolButton()
        title_label.setText(self._title_label)
        title_label.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title_label.setObjectName("titleLabel")
        title_label.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self._main_layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

    def _setup_central_widget(self):
        """ Sets the central widget. """
        self._central_widget = QWidget()
        self.setCentralWidget(self._central_widget)
        self._main_layout = QVBoxLayout()
        self._central_widget.setLayout(self._main_layout)
        
    def _clear_layout(self,layout):
        """ Clears teh current layout before update. """
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
    # Eventhandlers
             
    def _pick_color(self):
        """ Opens the color picker tool. """
        color = QColorDialog.getColor()
        if color.isValid():
            self._drawing_area.set_brush_color(color)
            
    def _on_back_clicked(self):
        """ Eventhandler of the back button. """
        self.close()
        self._go_back_callback(self.geometry())
      
    def _set_tool_for_all(self, tool):
        """ Sets the current tools for all DrawingArea instances. """
        self._current_tool = tool
        for drawing_area in self._drawing_areas:
            drawing_area.set_tool(tool)
        if tool == 'brush':
            for drawing_area in self._drawing_areas:
                drawing_area.adjust_tool_size(self._bursh_size)
            self._tool_size_slider.setValue(self._bursh_size)
        elif tool == 'eraser':
            self._tool_size_slider.setValue(self._eraser_size)
            for drawing_area in self._drawing_areas:
                drawing_area.adjust_tool_size(self._eraser_size)
        
    def _adjust_tool_size_for_all(self, size):
        """ Sets the current tool sizes for all DrawingArea instances. """
        if self._drawing_areas is not None and len(self._drawing_areas) >= 1:
            if self._drawing_areas[0].get_tool() == 'brush':
                self._bursh_size = size
            else:
                self._eraser_size = size
        for drawing_area in self._drawing_areas:
            drawing_area.adjust_tool_size(size)
            
    def _pick_color_for_all(self):
        """ Sets the current tool color for all DrawingArea instances. """
        color = QColorDialog.getColor(parent=self)
        self._current_color = color
        if color.isValid():
            for drawing_area in self._drawing_areas:
                drawing_area.set_brush_color(color)
                drawing_area.update()  
                
    def _undo_last_action(self):
        """Eventhandler of the Undo button. """
        if hasattr(self, '_last_active_drawing_area'):
            self._last_active_drawing_area.undo()
            
    def _set_last_active_drawing_area(self, input_drawing_area):
        """ Sets the last DrawingArea instance."""
        self._last_active_drawing_area = input_drawing_area
        
    # Getter functions
    
    def _get_current_tool(self):
        return self._current_tool
        
    # Abstract functions
    
    @abstractmethod
    def _save_all_drawings(self):
        """ Saves all changes on all DrawingArea instances. """
        raise NotImplementedError("The function is not implemented.")
        
    @abstractmethod   
    def _add_scroll_area(self):
        """ Adds a scrollarea instance, where the DrawingArea-s are displayed. """
        raise NotImplementedError("The function is not implemented.")
        
        
    

            
            
        
            
        
            
                    
                    
            
        