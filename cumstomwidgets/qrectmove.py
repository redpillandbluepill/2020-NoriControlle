from enum import Enum

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class Mode(Enum):
    NONE = 0,
    MOVE = 1,
    RESIZETL = 2,
    RESIZET = 3,
    RESIZETR = 4,
    RESIZER = 5,
    RESIZEBR = 6,
    RESIZEB = 7,
    RESIZEBL = 8,
    RESIZEL = 9


class QRectMove(QWidget):
    """ allow to move and resize by user"""
    menu = None
    mode = Mode.NONE
    position = None
    inFocus = pyqtSignal(bool)
    outFocus = pyqtSignal(bool)
    newGeometry = pyqtSignal(QRect)
    lastGeometry = pyqtSignal(QRect, str)

    def __init__(self, parent, pos, size, cWidget):
        super().__init__(parent=parent)
        self.resize(size.x(), size.y())
        self.setAttribute(Qt.WA_DeleteOnClose, True)
        self.setVisible(True)
        self.setAutoFillBackground(False)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.ClickFocus)
        self.setFocus()
        self.move(pos)

        self.vLayout = QVBoxLayout(self)
        self.setChildWidget(cWidget)

        self.m_infocus = True
        self.m_showMenu = False
        self.m_isEditing = True
        self.installEventFilter(parent)

    def setChildWidget(self, cWidget):
        if cWidget:
            self.childWidget = cWidget
            self.childWidget.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            self.childWidget.setParent(self)
            self.childWidget.releaseMouse()
            self.vLayout.addWidget(cWidget)
            self.vLayout.addStretch(1)
            #self.vLayout.setContentsMargins(0,0,0,0)

    def focusInEvent(self, a0: QFocusEvent):
        self.m_infocus = True
        p = self.parentWidget()
        p.installEventFilter(self)
        p.repaint()
        self.inFocus.emit(True)

    def focusOutEvent(self, a0: QFocusEvent):
        if not self.m_isEditing:
            return
        if self.m_showMenu:
            return
        self.mode = Mode.NONE
        self.outFocus.emit(False)
        self.m_infocus = False

    def paintEvent(self, e: QPaintEvent):
        painter = QPainter(self)
        color = (r, g, b, a) = (0, 0, 255, 30)

        rect = e.rect()
        rect.adjust(0, 0, -1, -1)
        painter.setPen(QColor(r, g, b))
        painter.drawRect(rect)

    def mousePressEvent(self, e: QMouseEvent):
        self.position = QPoint(e.globalX() - self.geometry().x(), e.globalY() - self.geometry().y())
        if not self.m_isEditing:
            return
        if not self.m_infocus:
            return
        if not e.buttons() and Qt.LeftButton:
            self.setCursorShape(e.pos())
            return
        if e.button() == Qt.RightButton:
            self.popupShow(e.pos())
            e.accept()

    def keyPressEvent(self, e: QKeyEvent):
        if not self.m_isEditing: return
        if e.key() == Qt.Key_Delete:
            self.deleteLater()
        # Moving container with arrows
        if QApplication.keyboardModifiers() == Qt.ControlModifier:
            newPos = QPoint(self.x(), self.y())
            if e.key() == Qt.Key_Up:
                newPos.setY(newPos.y() - 1)
            if e.key() == Qt.Key_Down:
                newPos.setY(newPos.y() + 1)
            if e.key() == Qt.Key_Left:
                newPos.setX(newPos.x() - 1)
            if e.key() == Qt.Key_Right:
                newPos.setX(newPos.x() + 1)
            self.move(newPos)

        if QApplication.keyboardModifiers() == Qt.ShiftModifier:
            if e.key() == Qt.Key_Up:
                self.resize(self.width(), self.height() - 1)
            if e.key() == Qt.Key_Down:
                self.resize(self.width(), self.height() + 1)
            if e.key() == Qt.Key_Left:
                self.resize(self.width() - 1, self.height())
            if e.key() == Qt.Key_Right:
                self.resize(self.width() + 1, self.height())
        self.newGeometry.emit(self.geometry())


    def setCursorShape(self, e_pos: QPoint):
        diff = 3
        # Left - Bottom

        if (((e_pos.y() > self.y() + self.height() - diff) and # Bottom
            (e_pos.x() < self.x() + diff)) or # Left
        # Right-Bottom
        ((e_pos.y() > self.y() + self.height() - diff) and # Bottom
        (e_pos.x() > self.x() + self.width() - diff)) or # Right
        # Left-Top
        ((e_pos.y() < self.y() + diff) and # Top
        (e_pos.x() < self.x() + diff)) or # Left
        # Right-Top
        (e_pos.y() < self.y() + diff) and # Top
        (e_pos.x() > self.x() + self.width() - diff)): # Right
            # Left - Bottom
            if ((e_pos.y() > self.y() + self.height() - diff) and # Bottom
            (e_pos.x() < self.x()
                + diff)): # Left
                self.mode = Mode.RESIZEBL
                self.setCursor(QCursor(Qt.SizeBDiagCursor))
                # Right - Bottom
            if ((e_pos.y() > self.y() + self.height() - diff) and # Bottom
            (e_pos.x() > self.x() + self.width() - diff)): # Right
                self.mode = Mode.RESIZEBR
                self.setCursor(QCursor(Qt.SizeFDiagCursor))
            # Left - Top
            if ((e_pos.y() < self.y() + diff) and # Top
            (e_pos.x() < self.x() + diff)): # Left
                self.mode = Mode.RESIZETL
                self.setCursor(QCursor(Qt.SizeFDiagCursor))
            # Right - Top
            if ((e_pos.y() < self.y() + diff) and # Top
            (e_pos.x() > self.x() + self.width() - diff)): # Right
                self.mode = Mode.RESIZETR
                self.setCursor(QCursor(Qt.SizeBDiagCursor))
        # check cursor horizontal position
        elif ((e_pos.x() < self.x() + diff) or # Left
            (e_pos.x() > self.x() + self.width() - diff)): # Right
            if e_pos.x() < self.x() + diff: # Left
                self.setCursor(QCursor(Qt.SizeHorCursor))
                self.mode = Mode.RESIZEL
            else: # Right
                self.setCursor(QCursor(Qt.SizeHorCursor))
                self.mode = Mode.RESIZER
        # check cursor vertical position
        elif ((e_pos.y() > self.y() + self.height() - diff) or # Bottom
            (e_pos.y() < self.y() + diff)): # Top
            if e_pos.y() < self.y() + diff: # Top
                self.setCursor(QCursor(Qt.SizeVerCursor))
                self.mode = Mode.RESIZET
            else: # Bottom
                self.setCursor(QCursor(Qt.SizeVerCursor))
                self.mode = Mode.RESIZEB
        else:
            self.setCursor(QCursor(Qt. ArrowCursor))
            self.mode = Mode.MOVE

    def mouseReleaseEvent(self, e: QMouseEvent):
        QWidget.mouseReleaseEvent(self, e)
        self.lastGeometry.emit(self.geometry(), self.childWidget.text())

    def mouseMoveEvent(self, e: QMouseEvent):
        QWidget.mouseMoveEvent(self, e)
        if not self.m_isEditing:
            return
        if not self.m_infocus:
            return
        if not e.buttons() and Qt.LeftButton:
            p = QPoint(e.x() + self.geometry().x(), e.y() + self.geometry().y())
            self.setCursorShape(p)
            return

        if (self.mode == Mode.MOVE or self.mode == Mode.NONE) and e.buttons() and Qt.LeftButton:
            toMove = e.globalPos() - self.position
            if toMove.x() < 0:return
            if toMove.y() < 0:return
            if toMove.x() > self.parentWidget().width() - self.width(): return
            self.move(toMove)
            self.newGeometry.emit(self.geometry())
            self.parentWidget().repaint()
            return
        if (self.mode != Mode.MOVE) and e.buttons() and Qt.LeftButton:
            if self.mode == Mode.RESIZETL: # Left - Top
                newwidth = e.globalX() - self.position.x() - self.geometry().x()
                newheight = e.globalY() - self.position.y() - self.geometry().y()
                toMove = e.globalPos() - self.position
                self.resize(self.geometry().width() - newwidth, self.geometry().height() - newheight)
                self.move(toMove.x(), toMove.y())
            elif self.mode == Mode.RESIZETR: # Right - Top
                newheight = e.globalY() - self.position.y() - self.geometry().y()
                toMove = e.globalPos() - self.position
                self.resize(e.x(), self.geometry().height() - newheight)
                self.move(self.x(), toMove.y())
            elif self.mode== Mode.RESIZEBL: # Left - Bottom
                newwidth = e.globalX() - self.position.x() - self.geometry().x()
                toMove = e.globalPos() - self.position
                self.resize(self.geometry().width() - newwidth, e.y())
                self.move(toMove.x(), self.y())
            elif self.mode == Mode.RESIZEB: # Bottom
                self.resize(self.width(), e.y())
            elif self.mode == Mode.RESIZEL: # Left
                newwidth = e.globalX() - self.position.x() - self.geometry().x()
                toMove = e.globalPos() - self.position
                self.resize(self.geometry().width() - newwidth, self.height())
                self.move(toMove.x(), self.y())
            elif self.mode == Mode.RESIZET:# Top
                newheight = e.globalY() - self.position.y() - self.geometry().y()
                toMove = e.globalPos() - self.position
                self.resize(self.width(), self.geometry().height() - newheight)
                self.move(self.x(), toMove.y())
            elif self.mode == Mode.RESIZER: # Right
                self.resize(e.x(), self.height())
            elif self.mode == Mode.RESIZEBR:# Right - Bottom
                self.resize(e.x(), e.y())
            self.parentWidget().repaint()
        self.newGeometry.emit(self.geometry())


