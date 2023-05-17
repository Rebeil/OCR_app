import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import ImageGrab
from PyQt5.QtCore import pyqtSignal, QRectF
from PyQt5.QtGui import QPixmap, QPainterPath
from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QFileDialog, QSizePolicy, QTextEdit, QPushButton, \
    QHBoxLayout, QGridLayout, QVBoxLayout


class SnippingWidget(QtWidgets.QMainWindow):
    closed = pyqtSignal()

    def __init__(self, parent=None):
        super(SnippingWidget, self).__init__(parent)
        # self.setAttribute(QtCore.Qt.WA_NoSystemBackground, False)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        # self.setStyleSheet("background:transparent;")
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        self.outsideSquareColor = "red"
        self.squareThickness = 0

        self.start_point = QtCore.QPoint()
        self.end_point = QtCore.QPoint()

    def mousePressEvent(self, event):
        self.start_point = event.pos()
        self.end_point = event.pos()
        print(f'Позиция нажатия: {self.start_point, self.end_point}')
        self.update()

    def mouseMoveEvent(self, event):
        self.end_point = event.pos()
        print(f'Позиция перемещения: {self.end_point}')
        self.update()

    def mouseReleaseEvent(self, QMouseEvent):
        r = QtCore.QRect(self.start_point, self.end_point).normalized()
        self.hide()
        try:
            img = ImageGrab.grab(bbox=r.getCoords())
            img.save("testpic/testImage.png")
            QtWidgets.QApplication.restoreOverrideCursor()
            self.closed.emit()
            self.start_point = QtCore.QPoint()
            self.end_point = QtCore.QPoint()
            print(f'Позиция остановки: {self.end_point}')
        except AttributeError as e:
            print("кпввар", e)

    def paintEvent(self, event):
        # trans = QtGui.QColor(22, 100, 233)
        r = QtCore.QRectF(self.start_point + QtCore.QPoint(-1, -1), self.end_point).normalized()
        qp = QtGui.QPainter(self)
        # trans.setAlphaF(0.2)
        # qp.setBrush(trans)
        outer = QtGui.QPainterPath()
        outer.addRect(QtCore.QRectF(self.rect()))
        inner = QtGui.QPainterPath()
        inner.addRect(r)
        r_path = outer - inner
        qp.drawPath(r_path)
        qp.setPen(
            QtGui.QPen(QtGui.QColor(self.outsideSquareColor), self.squareThickness)
        )
        # trans.setAlphaF(0)
        # qp.setBrush(trans)
        qp.drawRect(r)


