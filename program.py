import tkinter as tk
from typing import Tuple

import numpy as np
from PIL import Image, ImageTk

from consts import ROT_ANGLE
from object import Object
from observer import Observer
from pivot import Pivot


class Program(Observer):

    def __init__(self, master, dimensions: Tuple[int, int]):
        self.master = master
        self.master.title("2D Transformations")

        self.h, self.w = 300, 300

        self.canvas_arr = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        self.obj = Object(np.array([
            [20, 20, 1],
            [80, 20, 1],
            [80, 80, 1],
            [20, 80, 1],
            [20, 20, 1],
        ]))

        self.img = ImageTk.PhotoImage(Image.fromarray(self.canvas_arr))

        self.canvas = tk.Canvas(master, width=self.w, height=self.h)
        self.update()
        # self.canvas.create_image(0, 0, anchor='nw', image=self.img)

        # mx, my = self.w // 2, self.h // 2
        # self.rec_points = [
        #     mx, my,
        #     mx + 20, my + 20
        # ]
        # self.rec = self.canvas.create_rectangle(self.rec_points[0], self.rec_points[1], self.rec_points[2],
        #                                         self.rec_points[3], fill="blue")

        self.canvas.grid(row=0, column=0)

        frame = tk.Frame(master).grid(row=0, column=0)

        self.btn_inc = tk.Button(frame, text="Move down", command=self.increase) \
            .grid(row=0, column=1, padx=2, pady=2)
        self.btn_dec = tk.Button(frame, text="Move up", command=self.decrease) \
            .grid(row=0, column=2, padx=2, pady=2)
        self.btn_rot = tk.Button(frame, text="Rotate", command=self.rotate) \
            .grid(row=1, column=2)

        self.rot_label = tk.Label(frame, text="Rotation angle: ").grid(row=1, column=0)
        self.rot_entry = tk.Entry(frame)
        self.rot_entry.insert(0, ROT_ANGLE)
        self.rot_entry.grid(row=1, column=1)

        midx, midy = self.obj.center_point
        print(midx, midy)
        pivot = Pivot(self.canvas, midx, midy, self.obj.move, width=8)
        self.register_observer(pivot)

    def rotate(self):

        # print(self.obj.points)
        angle = int(self.rot_entry.get())
        if 0 <= angle <= 360:
            self.obj.rotate(angle, point=self.obj.center_point)
        self.update()

    def increase(self):
        self.obj.move(10, 10)
        self.update()

    def decrease(self):
        self.obj.move(-10, -10)
        self.update()

    def notify(self):
        self.update()

    def update(self):
        self.canvas_arr = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        self.obj.draw(self.canvas_arr)
        # print(self.obj.points)

        self.img = ImageTk.PhotoImage(Image.fromarray(self.canvas_arr.astype(np.uint8)))

        self.canvas.create_image(0, 0, anchor='nw', image=self.img)

