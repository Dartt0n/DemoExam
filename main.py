from PyQt5 import QtWidgets, QtCore, QtGui
import sys
import math

MAX_FIGURES_COUNT = 5


class Interface:
    """
    Класс, содержащий разметку интерфейса
    """
    # отступ от рамки
    padding = 10
    # размеры кнопок
    buttons_width = 150
    buttons_height = 50
    # размеры кнопок палитры
    figures_width = 200
    figures_height = 200
    # рамзеры окна
    window_width = 1000
    window_height = 700
    # размеры поля для рисования
    canvas_height = 620
    canvas_width = 770
    # размеры надписи
    label_width = 500
    label_height = 50

    # расположение кнопок на экране
    buttons = {
        'triangle': QtCore.QRect(
            padding,
            padding,
            figures_width,
            figures_height
        ),
        'square': QtCore.QRect(
            padding,
            padding * 2 + figures_height,
            figures_width,
            figures_height
        ),
        '5_angle_polygon': QtCore.QRect(
            padding,
            padding * 3 + figures_height * 2,
            figures_width,
            figures_height
        ),
        'exit': QtCore.QRect(
            window_width - padding - buttons_width,
            window_height - padding - buttons_height,
            buttons_width,
            buttons_height
        ),
        'delete': QtCore.QRect(
            window_width - (padding + buttons_width) * 2,
            window_height - padding - buttons_height,
            buttons_width,
            buttons_height
        )
    }
    # расположение поля для рисования на экране
    canvas = QtCore.QRect(
        padding * 2 + figures_width,
        padding,
        canvas_width,
        canvas_height
    )

    info_label = QtCore.QRect(
        padding,
        window_height - padding - buttons_height,
        label_width,
        label_height,
    )


