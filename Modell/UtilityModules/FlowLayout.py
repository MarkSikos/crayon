from PyQt6.QtWidgets import  QLayout, QSizePolicy
from PyQt6.QtCore import QRect, QSize, QPoint, Qt

class FlowLayout(QLayout):
    """
    Egy szimpla QLayout beállításait végző osztály. Mivel ezeket a beállításokat több osztályban is használom, így inkább felülírtam 
    a QLayoutot, és egy saját osztályt definiáltam a főmenő és a feladatok menüinek a layoutjának. 
    Az osztály függvényei a Qt dokumentáció templátejének felahsználásával készült.
    """
    
    # Konstruktor
    
    def __init__(self, parent=None, margin=10, spacing=10):
        super(FlowLayout, self).__init__(parent)
        if parent is not None:
            self.setContentsMargins(margin, margin, margin, margin)
        self.spacing = spacing
        self.itemList = []

    def addItem(self, item):
        """ Egy elem hozzávétele a layouthoz."""
        self.itemList.append(item)

    def count(self):
        """ Elemek számának meghatározása a layoutban."""
        return len(self.itemList)

    def itemAt(self, index):
        """ Egy elem visszaadása megfelelő indexről. """
        if index >= 0 and index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        """ A layout listájának biztonságosan megvalósított pop művelete."""
        if index >= 0 and index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        """ Az átméreteződés beállítása """
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        """ Kocka alak beállítása"""
        return True

    def heightForWidth(self, width):
        """ Magasság meghatározását végző függvény."""
        height = self.doLayout(QRect(0, 0, width, 0), True)
        return height

    def setGeometry(self, rect):
        """ Geometria (méret és hely) beállításának a felüldefiniálása."""
        super(FlowLayout, self).setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        """ A layout minimalizálásának beállítása."""
        return self.minimumSize()

    def minimumSize(self):
        """ A layout minimum méretének a kiszámítása."""
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    def doLayout(self, rect, testOnly):
        """ Az elemek elrendezése a layoutban. """
        x = rect.x()
        y = rect.y()
        lineHeight = 0
        for item in self.itemList:
            wid = item.widget()
            spaceX = self.spacing + wid.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Horizontal)
            spaceY = self.spacing + wid.style().layoutSpacing(QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton, Qt.Orientation.Vertical)
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0
            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())
        return y + lineHeight - rect.y()
