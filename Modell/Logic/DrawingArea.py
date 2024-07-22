from PyQt6.QtWidgets import QWidget, QMessageBox
from PyQt6.QtGui import QImage, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QPointF
from PyQt6.QtWidgets import QWidget, QMessageBox

MAX_SIZE = 40

class DrawingArea(QWidget):
    """
    A Rajzprogram rajzolási és képszerkesztéi/kezelési logikáját megvalósító osztály.
    """
    
    # Események 
    drawing_active = pyqtSignal()  
    drawing_ended = pyqtSignal()  
    
    # Konstruktor
    
    def __init__(self, image_path, save_new_image_callback, image_id = None):
        super().__init__()
        self.setMouseTracking(True) 
        self.__current_mode = 'empty'
        self.__image_id = image_id
        self.__original_image_path = image_path
        self.__original_image = QImage(image_path)
        self.setFixedSize(self.__original_image.size())  
        self.__save_new_image_callback = save_new_image_callback
        self.__temp_image = QImage(image_path)
        self.__lines_image = QImage(self.__original_image.size(), QImage.Format.Format_ARGB32_Premultiplied)
        self.__lines_image.fill(Qt.GlobalColor.white)  
        self.__dots_image = QImage(self.__original_image.size(), QImage.Format.Format_ARGB32_Premultiplied)
        self.__dots_image.fill(Qt.GlobalColor.white) 
        self.__empty_image = QImage(self.__original_image.size(), QImage.Format.Format_ARGB32_Premultiplied)
        self.__empty_image.fill(Qt.GlobalColor.white)  
        self.__dots_image_visible = False
        self.__lines_image_visible = False
        self.__empty_image_visible = True
        self.__drawing = False
        self.__current_tool = 'brush'  
        self.tool_sizes = {'brush': 2, 'eraser': 2}
        self.__undo_stack = []  
        self.__lastPoint = QPoint()
        self.__brushColor = Qt.GlobalColor.black
        self.drawing_active.emit()

    # Rajzolási logikát meghatározó függvények
    def adjust_tool_size(self, size):
        """ Eszköz méretének beállítása. """
        self.tool_sizes[self.__current_tool] = size   
  
    def draw_permanent_lines(self):
        """ Háttérvonalak rajzolása. """
        painter = QPainter(self.__lines_image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(210, 210, 210), 2) 
        painter.setPen(pen)
        lines_spacing = MAX_SIZE 
        for y in range(lines_spacing, self.__lines_image.height(), lines_spacing):
            painter.drawLine(0, y, self.__lines_image.width(), y)
        painter.end()
        self.update()

    def draw_permanent_dots(self):
        """ Háttérpontok rajzolása. """
        painter = QPainter(self.__dots_image)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        pen = QPen(QColor(210, 210, 210), 2)  
        painter.setPen(pen)
        dots_spacing = MAX_SIZE  
        dot_interval = MAX_SIZE  
        for y in range(dots_spacing, self.__dots_image.height(), dots_spacing):
            x = 0
            while x < self.__dots_image.width():
                painter.drawPoint(x, y)  
                x += dot_interval  
        painter.end()
   
    def undo(self):
        """  A legutóbbi művelet visszavonása. """
        if self.__undo_stack:
            self.__temp_image = self.__undo_stack.pop()
            self.update()
        else:
            QMessageBox.information(self, "Visszavonás", "Nem lehet tovább visszavonni!")

    def save_changes(self ):
        """ A kép változásainak mentése. """
        self.__temp_image.save(self.__original_image_path, "PNG")
        self.__save_new_image_callback(self.__original_image_path, self.__image_id)
    
    def set_drawing_mode(self, mode):
        """ Rajzolási mód beállítása. """
        self.__dots_image_visible = False
        self.__lines_image_visible = False
        self.__empty_image_visible = False
        if mode == 'Vonalak':
            self.__lines_image_visible = True
            self.draw_permanent_lines()
            self.__current_mode = 'lines'
        elif mode == 'Pontok':
            self.__dots_image_visible = True
            self.draw_permanent_dots ()
            self.__current_mode = 'dots'
        elif mode == 'Üres':
            self.__empty_image_visible = True
            self.__current_mode = 'empty'
        self.update()
        
    # Események, illetve a PyQT Események felüldefiniálása:
        
    def paintEvent(self, event):
        """ A widget újrarajzolásának eseménykezelése. """
        painter = QPainter(self)
        if self.__lines_image_visible:
            painter.drawImage(0, 0, self.__lines_image)
        if self.__dots_image_visible:
            painter.drawImage(0, 0, self.__dots_image)
        if self.__empty_image_visible:
            painter.drawImage(0, 0, self.__empty_image) 
        painter.drawImage(0, 0, self.__temp_image)
        
    def mousePressEvent(self, event):
        """ Az egér lenyomásának eseménykezelése. """
        super().mousePressEvent(event)
        self.drawing_active.emit() 
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.__drawing = True
            self.__lastPoint = event.position().toPoint() if isinstance(event.position(), QPointF) else event.position()
            self.__undo_stack.append(self.__temp_image.copy()) 

    def mouseMoveEvent(self, event):
        """ Az egér mozgatásának (rajzolás) eseménykezelése. """
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.__drawing:
            painter_temp = QPainter(self.__temp_image)
            painter_temp.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter_original = QPainter(self.__original_image)
            painter_original.setRenderHint(QPainter.RenderHint.Antialiasing)
            
            if self.__current_tool == 'eraser':
                painter_temp.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                painter_original.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                
            pen = QPen(self.__brushColor, self.tool_sizes.get(self.__current_tool, 5), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin)
            painter_temp.setPen(pen)
            painter_original.setPen(pen)
            start_point = self.__lastPoint
            end_point = event.position().toPoint() if isinstance(event.position(), QPointF) else event.position()
            painter_temp.drawLine(start_point, end_point)
            
            if self.__current_tool == 'eraser':
                painter_original.drawLine(start_point, end_point)
            self.__lastPoint = end_point
            self.update()

    def mouseReleaseEvent(self, event):
        """ Az egér felengedésének eseménykezelése (azaz vége a rajzolásnak). """
        if event.button() == Qt.MouseButton.LeftButton:
            self.__drawing = False
        self.drawing_ended.emit()
        
    # Getterek / Setterek
            
    def set_brush_color(self,color):
        self.__brushColor = color
            
    def set_tool(self, tool):
        self.__current_tool = tool
        
    def get_tool(self):
        return self.__current_tool
    
    def get_image_id(self):
        return self.__image_id
    
    def get_original_image_path(self):
        return self.__original_image_path
    
    def get_current_drawing_mode(self):
        return self.__current_mode
        
    