import tkinter as tk
from collections import deque
from typing import Tuple

import numpy as np
from PIL import Image, ImageTk

from consts import ROT_ANGLE
from object import Object
from observer import Observer
from pivot import Pivot, MP, SP


class Program(Observer):

    def __init__(self, master, dimensions: Tuple[int, int], debug=False):
        self.master = master
        self.master.title("2D Transformations")
        self.debug = debug
        if self.debug:
            self.text = []

        self.image = None
        self.history = deque()

        self.h, self.w = 600, 600

        self.canvas = tk.Canvas(master, width=self.w, height=self.h)

        self.canvas_arr = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        self.obj = Object(self.canvas, np.array([
            [20, 20, 1],
            [80, 20, 1],
            [80, 80, 1],
            [20, 80, 1],
            [20, 20, 1],
        ]))

        self.img = ImageTk.PhotoImage(Image.fromarray(self.canvas_arr))

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

        # self.rot_label = tk.Label(frame, text="Rotation angle: ").grid(row=1, column=0)
        # self.rot_entry = tk.Entry(frame)
        # self.rot_entry.insert(0, ROT_ANGLE)
        # self.rot_entry.grid(row=1, column=1)


        # pivot = Pivot(self.canvas, 45, 45, self.obj.move, width=8)
        for p in self.obj.pivots:
            self.register_observer(p)


        # tk.Button(frame, text="Scale mode", command=lambda: self.obj.choose_pivot(self.canvas, SP)) \
        #     .grid(row=0, column=1)
        # tk.Button(frame, text="Position mode", command=lambda: self.obj.choose_pivot(self.canvas, MP)) \
        #     .grid(row=0, column=2)

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
        # It is needed to clear canvas items, so that no memory leak would appear
        # self.canvas.delete("all")
        self.canvas.delete(self.image)

        self.canvas_arr = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        self.obj.draw(self.canvas_arr)
        # print(self.obj.points)

        self.img = ImageTk.PhotoImage(Image.fromarray(self.canvas_arr.astype(np.uint8)))

        self.image = self.canvas.create_image(0, 0, anchor='nw', image=self.img)

        for p in self.obj.pivots:
            p.draw()

        if self.debug:
            for t in self.text:
                self.canvas.delete(t)

            for p in self.obj.points:
                self.text.append(
                    self.canvas.create_text(p[1] + 10, p[0] + 10,
                                            text="({}, {})".format(p[1], p[0]), font="Times 11", fill="red"))

        print(self.canvas.find_all(), "length: ", len(self.canvas.find_all()))