class Canvas(QtWidgets.QWidget):
    """
    Класс "доски для рисования", на нем отрисовываются фигуры
    """

    def __init__(self, *args, **kwargs):
        """
        Инициализация обьекта
        :param args: Параметры для родительского класса QWidget
        :param kwargs: Параметры для родительского класса QWidget
        """
        self.selected_figure_draw = None
        self.selected_figure_edit = None
        self.figures = []
        # стартовая позиция drag-and-drop`a для изменения размеров фигуры
        self.left_dad_pos = None
        self.right_dad_pos = None
        super(Canvas, self).__init__(*args, **kwargs)

    def mouseReleaseEvent(self, event):
        """
        Обработчик события поднятия мыши
        :param event: Событие поднятия
        :return: None
        """
        self.left_dad_pos = None
        self.right_dad_pos = None

    def mouseMoveEvent(self, event):
        """
        Обработчик события движения мыши
        :param event: Событие движения
        :return: None
        """
        # если тянут левую кнопку мыши
        if self.left_dad_pos is not None and self.selected_figure_edit is not None:
            figure = self.figures[self.selected_figure_edit]
            self.figures.remove(figure)
            # вычисляем направления как произведение двух параметром и сравнение с 0
            # - * - = +
            # - * + = -
            # + * - = -
            # + * + = +
            navigation = -1 if (self.left_dad_pos[0] - event.pos().x()) * (
                    self.left_dad_pos[1] - event.pos().y()) < 0 else 1
            figure = ShapePolygon(
                figure.angles,
                figure.radius + navigation * math.hypot(
                    self.left_dad_pos[0] - event.pos().x(),
                    self.left_dad_pos[1] - event.pos().y()
                ) / 6,  # 6 для уменьшения чувствительности,
                figure.center_x,
                figure.center_y,
                figure.rotation
            )
            self.left_dad_pos = event.pos().x(), event.pos().y()
            self.figures.append(figure)

        # если тянут правую кнопку мыши
        if self.right_dad_pos is not None and self.selected_figure_edit is not None:
            figure = self.figures[self.selected_figure_edit]
            self.figures.remove(figure)
            figure = ShapePolygon(  # создаем новую фигуру с другим углом отклонения
                figure.angles,
                figure.radius,
                figure.center_x,
                figure.center_y,
                figure.rotation + math.hypot(
                    self.right_dad_pos[0] - event.pos().x(),
                    self.right_dad_pos[1] - event.pos().y()
                ) / 15  # 8 для уменьшения чувствительности
            )
            self.right_dad_pos = event.pos().x(), event.pos().y()
            self.figures.append(figure)
        self.update()

    def mousePressEvent(self, event):
        """
        Обработчик события нажатия мышью на обьекта
        :param event: Событие нажания
        :return: None
        """
        click_x, click_y = event.pos().x(), event.pos().y()  # получаем координаты клика мышью

        if event.button() == QtCore.Qt.RightButton:
            self.select(None)  # если нажата правая кнопка мыши - снимаем выделение
            self.right_dad_pos = click_x, click_y  # мышь нажали - сохраняем начальную позицию d&d
            self.parent().info_label.setText('Выберите фигуру из палитры')
            return

        self.left_dad_pos = click_x, click_y  # мышь нажали - сохраняем начальную позицию d&d
        if self.selected_figure_draw is None:  # если фигура не выбрана
            if not self.figures:  # и нету фигур
                return  # выходим, нам не из чего искать выделяемую фигуру
            # создаем массив центров фигру
            shapes_centers = [(shape.center_x, shape.center_y) for shape in self.figures]
            shapes_distances = []
            # и массив расстояний от точки клика мыши до центра фигуры
            for shape in shapes_centers:
                shapes_distances.append(
                    math.hypot(
                        click_x - shape[0],
                        click_y - shape[1]
                    )
                )

            # находим миниманое расстояние и сохраняем индекс фигуры
            min_distance = shapes_distances[0]
            shape_index = 0
            for index, value in enumerate(shapes_distances):
                if value < min_distance:
                    min_distance = value
                    shape_index = index

            # выделяем найденую фигуру
            self.selected_figure_edit = shape_index
            self.parent().info_label.setText(
                'Тяните ПКМ чтобы вращать.\n'
                'Тените ЛКМ влево-вниз или вправо-верх чтобы уменьшить размер,\n'
                'и влево-верх или вправо-вниз чтобы увеличить\n'
                'Delete - удалить'
            )
        else:
            # фигура была выбрана -> надо отрисровать ее
            if len(self.figures) == MAX_FIGURES_COUNT:  # если фигур максимальное количество
                self.parent().info_label.setText('Может сущеcтвовать не более 5 фигур')
                return
            self.figures.append(ShapePolygon(  # добавляем фигуру к отрисовываемым
                self.selected_figure_draw.angles,
                self.selected_figure_draw.radius,
                click_x, click_y,
                self.selected_figure_draw.rotation,
            ))
            self.select(None)  # убираем выделение
        self.update()  # отрисроваем все фигуры

    def select(self, figure):
        """
        Сохраняет выбор фигуры
        :param figure: фигура или None
        :return: None
        """
        self.selected_figure_draw = figure

    def delete_selected_figure(self):
        """
        Удаляет выбраную фигуру
        :return: None
        """
        if self.selected_figure_edit is not None:
            # Если фигуры выбрана, удаляем
            self.figures.pop(self.selected_figure_edit)
        # снимаем выделение
        self.selected_figure_edit = None
        # отрисроваем все фигуры заново
        self.update()

    def paintEvent(self, event):
        """
        Обработчик события отрисовки обьекта на экране
        :param event: cобытие отрисовки
        :return: None
        """
        super(Canvas, self).paintEvent(event)  # вызываем родительский метод отрисовки
        painter = QtGui.QPainter()  # создает обьект отрисовщика
        painter.begin(self)
        # контур фигур черным, шириной 5 пикселей
        pen = QtGui.QPen(QtGui.QColor(0, 0, 0))
        pen.setWidth(5)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width(), self.height())  # рамка
        # заливка - красная
        brush = QtGui.QBrush(QtGui.QColor(255, 0, 0))
        painter.setBrush(brush)
        for index, polygon in enumerate(self.figures):
            # отрисовываем фигуру
            painter.drawPolygon(polygon)
            if index == self.selected_figure_edit:  # если эта фигура выбрана
                for point in polygon:  # для каждой вершины
                    # получаем координы вершины
                    x, y = point.x(), point.y()
                    # синий контур и заливка
                    painter.setPen(QtGui.QColor(0, 0, 255))
                    painter.setBrush(QtGui.QColor(0, 0, 255))
                    # рисуем прямоугольник размерами 10 на 10 пикселей, так чтобы точка было в центре
                    painter.drawRect(round(x - 5), round(y - 5), 10, 10)
                # возвращаем первоначальные значения заливки и контура
                painter.setBrush(brush)
                painter.setPen(pen)
        painter.end()


class ShapePolygon(QtGui.QPolygonF):
    """
    Класс правильного многоугольника
    """

    def __init__(self, angles, radius, center_x, center_y, rotation):
        """
        Создание правильного многоугольника
        :param angles: Количество вершин
        :param radius: Радиус описанной окружности
        :param center_x: X координата центра
        :param center_y: Y координата центра
        :param rotation: угол отклонения
        """
        super(ShapePolygon, self).__init__()
        self.center_x = center_x
        self.center_y = center_y
        self.angles = angles
        self.rotation = rotation
        self.radius = radius
        step = 2 * math.pi / angles
        for i in range(angles):
            angle = step * i + rotation
            x = radius * math.cos(angle) + center_x
            y = radius * math.sin(angle) + center_y
            self.append(QtCore.QPoint(round(x), round(y)))


