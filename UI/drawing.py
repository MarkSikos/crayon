from PyQt6.QtWidgets import QWidget, QMessageBox, QApplication, QColorDialog
from PyQt6.QtGui import QImage, QPainter, QPen, QColor
from PyQt6.QtCore import Qt, QPoint, QRect, pyqtSignal

class DrawingArea(QWidget):
    activeSignal = pyqtSignal(object)  # Signal to emit this DrawingArea as active


    def __init__(self, image_path):
        super().__init__()
        
        ### Egymáson lévő kép rétegek
        self.original_image_path = image_path
        self.original_image = QImage(image_path)  # Load the original image from the path
        self.setFixedSize(self.original_image.size())  # Set the widget size to match the image size
        
        self.temp_image = QImage(self.original_image.size(), QImage.Format.Format_ARGB32_Premultiplied)
        self.temp_image.fill(Qt.GlobalColor.transparent)  # Start with a transparent image for drawing
        
        self.lines_image = QImage(self.original_image.size(), QImage.Format.Format_ARGB32_Premultiplied)
        self.lines_image.fill(Qt.GlobalColor.white)  # Start with a transparent image for lines
        self.drawPermanentLines()
        
        
        self.drawing = False
        self.current_tool = 'brush'  # Initialize with 'brush' to avoid NULL value
        self.tool_sizes = {'brush': 5, 'eraser': 10}
        
        self.undo_stack = []  # Initialize the undo stack
        self.lastPoint = QPoint()
        self.brushColor = Qt.GlobalColor.black
        
        self.selection_start = None
        self.selection_end = None
        self.is_selecting = False
        
        self.activeSignal.emit(self)

    def setTool(self, tool):
        if tool == 'select':
            self.is_selecting = True
        else:
            self.is_selecting = False
        self.current_tool = tool
        
    def adjustToolSize(self, size):
        # Adjust the size of the current tool
        self.tool_sizes[self.current_tool] = size
        # No need to call update here unless you have a specific reason to redraw the widget at this point

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.activeSignal.emit(self) 
        if self.is_selecting and event.button() == Qt.MouseButton.LeftButton:
            self.selection_start = event.position().toPoint()
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.drawing = True
            self.lastPoint = event.position().toPoint()
            self.undo_stack.append(self.temp_image.copy())  # Save the current state before drawing

    from PyQt6.QtGui import QPainter

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.drawing:
            if self.current_tool == 'select':
                # Handle selection logic here
                self.selection_end = event.position().toPoint()
            else:
                # For other tools, proceed with drawing logic
                painter = QPainter(self.temp_image)
                if self.current_tool == 'eraser':
                    # Correctly set the eraser to erase content by using a transparent pen
                    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                    painter.setPen(QPen(QColor(0, 0, 0, 0), self.tool_sizes.get(self.current_tool, 10), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
                else:
                    # For the brush, use the selected color
                    painter.setPen(QPen(self.brushColor, self.tool_sizes.get(self.current_tool, 5), Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
                painter.drawLine(self.lastPoint, event.position().toPoint())
                self.lastPoint = event.position().toPoint()
            self.update()  # Update the widget to trigger a repaint



    def mouseReleaseEvent(self, event):
        if self.is_selecting and event.button() == Qt.MouseButton.LeftButton:
            self.copySelectionToClipboard()
        
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.lines_image) 
        painter.drawImage(0, 0, self.original_image)
        
        #self.drawLines(painter)
        #self.drawPermanentLines()
        
        painter.drawImage(0, 0, self.temp_image)
        
        if self.is_selecting and self.selection_start and self.selection_end:
            rect = QRect(self.selection_start, self.selection_end)
            painter.setPen(QPen(Qt.GlobalColor.black, 1, Qt.PenStyle.DashLine))
            painter.drawRect(rect)

    def drawLines(self, painter):
        pen = QPen(QColor(210, 210, 210), 2)  # Light grey color, adjust thickness as needed
        painter.setPen(pen)
        lines_spacing = 30  # Adjust spacing as needed

        # Draw horizontal lines across the canvas
        for y in range(lines_spacing, self.original_image.height(), lines_spacing):
            painter.drawLine(0, y, self.original_image.width(), y)
   
    def copySelectionToClipboard(self):
        if self.selection_start and self.selection_end:
            rect = QRect(self.selection_start, self.selection_end).normalized()
            image = self.original_image.copy(rect)
            QApplication.clipboard().setImage(image)
            self.selection_start = None
            self.selection_end = None
            self.update()  # Clear the selection rectangle
   
    def drawPermanentLines(self):
        painter = QPainter(self.lines_image)
        pen = QPen(QColor(210, 210, 210), 2)  # Light grey color, adjust thickness as needed
        painter.setPen(pen)
        lines_spacing = 30  # Adjust spacing as needed

        # Draw horizontal lines across the canvas
        for y in range(lines_spacing, self.lines_image.height(), lines_spacing):
            painter.drawLine(0, y, self.lines_image.width(), y)

        painter.end()
   
   
    def undo(self):
        if self.undo_stack:
            self.temp_image = self.undo_stack.pop()
            self.update()
        else:
            QMessageBox.information(self, "Undo", "Nothing to undo!")


    def save_changes(self):
        painter = QPainter(self.original_image)
        painter.drawImage(0, 0, self.temp_image)
        painter.end()
        self.original_image.save(self.original_image_path)
        
        def pick_color_for_all(self):
            color = QColorDialog.getColor()
            if color.isValid():
                for drawing_area in self.drawing_areas:
                    drawing_area.brushColor = color
