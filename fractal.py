from PIL import Image, ImageDraw
import numpy as np
import math
from tqdm import tqdm


class TreeFractal:
    def __init__(self, width=1920, height=1080, base_length=100, background_color=(255, 255, 255, 0),
                 offset_x=0, offset_y=0, left_bottom=(0, 0), right_bottom=(0, 0)):
        """
        Инициализирует процесс генерации дерева.
        :param width: Ширина холста для рисования
        :param height: Высота холста для рисования
        :param base_length: Длина (в пикселях) начального квадрата
        :param background_color: Цвет фона холста
        :param offset_x: Смещение фрактала дерева по оси X
        :param offset_y: Смещение фрактала дерева по оси Y
        :param left_bottom: Координаты левого нижнего угла начального квадрата
        :param right_bottom: Координаты правого нижнего угла начального квадрата
        """
        # Преобразуем координаты в соответствии с шириной квадрата
        center_x = width / 2
        center_y = height / 2

        self.start_coords = (
            (center_x + left_bottom[0] * base_length + offset_x, center_y - left_bottom[1] * base_length - offset_y),
            (center_x + right_bottom[0] * base_length + offset_x, center_y - right_bottom[1] * base_length - offset_y)
        )

        self.canvas = (width, height)
        self.background_color = background_color

        self.image = Image.new('RGBA', self.canvas, self.background_color)
        self.draw = ImageDraw.Draw(self.image)
        self.base_length = base_length

    @staticmethod
    def __convert_list_to_tuple(*args):
        """
        Преобразует несколько кортежей или массивоподобных объектов в список кортежей
        :param args: Несколько кортежей или объектов, похожих на массив
        :return: Возвращает список кортежей
        """

        return [tuple(x) for x in args]

    def __draw_grid(self):
        """
        Рисует координатную сетку на изображении, масштабированную по base_length.
        Центр изображения соответствует координате (0, 0).
        """
        draw = self.draw
        width, height = self.canvas
        center_x = width // 2
        center_y = height // 2

        # Цвет и стиль сетки
        grid_color = (200, 200, 200, 255)

        # Вертикальные линии
        x = center_x
        while x < width:
            draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
            x += self.base_length
        x = center_x - self.base_length
        while x > 0:
            draw.line([(x, 0), (x, height)], fill=grid_color, width=1)
            x -= self.base_length

        # Горизонтальные линии
        y = center_y
        while y < height:
            draw.line([(0, y), (width, y)], fill=grid_color, width=1)
            y += self.base_length
        y = center_y - self.base_length
        while y > 0:
            draw.line([(0, y), (width, y)], fill=grid_color, width=1)
            y -= self.base_length

        # Оси координат
        axis_color = (150, 150, 150, 255)
        draw.line([(center_x, 0), (center_x, height)], fill=axis_color, width=2)  # Ось Y
        draw.line([(0, center_y), (width, center_y)], fill=axis_color, width=2)  # Ось X

    def __draw_cube(self, p1, p2, fill=None, outline=(0, 0, 0)):
        """
        Вычисляет неизвестные точки квадрата, затем рисует квадрат и возвращает эти точки
        :param p1: Первая известная точка квадрата, заданная в виде кортежа
        :param p2: Вторая известная точка квадрата, заданная в виде кортежа
        :param fill: Цвет заливки фигуры
        :param outline: Цвет обводки фигуры
        :return: Возвращает 2 вновь вычисленные точки, которые ранее не были известны
        """

        p1_to_p2 = np.subtract(p1, p2)
        # print(p1_to_p2, p1, p2)
        p1_to_p4 = (-p1_to_p2[1], p1_to_p2[0])

        p3 = np.add(p2, p1_to_p4)
        p4 = np.add(p1, p1_to_p4)

        self.draw.polygon(self.__convert_list_to_tuple(p1, p2, p3, p4), fill=fill, outline=outline)

        return p3, p4

    def __draw_triangle(self, p1, p2, fill=None, outline=(0, 0, 0), angle=45, mirror=False):
        """
        Вычисляет неизвестную вершину треугольника, затем рисует квадрат и возвращает точки
        :param p1: Первая известная вершина треугольника, заданная в виде кортежа
        :param p2: Вторая известная вершина треугольника, заданная в виде кортежа
        :param fill: Цвет заливки
        :param outline: Цвет контура
        :param angle: Угол α, который должен иметь треугольник
        :param mirror: Нужно ли отразить треугольник (поменять углы местами)
        :return: Возвращает 2 пары точек (2x2), которые являются ребрами, на основе которых строятся квадраты
        """

        angle = max(1, min(angle, 89))

        # Переводим угол в радианы
        angle1 = math.pi * ((90 - angle) / 180)
        angle2 = math.pi * (angle / 180)
        if mirror:
            angle1, angle2 = angle2, angle1
        angle3 = math.pi - angle1 - angle2

        # Вычисляем расстояние между p1 и p2
        p1_to_p2 = np.subtract(p2, p1)
        length_p1_to_p2 = np.linalg.norm(p1_to_p2)

        # # Если длина слишком маленькая, пропускаем вычисления
        # if length_p1_to_p2 < 1e-6:
        #     raise ValueError("Длина между p1 и p2 слишком мала!")

        # Вычисление длины от p1 до p3 (вершина треугольника)
        length_p1_to_p3 = length_p1_to_p2 * math.sin(angle2) / math.sin(angle3)

        x, y = p1_to_p2

        equation_1 = p1[0] * x + p1[1] * y + length_p1_to_p3 * length_p1_to_p2 * math.cos(angle1)
        equation_2 = p2[1] * x - p2[0] * y + length_p1_to_p3 * length_p1_to_p2 * math.sin(angle1)

        # Устанавливаем пороговое значение для координат
        threshold = 1e-6
        x3 = ((1 / length_p1_to_p2) ** 2) * (x * equation_1 - y * equation_2)
        y3 = ((1 / length_p1_to_p2) ** 2) * (y * equation_1 + x * equation_2)

        # Проверка на маленькие значения координат
        if abs(x3) < threshold:
            x3 = 0
        if abs(y3) < threshold:
            y3 = 0

        p3 = (x3, y3)

        self.draw.polygon(self.__convert_list_to_tuple(p1, p2, p3), fill=fill, outline=outline)

        return (p3, p1), (p2, p3)

    @staticmethod
    def __default_style_gen(depth, shape=None):
        """
        Стандартная функция для раскраски дерева
        :param depth: Текущая глубина, на основе которой определяется стиль
        :param shape: Либо "cube" (куб), либо "triangle" (треугольник), в зависимости от текущей фигуры
        :return: Возвращает стиль, который должна иметь текущая фигура
        """

        if depth <= 2:
            fill = (100, 54, 15)
        elif depth <= 5:
            fill = (162, 96, 41)
        else:
            fill = (38, 196, 64)
        return {"fill": fill, "outline": (0, 0, 0)}

    def calculate_effective_depth(self, base_length, angle_deg, min_pixel_size):
        """
        Рассчитывает эффективную глубину, при которой размер элементов дерева остаётся видимым на экране.
        :param base_length: Начальная длина первого объекта (начальный размер в пикселях).
        :param angle_deg: Угол в градусах, который определяет коэффициент уменьшения размера.
        :param min_pixel_size: Минимальный размер объекта (в пикселях), который всё ещё считается видимым.
        :return: Эффективная глубина, при которой элементы дерева всё ещё видимы.
        """
        # Преобразуем угол из градусов в радианы
        angle_rad = math.radians(angle_deg)

        # Рассчитываем коэффициент уменьшения для каждого шага дерева
        scale_factor = math.cos(angle_rad)  # Коэффициент уменьшения размера на каждом шаге

        # Начальный размер элемента дерева
        current_size = base_length

        # Начинаем с 1-го шага и продолжаем, пока размер не станет меньше минимального видимого размера
        depth = 0
        while current_size >= min_pixel_size:
            current_size *= scale_factor  # Уменьшаем размер элемента дерева
            depth += 1  # Увеличиваем глубину

        return depth

    def generate(self, style_gen=None, depth=12, background_color=None, angle=90, mirror=True, show_grid=False):
        """
        Рисует дерево на холсте
        :param style_gen: Использует этот стиль раскраски, если он задан, иначе используется стиль по умолчанию
        :param depth: Глубина, на которую должно быть сгенерировано дерево
        :param background_color: Использует этот цвет фона, если задан, иначе используется изначальное значение
        :param angle: Угол α, который должны иметь треугольники
        :param mirror: Если установлено в True, дерево будет отражено по горизонтали
        :param show_grid: Если True — отобразить координатную сетку
        :return: Ничего не возвращает
        """

        # Если глубина равна 0, рисуем только квадрат и завершаем
        if depth == 0:
            self.__draw_cube(*self.start_coords, **self.__default_style_gen(0, shape="cube"))
            return

        background_color = background_color if background_color is not None else self.background_color
        self.draw.rectangle([(0, 0), self.canvas], fill=background_color)

        if show_grid:
            self.__draw_grid()

        style_gen = style_gen if style_gen is not None else self.__default_style_gen

        coord_sets = [self.start_coords]
        next_coord_sets = []

        for current_depth in tqdm(range(depth), desc="Generating Tree", unit="depth"):
            for coord_set in coord_sets:
                cube_coord_set = self.__draw_cube(
                    *coord_set,
                    **style_gen(current_depth, shape="cube")
                )

                triangle_coord_sets = self.__draw_triangle(
                    *cube_coord_set,
                    **style_gen(current_depth, shape="triangle"),
                    angle=angle,
                    mirror=mirror
                )

                [next_coord_sets.append(triangle_coord_set) for triangle_coord_set in triangle_coord_sets]

            coord_sets = next_coord_sets
            next_coord_sets = []

    def save(self, filename):
        """
        Сохраняет изображение с холста в файл
        :param filename: Имя файла, в который должно быть сохранено изображение
        :return: Ничего не возвращает
        """

        self.image.save(filename)