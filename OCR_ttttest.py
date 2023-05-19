import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PIL import ImageGrab
from PyQt5.QtCore import pyqtSignal, QRectF, QRegExp, QObject
from PyQt5.QtGui import QPixmap, QPainterPath, QRegExpValidator
from PyQt5.QtWidgets import (QGraphicsScene, QGraphicsView, QFileDialog, QSizePolicy, QTextEdit, QPushButton,
                             QHBoxLayout, QGridLayout, QVBoxLayout, QPlainTextEdit, QLineEdit, QLCDNumber, QSlider)
from pathlib import Path


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
        """
        Функция отслеживания нажатия ЛКМ
        :param event:
        :return:
        """
        self.start_point = event.pos()
        self.end_point = event.pos()
        print(f'Позиция нажатия: {self.start_point, self.end_point}')
        self.update()

    def mouseMoveEvent(self, event):
        """
        Функция отслеживания перемещения мыши
        :param event:
        :return:
        """
        self.end_point = event.pos()
        print(f'Позиция перемещения: {self.end_point}')
        self.update()

    def mouseReleaseEvent(self, QMouseEvent):
        """
        Функция отслеживания вырезания области изображения
        :param QMouseEvent:
        :return:
        """
        r = QtCore.QRect(self.start_point, self.end_point).normalized()
        self.hide()
        try:
            img = ImageGrab.grab(bbox=r.getCoords())
            try:
                img.save("testpic/testImage.png")
                QtWidgets.QApplication.restoreOverrideCursor()
                self.closed.emit()
                self.start_point = QtCore.QPoint()
                self.end_point = QtCore.QPoint()
                print(f'Позиция остановки: {self.end_point}')
            except SystemError as e:
                print('SystemError', e)

        except AttributeError as e:
            print('AttributeError', e)

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
        self.angle = 5

    def slot_rotate_left(self):
        """
        поворот против часовой стрелки на 5 градусов
        :return:
        """
        self.rotate(-self.angle)
        self.angle_of_rotate_image += self.angle

    def slot_rotate_right(self):
        """
        поворот по часовой стрелки на 5 градусов
        :return:
        """
        self.rotate(self.angle)
        self.angle_of_rotate_image -= self.angle

    def reset_angle(self):
        """
        сброс поворота изображения
        :return:
        """
        self.rotate(self.angle_of_rotate_image)
        self.angle_of_rotate_image = 0