class MyView(QGraphicsView):
    def __init__(self, *args):
        QGraphicsView.__init__(self, *args)
        self.angle_of_rotate_image = 0

    def slotRotateLeft(self):
        """
        поворот против часовой стрелки на 5 градусов
        :return:
        """
        self.rotate(-5)
        self.angle_of_rotate_image += 5

    def slotRotateRight(self):
        """
        поворот по часовой стрелки на 5 градусов
        :return:
        """
        self.rotate(5)
        self.angle_of_rotate_image -= 5

    def reset_angle(self):
        """
        сброс поворота изображения
        :return:
        """
        self.rotate(self.angle_of_rotate_image)
        self.angle_of_rotate_image = 0


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.pixmap = None
        self.centralWidget = QtWidgets.QWidget()
        self.centralWidget.setStyleSheet("background-color: rgb(153, 193, 241);")
        self.setCentralWidget(self.centralWidget)

        # политика размера для кнопок
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

        # region виджет изображения(scene)
        self.scene = QGraphicsScene()
        self.view = MyView(self.scene)
        # endregion

        # region Кнопка выделить область(btn_select_area)
        self.btn_select_area = QtWidgets.QPushButton('Выделить область')
        self.btn_select_area.clicked.connect(self.activateSnipping)
        self.btn_select_area.setStyleSheet("background-color: rgb(255, 47, 253);")
        self.btn_select_area.setShortcut(QtCore.Qt.ALT + QtCore.Qt.Key_Q)
        # endregion

        # region правый верхний виджет(text_view)
        self.text_view = QTextEdit()
        # endregion

        # region кнопка загрузить изображение(open_btn)
        self.open_btn = QPushButton()
        self.open_btn.setText('Загрузить изображение')
        self.open_btn.setStyleSheet("background-color: rgb(237, 51, 59);")
        self.open_btn.clicked.connect(self.show_image)
        # endregion

        # region Выгрузить текст(btn_upload_text)
        self.btn_upload_text = QPushButton()
        self.btn_upload_text.setText('Выгрузить текст')
        self.btn_upload_text.setStyleSheet("background-color: rgb(145, 65, 172);")
        self.btn_upload_text.clicked.connect(self.upload_text)
        # endregion

        # region Очистить вывод(btn_clean_output)
        self.btn_clean_output = QPushButton()
        self.btn_clean_output.setText('Очистить вывод')
        self.btn_clean_output.setStyleSheet("background-color: rgb(87, 227, 137);")
        self.btn_clean_output.clicked.connect(self.clean_output)
        # endregion

        # region Сбросить поворот(btn_reset_angle)
        self.btn_reset_angle = QPushButton()
        self.btn_reset_angle.setText('Сбросить поворот')
        self.btn_reset_angle.setStyleSheet("background-color: rgb(128, 128, 137);")
        self.btn_reset_angle.setEnabled(True)
        self.btn_reset_angle.clicked.connect(self.view.reset_angle)
        self.btn_reset_angle.setSizePolicy(sizePolicy)
        self.btn_reset_angle.setMaximumHeight(50)
        # endregion

        # region Распознать(btn_recognize_text)
        self.btn_recognize_text = QPushButton()
        self.btn_recognize_text.setText('Распознать')
        self.btn_recognize_text.setStyleSheet("background-color: rgb(255, 228, 92);")
        self.btn_recognize_text.clicked.connect(self.recognize_text)
        # endregion

        # region Повернуть изображение(layout_flip_the_image)
        self.layout_flip_the_image = QHBoxLayout()
        # self.layout_flip_the_image.setStyleSheet("background-color: rgb(248, 228, 255);")
        # endregion

        # region левый нижний виджет(layout_lower_left)
        self.layout_lower_left = QVBoxLayout()

        self.layout_lower_left.addWidget(self.open_btn, 5)
        self.open_btn.setSizePolicy(sizePolicy)
        self.open_btn.setMaximumHeight(50)

        self.layout_lower_left.addWidget(self.btn_recognize_text, 5)
        self.btn_recognize_text.setSizePolicy(sizePolicy)
        self.btn_recognize_text.setMaximumHeight(50)

        self.layout_lower_left.addWidget(self.btn_select_area, 5)
        self.btn_select_area.setSizePolicy(sizePolicy)
        self.btn_select_area.setMaximumHeight(50)
        # endregion

        # region правый нижний виджет(layout_lower_right)
        self.layout_lower_right = QVBoxLayout()
        self.layout_lower_right.addWidget(self.btn_clean_output, 50)
        self.btn_clean_output.setSizePolicy(sizePolicy)  # установка политики размера
        self.btn_clean_output.setMaximumHeight(50)  # установка максимального размера кнопки

        self.layout_lower_right.addWidget(self.btn_upload_text, 50)
        self.btn_upload_text.setSizePolicy(sizePolicy)  # установка политики размера
        self.btn_upload_text.setMaximumHeight(50)  # установка максимального размера кнопки

        self.layout_lower_right.addLayout(self.layout_flip_the_image)
        # endregion

        # region главный виджет(gridlayout)
        self.grid = QGridLayout(self.centralWidget)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(0)
        # endregion

        # layout = QtWidgets.QVBoxLayout(self.centralWidget)
        # layout.addWidget(self.view, 1)
        # layout.addWidget(self.button, 0)
        # layout.addWidget(self.open_btn, 0)

        self.layout_up_left = QHBoxLayout()
        ########
        # region кнопка поворота налево
        self.buttonLeft = QPushButton("Поворот \nналево")
        self.buttonLeft.setStyleSheet("background-color: rgb(12, 40, 90);")
        self.buttonLeft.setSizePolicy(sizePolicy)
        self.buttonLeft.setMaximumHeight(50)
        # endregion

        # region кнопка поворота направо
        self.buttonRight = QPushButton("Поворот \nнаправо")
        self.buttonRight.setStyleSheet("background-color: rgb(12, 40, 90);")
        self.buttonRight.setSizePolicy(sizePolicy)
        self.buttonRight.setMaximumHeight(50)
        # endregion

        self.buttonLeft.clicked.connect(self.view.slotRotateLeft)
        self.buttonRight.clicked.connect(self.view.slotRotateRight)

        self.buttonLeft.setEnabled(False)
        self.buttonRight.setEnabled(False)

        # region добавление на лейаут кнопок для манипуляции с изображением
        self.layout_flip_the_image.addWidget(self.buttonLeft)
        self.layout_flip_the_image.addWidget(self.buttonRight)
        self.layout_flip_the_image.addWidget(self.btn_reset_angle)
        # endregion

        # левый верхний виджет
        self.layout_up_left.addWidget(self.view)

        # region добавление виджетов на главный виджет(grid)
        """
                                grid
                |--------------------------------------|
                |    layout_up_left |    text_view     |
                |--------------------------------------|
                | layout_lower_left |layout_lower_right|
                |--------------------------------------|
                """
        self.grid.addLayout(self.layout_up_left, 0, 0)
        self.grid.addWidget(self.text_view, 0, 1)
        self.grid.addLayout(self.layout_lower_left, 1, 0)
        self.grid.addLayout(self.layout_lower_right, 1, 1)
        # endregion

        self.snipper = SnippingWidget()

    def activateSnipping(self):
        """
        выделяет область
        :return:
        """
        self.snipper.showFullScreen()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CrossCursor)
        # self.hide()

    def show_image(self):
        """
        Загружает и отображает изображение в левый верхний виджет(scroll_area)
        :return:
        """

        self.scene.clear()  # очистка сцены

        fileName, _ = QFileDialog.getOpenFileName(self,
                                                  "Open Image", ".",
                                                  "Image Files (*.png *.jpg *.tif);;JPG file (*.jpg);; PNG file ("
                                                  "*.png);; Tif file (*.tif)")
        if fileName:
            self.pixmap = QPixmap(fileName)
            if not self.pixmap is None:
                self.scene.addPixmap(self.pixmap)
                self.buttonLeft.setEnabled(True)
                self.buttonRight.setEnabled(True)
        # flag = True

    def upload_text(self):
        """
        Выгружает текст в формате .txt
        :return:
        """
        try:
            file, _ = QFileDialog.getSaveFileName(None, "QFileDialog getSaveFileName() Demo",  # file, check
                                                  "", "All Files (*);;Text Files (*.txt)")
            # if check:
            #     print(file)
            try:
                with open(file + '.txt', 'w') as file:
                    file.write(self.text_view.toPlainText())
            except BaseException as e:
                print(e)
        except FileNotFoundError as e:
            print(e)
            sys.exit(app.exec_())
        except FileExistsError as e:
            print(e)
            sys.exit(app.exec_())

    def clean_output(self):
        """
        Очищает текст в верхнем правом виджете(text_view)
        :return:
        """
        self.text_view.setText('')

    def select_an_area(self):
        pass

    def recognize_text(self):
        """
        Распознаёт выделенный символ
        :return:
        """
        pass


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.resize(400, 300)
    w.show()
    sys.exit(app.exec_())
