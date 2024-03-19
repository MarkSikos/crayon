from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QImage, QPainter, QPen, QPixmap
from PyQt6.QtCore import Qt, QPoint

class DrawingArea(QWidget):
    def __init__(self, image_path):
        super().__init__()
        self.original_image_path = image_path
        self.original_image = QImage(image_path)  # Load the original image from the path
        self.setFixedSize(self.original_image.size())  # Set the widget size to match the image size
        
        # Create a QImage to hold the temporary drawing. It should be the same size as the original image.
        self.temp_image = QImage(self.original_image.size(), QImage.Format.Format_ARGB32_Premultiplied)
        self.temp_image.fill(Qt.GlobalColor.transparent)  # Start with a transparent image for drawing
        
        self.drawing = False
        self.brushSize = 5
        self.brushColor = Qt.GlobalColor.black
        self.lastPoint = QPoint()

    def mousePressEvent(self, event):
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.drawing = True
            self.lastPoint = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.drawing:
            painter = QPainter(self.temp_image)
            painter.setPen(QPen(self.brushColor, self.brushSize, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
            painter.drawLine(self.lastPoint, event.position().toPoint())
            self.lastPoint = event.position().toPoint()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drawing = False

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.original_image)  # Draw the original image
        painter.drawImage(0, 0, self.temp_image)  # Draw the temporary image (drawings) on top

    # Add other necessary methods and functionality...