class Communicate(QObject):
    end_enter = pyqtSignal()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # region private varable
        tmp = 180  # максимальный размер нижних лэйаутов
        self.__max_height_size_of_widget_left_down_layout = tmp // 3
        self.__max_height_size_of_widget_right_down_layout = tmp // 4
        # endregion

        # region политика размера для кнопок(sizePolicy)
        size_policy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)
        # endregion

        self.pixmap = None

        # region главный виджет(centralWidget)
        self.centralWidget = QtWidgets.QWidget()
        self.centralWidget.setStyleSheet("background-color: rgb(153, 193, 241);")
        self.setCentralWidget(self.centralWidget)
        # endregion

        # region виджет изображения(scene)
        self.scene = QGraphicsScene()
        self.view = MyView(self.scene)
        self.view.setMinimumSize(300, 400)  # установка минимального размера
        # endregion

        # region слайдер QSlider(sld)
        # self.lcd = QLCDNumber(self)
        # self.lcd.setSegmentStyle(QLCDNumber.Flat)

        self.sld = QSlider(QtCore.Qt.Horizontal, self)
        self.sld.setValue(self.view.angle)
        self.sld.setSizePolicy(size_policy)
        self.sld.setMinimumHeight(25)
        self.sld.setMaximumHeight(self.__max_height_size_of_widget_right_down_layout)
        self.sld.setMaximum(360)
        self.sld.setEnabled(False)

        # self.sld.valueChanged.connect(self.lcd.display)
        self.sld.valueChanged.connect(self.line_text_edit)

        self.sld.setSizePolicy(size_policy)
        # endregion

        # self.c = Communicate()
        # self.c.end_enter.connect(self.textChanged)

        # region правый верхний виджет(text_view)
        self.text_view = QTextEdit()
        self.text_view.setMinimumSize(300, 400)  # установка минимального размера
        self.text_view.setFont(QtGui.QFont("Times", 18))
        # endregion

        # region ##Кнопки
        # region Кнопка выделить область(btn_select_area)
        self.btn_select_area = QtWidgets.QPushButton('Выделить область')
        self.btn_select_area.setStyleSheet("background-color: rgb(255, 47, 253);")
        self.btn_select_area.setFont(QtGui.QFont("Times", 18, QtGui.QFont.Bold))
        self.btn_select_area.setSizePolicy(size_policy)
        self.btn_select_area.setMinimumHeight(40)
        self.btn_select_area.setMaximumHeight(self.__max_height_size_of_widget_left_down_layout)
        self.btn_select_area.setShortcut(QtCore.Qt.ALT + QtCore.Qt.Key_Q)
        self.btn_select_area.clicked.connect(self.activateSnipping)
        self.btn_select_area.setEnabled(False)
        # endregion

        # region кнопка загрузить изображение(open_btn)
        self.open_btn = QPushButton()
        self.open_btn.setText('Загрузить изображение')
        self.open_btn.setStyleSheet("background-color: rgb(237, 51, 59);")
        self.open_btn.setFont(QtGui.QFont("Times", 18, QtGui.QFont.Bold))
        self.open_btn.setSizePolicy(size_policy)  # установка политики размера
        self.open_btn.setMinimumHeight(40)
        self.open_btn.setMaximumHeight(
            self.__max_height_size_of_widget_left_down_layout)  # установка максимального размера кнопки
        self.open_btn.setShortcut(QtCore.Qt.ALT + QtCore.Qt.Key_I)
        self.open_btn.clicked.connect(self.show_image)
        # endregion

        # region Распознать(btn_recognize_text)
        self.btn_recognize_text = QPushButton()
        self.btn_recognize_text.setText('Распознать')
        self.btn_recognize_text.setStyleSheet("background-color: rgb(255, 228, 92);")
        self.btn_recognize_text.setFont(QtGui.QFont("Times", 18, QtGui.QFont.Bold))
        self.btn_recognize_text.setSizePolicy(size_policy)
        self.btn_recognize_text.setMinimumHeight(40)
        self.btn_recognize_text.setMaximumHeight(self.__max_height_size_of_widget_left_down_layout)
        self.btn_recognize_text.setShortcut(QtCore.Qt.ALT + QtCore.Qt.Key_A)
        self.btn_recognize_text.clicked.connect(self.recognize_text)
        self.btn_recognize_text.setEnabled(False)
        # endregion

        # region Выгрузить текст(btn_upload_text)
        self.btn_upload_text = QPushButton()
        self.btn_upload_text.setText('Выгрузить текст')
        self.btn_upload_text.setStyleSheet("background-color: rgb(145, 65, 172);")
        self.btn_upload_text.setFont(QtGui.QFont("Times", 18, QtGui.QFont.Bold))
        self.btn_upload_text.setSizePolicy(size_policy)  # установка политики размера
        self.btn_upload_text.setMinimumHeight(40)
        self.btn_upload_text.setMaximumHeight(
            self.__max_height_size_of_widget_right_down_layout)  # установка максимального размера кнопки
        self.btn_upload_text.setShortcut(QtCore.Qt.ALT + QtCore.Qt.Key_T)
        self.btn_upload_text.clicked.connect(self.upload_text)
        # endregion

        # region Очистить вывод(btn_clean_output)
        self.btn_clean_output = QPushButton()
        self.btn_clean_output.setText('Очистить вывод')
        self.btn_clean_output.setStyleSheet("background-color: rgb(87, 227, 137);")
        self.btn_clean_output.setFont(QtGui.QFont("Times", 18, QtGui.QFont.Bold))
        self.btn_clean_output.setSizePolicy(size_policy)  # установка политики размера
        self.btn_clean_output.setMinimumHeight(40)
        self.btn_clean_output.setMaximumHeight(
            self.__max_height_size_of_widget_right_down_layout)  # установка максимального размера кнопки
        self.btn_clean_output.setShortcut(QtCore.Qt.ALT + QtCore.Qt.Key_C)
        self.btn_clean_output.clicked.connect(self.clean_output)
        # endregion

        # region Сбросить поворот(btn_reset_angle)
        self.btn_reset_angle = QPushButton()
        self.btn_reset_angle.setText('Сбросить\nповорот')
        self.btn_reset_angle.setStyleSheet("background-color: rgb(128, 128, 137);")
        self.btn_reset_angle.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))  # Roboto
        # self.btn_select_area.adjustSize()
        self.btn_reset_angle.setSizePolicy(size_policy)
        self.btn_reset_angle.setMinimumHeight(40)
        self.btn_reset_angle.setMaximumHeight(self.__max_height_size_of_widget_right_down_layout)
        self.btn_reset_angle.setShortcut(QtCore.Qt.ALT + QtCore.Qt.Key_0)
        self.btn_reset_angle.clicked.connect(self.view.reset_angle)
        self.btn_reset_angle.setEnabled(True)
        # endregion

        # region кнопка поворота налево(buttonLeft)
        self.buttonLeft = QPushButton("Поворот\nналево на")
        self.buttonLeft.setStyleSheet("background-color: rgb(12, 40, 90);")
        self.buttonLeft.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.buttonLeft.setSizePolicy(size_policy)
        self.buttonLeft.setMinimumHeight(40)
        self.buttonLeft.setMaximumHeight(self.__max_height_size_of_widget_right_down_layout)
        self.buttonLeft.setShortcut(QtCore.Qt.ALT + QtCore.Qt.Key_Minus)
        self.buttonLeft.clicked.connect(self.view.slot_rotate_left)
        self.buttonLeft.setEnabled(False)
        # endregion

        # region кнопка поворота направо(buttonRight)
        self.buttonRight = QPushButton("Поворот\nнаправо на")
        self.buttonRight.setStyleSheet("background-color: rgb(12, 40, 90);border-radius: 0;border: 0px solid")
        self.buttonRight.setFont(QtGui.QFont("Times", 12, QtGui.QFont.Bold))
        self.buttonRight.setSizePolicy(size_policy)
        self.buttonRight.setMinimumHeight(40)
        self.buttonRight.setMaximumHeight(self.__max_height_size_of_widget_right_down_layout)
        self.buttonRight.setShortcut(QtCore.Qt.ALT + QtCore.Qt.Key_Equal)
        self.buttonRight.clicked.connect(self.view.slot_rotate_right)
        self.buttonRight.setEnabled(False)
        # endregion

        # region кнопка изменения градуса поворота изажения(plain_text)
        self.plain_text = QLineEdit()
        self.plain_text.setMaxLength(3)
        reg_ex = QRegExp("[0-9]{1,3}")
        input_validator = QRegExpValidator(reg_ex, self.plain_text)
        self.plain_text.setValidator(input_validator)
        self.plain_text.setText(str(self.view.angle))
        self.plain_text.setStyleSheet("background-color: rgb(12, 40, 190);border-radius: 0;border: 0px solid")
        self.plain_text.setFont(QtGui.QFont("Times", 20, QtGui.QFont.Bold))
        self.plain_text.setSizePolicy(size_policy)
        self.plain_text.setMinimumHeight(40)
        self.plain_text.setMinimumWidth(40)
        # self.plain_text.setMaximumHeight(40)
        self.plain_text.setMaximumWidth(self.__max_height_size_of_widget_right_down_layout)
        self.plain_text.textChanged.connect(self.text_changed)
        self.plain_text.setEnabled(False)
        # endregion

        # endregion

        # region ##layouts
        # region лэйаут повернуть изображение(layout_flip_the_image)
        self.layout_flip_the_image = QHBoxLayout()
        # self.layout_flip_the_image.setStyleSheet("background-color: rgb(248, 228, 255);")
        # endregion

        # region левый нижний лэйаут(layout_lower_left[vertical])
        self.layout_lower_left = QVBoxLayout()
        """
              layout_lower_left(vertical)
                |------------------|
                |open_btn          |
                |btn_recognize_text|
                |btn_select_area   |
                |------------------|
        """
        self.layout_lower_left.addWidget(self.open_btn, 5)
        self.layout_lower_left.addWidget(self.btn_recognize_text, 5)
        self.layout_lower_left.addWidget(self.btn_select_area, 5)
        # endregion

        # region правый нижний лэйаут(layout_lower_right[vertical])
        self.layout_lower_right = QVBoxLayout()
        """
                  layout_lower_right(vertical)
                    |---------------------|
                    |btn_clean_output     |
                    |btn_upload_text      |
                    |layout_flip_the_image|
                    |---------------------|
        """
        self.layout_lower_right.addWidget(self.btn_clean_output, 50)
        self.layout_lower_right.addWidget(self.btn_upload_text, 50)
        self.layout_lower_right.addWidget(self.sld)
        self.layout_lower_right.addLayout(self.layout_flip_the_image)
        # endregion

        ####self.view.angle = int(self.plain_text.text())

        # region добавление на лэйаут(layout_flip_the_image[horizontal]) кнопок для манипуляции с изображением
        """
                    layout_flip_the_image(horizontal)
            |-------------------------------------------------|
            |buttonLeft|plain_text|buttonRight|btn_reset_angle|
            |-------------------------------------------------|
        """
        self.layout_flip_the_image.addWidget(self.buttonLeft)
        self.layout_flip_the_image.addWidget(self.plain_text)
        # self.layout_flip_the_image.addWidget(self.lcd)
        self.layout_flip_the_image.addWidget(self.buttonRight)
        self.layout_flip_the_image.addWidget(self.btn_reset_angle)
        # endregion

        # region левый верхний лэйаут(layout_up_left)
        self.layout_up_left = QHBoxLayout()
        self.layout_up_left.addWidget(self.view)
        # endregion
        # endregion

        # region главный виджет(gridlayout)
        self.grid = QGridLayout(self.centralWidget)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setSpacing(0)
        # endregion

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

        # region snipper
        self.snipper = SnippingWidget()
        # endregion

    # region Функции
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

        # self.centralWidget.setFocusPolicy(QtCore.Qt.NoFocus)

        filename, t = QFileDialog.getOpenFileName(self,
                                                  "Open Image", ".",
                                                  "Image Files (*.png *.jpg *.tif);;JPG file (*.jpg);; PNG file ("
                                                  "*.png);; Tif file (*.tif);; Tiff file (*.tiff)")
        print(type(t), t)
        # QFileDialog.show() передать фокус
        if filename:
            self.pixmap = QPixmap(filename)
            if not self.pixmap is None:
                # region включаем "килкабельность" у кнопок
                self.btn_select_area.setEnabled(True)
                self.sld.setEnabled(True)
                self.btn_recognize_text.setEnabled(True)
                self.plain_text.setEnabled(True)
                # endregion

                self.scene.clear()  # очистка сцены
                self.scene.setSceneRect(0, 0, self.pixmap.width(), self.pixmap.height())  # сброс скрола

                self.scene.addPixmap(self.pixmap)

                self.buttonLeft.setStyleSheet("background-color: rgb(12, 40, 90);"
                                              "color:white")
                self.buttonRight.setStyleSheet("background-color: rgb(12, 40, 90);"
                                               "color:white")

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

    def line_text_edit(self):
        """
        устанавливает значение в поле(plain_text) из значения слайдера
        :return:
        """
        self.plain_text.setText(str(self.sld.value()))

    def keyPressEvent(self, e):
        """
        Выход по нажатию shift+Q
        :param e:
        :return:
        """
        if int(e.modifiers()) == QtCore.Qt.ControlModifier:
            if e.key() == QtCore.Qt.Key_Q:
                self.close()
                # sys.exit(app.exec_())

    def text_changed(self):
        """
        Функция задаёт угол поворота(для view) и устаналивает на слайдере значение
        :return:
        """
        if self.plain_text.text() != '':
            self.view.angle = int(self.plain_text.text())
            self.sld.setSliderPosition(int(self.plain_text.text()))
            # self.c.end_enter.emit()

    # endregion


def create_folder():
    """
    создание папки для сохранения изображений
    :return:
    """
    home_dir = Path.home() / 'test_dir'
    if home_dir.is_dir():
        print('Папка существует')
    else:
        print(home_dir)
        home_dir.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    create_folder()

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.setWindowTitle("OCR")
    # w.setWindowIcon() # Задел на будущее
    w.resize(600, 400)
    w.show()
    sys.exit(app.exec_())
