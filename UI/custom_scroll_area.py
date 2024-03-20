from PyQt6.QtWidgets import QScrollArea, QVBoxLayout, QLabel
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QWheelEvent
from PyQt6.QtCore import QEvent



class CustomScrollArea(QScrollArea):
    
    
    def __init__(self, *args, **kwargs):
        super(CustomScrollArea, self).__init__(*args, **kwargs)
        self.progress = 0
        self.timer = QTimer(self)
        self.timer.setInterval(100)  # Adjust as needed
        self.timer.timeout.connect(self.increase_progress)
        self.atBottom = False


    

    def wheelEvent(self, event: QWheelEvent):
        super().wheelEvent(event)
        # Check if at bottom
        if self.verticalScrollBar().value() == self.verticalScrollBar().maximum():
            if event.angleDelta().y() < 0:  # Scrolling down
                if not self.atBottom:
                    self.atBottom = True
                    self.timer.start()
            else:  # Scrolling up
                self.reset_progress()
        else:
            self.reset_progress()

    def increase_progress(self):
        self.progress += 10  # Increment progress
        print("Progress:", self.progress)  # Placeholder action
        if self.progress >= 100:  # Threshold reached
            self.timer.stop()
            print("Threshold reached. Create a new PNG file.")
            self.emit_signal_new_png()  # Function to handle new PNG file creation
            self.reset_progress()

    def reset_progress(self):
        self.progress = 0
        self.atBottom = False
        self.timer.stop()

    def emit_signal_new_png(self):
        # Create an instance of QEvent with our custom event type
        event = QEvent(CreatePngEventType)
        
        # Post this event to the ImageViewWindow
        QApplication.postEvent(self.parentWidget(), event)