class MainWindow(QGroupBox):
    def __init__(self):
        super().__init__()
        self.resize(1000, 500)

        lab1 = QLabel("1")
        lab1.setStyleSheet('''
            font-size: 20px;
            font-weight: bold;
            color: blue;
        ''')
        lab2 = QLabel("2")
        lab2.setStyleSheet('''
            font-size: 20px;
            font-weight: bold;
            color: blue;
        ''')

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        #self.label.setAttribute(Qt.WA_TransparentForMouseEvents)
        pixmap = QPixmap('images/button.png').scaled(560, 440)
        self.label.setPixmap(pixmap)
        self.label.mousePressEvent = self.mousePressEvent

        v_box = QVBoxLayout()
        v_box.addSpacing(20)
        v_box.addWidget(self.label, alignment=Qt.AlignCenter)
        v_box.addSpacing(20)
        self.setLayout(v_box)

        con1 = QRectMove(self.label, QPoint(10, 10), lab1)
        con2 = QRectMove(self.label, QPoint(110, 110), lab2)

        con1.newGeometry.connect(self.test)

        self.show()

    def test(self, geometry):
        print(geometry.x(), geometry.y(), geometry.width(), geometry.height())
        # 좌표!!
        begin = QPoint(geometry.x(), geometry.y())
        end = QPoint(geometry.x() + geometry.width(), geometry.y() + geometry.height())
        print(begin, end)



#
# if __name__ == '__main__':
#     app = QApplication(sys.argv)
#     ex = MainWindow()
#     sys.exit(app.exec_())