class PaletteButton(QtWidgets.QPushButton):
    """
    Класс кнопок палитры, позволяет отрисовать правильный многоугольник на поверхности кнопки
    """

    def __init__(self, angles, rotation=0, *args, **kwargs):
        """
        Создание обьекта
        :param angles: Количество вершин правильного многоугольника
        :param rotation: Угол отклонения правильного многоугольника
        :param args: Параметры для родительского класса QPushButton
        :param kwargs: Параметры для родительского класса QPushButton
        """
        self.angles = angles
        self.polygon_rotation = math.radians(rotation)
        super(PaletteButton, self).__init__(*args, **kwargs)

    def paintEvent(self, event):
        """
        Обработчик события отрисовки обьекта на экране
        :param event: cобытие отрисовки
        :return: None
        """
        super(PaletteButton, self).paintEvent(event)
        painter = QtGui.QPainter()
        painter.begin(self)
        # красная заливка
        painter.setBrush(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
        # рисуем фигуру
        painter.drawPolygon(
            ShapePolygon(
                self.angles,
                self.width() // 2 - Interface.padding,  # радиус = половина ширины - отступ от края
                self.width() // 2,
                self.height() // 2,
                self.polygon_rotation
            )
        )
        painter.end()


class MainWindow(QtWidgets.QWidget):
    """
    Основнок окно приложения
    """

    def __init__(self, *args, **kwargs):
        """
        Создает обьект
        :param args: Параметры для родительского класса QWidget
        :param kwargs: Параметры для родительского класса QWidget
        """
        self.selected_figure = None
        self.default_shape_radius = 100  # радиус фигуры по умолчанию
        super(MainWindow, self).__init__(*args, **kwargs)
        self.init_ui()  # инициализируем интерфейс
        self.bind_buttons()  # "вешаем" обработчики на кнопки

    def init_ui(self):
        """
        Инициализирует интерфейс
        :return: None
        """
        self.setStyleSheet(
            "background-color: #eeeeee;"  # свело серый фон
            "font-size: 18px;"  # размер шрифта
        )
        # размеры виджета
        self.setGeometry(0, 0, Interface.window_width, Interface.window_height)

        # добавляем кнопки, задаем им размер и позицию, а так же свойства отображения
        self.palette_triangle = PaletteButton(3, rotation=-90, parent=self)
        self.palette_triangle.setGeometry(Interface.buttons['triangle'])
        self.palette_triangle.setStyleSheet("background-color: #ffffff")

        self.palette_square = PaletteButton(4, rotation=-45, parent=self)
        self.palette_square.setGeometry(Interface.buttons['square'])
        self.palette_square.setStyleSheet("background-color: #ffffff")

        self.palette_fiveangle = PaletteButton(5, rotation=-22, parent=self)
        self.palette_fiveangle.setGeometry(Interface.buttons['5_angle_polygon'])
        self.palette_fiveangle.setStyleSheet("background-color: #ffffff")

        self.delete_button = QtWidgets.QPushButton(parent=self, text='Delete')
        self.delete_button.setGeometry(Interface.buttons['delete'])
        self.delete_button.setStyleSheet("background-color: #ffffff")

        self.exit_button = QtWidgets.QPushButton(parent=self, text='Exit')
        self.exit_button.setGeometry(Interface.buttons['exit'])
        self.exit_button.setStyleSheet("background-color: #ff4d00")  # выделяеющийся цвет фона

        self.canvas = Canvas(parent=self)
        self.canvas.setGeometry(Interface.canvas)
        self.canvas.setStyleSheet("background-color: #ffffff")

        self.info_label = QtWidgets.QLabel(parent=self)
        self.info_label.setGeometry(Interface.info_label)
        self.info_label.setStyleSheet("font-size: 12px")
        self.info_label.setText('Выберите фигуру из палитры')

    def select(self, angles):
        """
        Выбор фигуры
        :param angles: Количество уголов правильного многоугольника (выбранной фигуры)
        :return: None
        """
        self.selected_figure = angles
        # выбираем фигуры для обьекта отрисовки
        self.canvas.select(ShapePolygon(self.selected_figure, self.default_shape_radius, 0, 0, 0))
        self.info_label.setText('ПКМ - отмена, ЛКМ по полю - рисование')

    def bind_buttons(self):
        """
        "Вешает" обработчики на кнопки
        :return: None
        """
        # выход
        self.exit_button.clicked.connect(lambda event: sys.exit(0))
        # удаления элемента
        self.delete_button.clicked.connect(lambda event: self.canvas.delete_selected_figure())
        # выбор фигуры
        self.palette_triangle.clicked.connect(lambda event: self.select(3))
        self.palette_square.clicked.connect(lambda event: self.select(4))
        self.palette_fiveangle.clicked.connect(lambda event: self.select(5))

    def keyPressEvent(self, event):
        """
        Обработчик события нажатия клавишы на клавиатуре
        :param event: Событие нажатия
        :return: None
        """
        if event.key() == QtCore.Qt.Key_Delete:  # если нажата кнопка Delete
            self.canvas.delete_selected_figure()  # удаляем выбранную фигуры


if __name__ == '__main__':
    # создает приложение
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    # запускаем его, результат выполнения приложения = результат выполнения программы
    sys.exit(app.exec_())
