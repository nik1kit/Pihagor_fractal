import tkinter as tk
from tkinter import messagebox
from threading import Thread
from PIL import Image, ImageTk
import os

from fractal import TreeFractal  # предполагается, что твой класс TreeFractal сохранён в fractal.py

class FractalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор дерева Пифагора")
        self.root.geometry("400x400")

        # Поля ввода
        self.left_label = tk.Label(root, text="Левый нижний угол (x;y):")
        self.left_label.pack()
        self.left_entry = tk.Entry(root)
        self.left_entry.pack()

        self.right_label = tk.Label(root, text="Правый нижний угол (x;y):")
        self.right_label.pack()
        self.right_entry = tk.Entry(root)
        self.right_entry.pack()

        self.angle_label = tk.Label(root, text="Угол (в градусах):")
        self.angle_label.pack()
        self.angle_entry = tk.Entry(root)
        self.angle_entry.pack()

        self.depth_label = tk.Label(root, text="Глубина:")
        self.depth_label.pack()
        self.depth_entry = tk.Entry(root)
        self.depth_entry.pack()

        # Флажок координатной сетки
        self.grid_var = tk.BooleanVar()
        self.grid_check = tk.Checkbutton(root, text="Показать координатную сетку", variable=self.grid_var)
        self.grid_check.pack()

        # Кнопка запуска
        self.start_button = tk.Button(root, text="Сгенерировать", command=self.run_generation)
        self.start_button.pack(pady=10)

        self.status = tk.Label(root, text="")
        self.status.pack()

        self.optimal_depth_label = tk.Label(root, text="Оптимальная глубина: –")
        self.optimal_depth_label.pack()

    def run_generation(self):
        try:
            # Парсим ввод
            left_x, left_y = map(float, self.left_entry.get().replace(',', '.').split(';'))
            right_x, right_y = map(float, self.right_entry.get().replace(',', '.').split(';'))
            angle = float(self.angle_entry.get().replace(',', '.'))
            depth = int(self.depth_entry.get())

            if abs(right_x - left_x) != 1 or left_y != right_y:
                messagebox.showerror("Ошибка",
                                     "Указанные точки должны быть вершинами единичного горизонтального квадрата (разница x = 1, y одинаковые).")
                return

            # Запуск в отдельном потоке
            thread = Thread(target=self.generate_tree, args=((left_x, left_y), (right_x, right_y), angle, depth, self.grid_var.get()))
            thread.start()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Неверный ввод: {e}")

    def generate_tree(self, left_bottom, right_bottom, angle, depth, show_grid):
        self.status.config(text="Генерация дерева...")

        if not (0 < angle < 90):
            messagebox.showerror("Ошибка",
                                 "Угол должен быть в диапазоне от 0 до 90 градусов (не включая границы)")
            return


        tree = TreeFractal(width=1920, height=1080, base_length=100,
                           left_bottom=left_bottom, right_bottom=right_bottom)

        optimal = tree.calculate_effective_depth(base_length=100, angle_deg=angle, min_pixel_size=1)
        self.optimal_depth_label.config(text=f"Оптимальная глубина: {optimal}")

        tree.generate(depth=depth, angle=angle, show_grid=show_grid)
        tree.save("tree.png")

        self.status.config(text="Готово! Файл сохранен как tree.png")
        os.startfile("tree.png")  # откроет изображение (только Windows)


if __name__ == "__main__":
    root = tk.Tk()
    app = FractalApp(root)
    root.mainloop()

