import tkinter as tk
from typing import Tuple

import numpy as np
from PIL import Image, ImageTk
from object import Object



class Program:

    def __init__(self, master, dimensions: Tuple[int, int]):
        self.master = master
        self.master.title("2D Transformations")

        frame = tk.Frame(master).grid(row=0, column=0)

        self.btn_inc = tk.Button(frame, text="Increase slope", command=self.increase) \
            .grid(row=0, column=1, padx=2, pady=2)
        self.btn_dec = tk.Button(frame, text="Decrease slope", command=self.decrease) \
            .grid(row=0, column=2, padx=2, pady=2)
        self.btn_rot = tk.Button(frame, text="Rotate", command=self.rotate) \
            .grid(row=1, column=2, padx=2, pady=2)

        self.h, self.w = 300, 300

        self.canvas_arr = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        self.obj = Object(np.array([
            [20, 20, 1],
            [80, 20, 1],
            [80, 80, 1],
            [20, 80, 1],
            [20, 20, 1],
        ]))

        # self.obj.draw(self.canvas_arr)
        #
        # self.img = ImageTk.PhotoImage(Image.fromarray(self.canvas_arr))

        self.canvas = tk.Canvas(master, width=self.w, height=self.h)
        self.update()
        # self.canvas.create_image(0, 0, anchor='nw', image=self.img)

        self.canvas.grid(row=0, column=0)

        # fig = Figure(figsize=(5, 4), dpi=100)
        # ax = fig.add_subplot(111)
        # self.line, = ax.plot(range(10))
        # #
        # w, h = 100, 100
        # self.c = tk.Canvas(master, width=w, height=h)
        # self.c.create_rectangle(0, 0, 100, 100, fill="red")
        #
        # self.canvas = FigureCanvasTkAgg(fig, master=self.c)
        # self.canvas.draw()
        # self.canvas.get_tk_widget().grid(row=0, column=0)
        #
        # self.c.grid(row=0, column=0)
        # # widget.grid(row=0, column=0)

        # self.l_rot = tk.Label(master, text="Rotation: ").grid(row=0, column=0, pady=2)
        # self.l_scale = tk.Label(master, text="Scale: ").grid(row=1, column=0, pady=2)
        #
        # self.e_rot = tk.Entry(master).grid(row=0, column=1, pady=2)
        # self.e_scale = tk.Entry(master).grid(row=1, column=1, pady=2)
        #
        # fig = Figure(figsize=(5, 4), dpi=100)
        # t = np.arange(0, 3, .01)
        # fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))
        #
        # canvas = FigureCanvasTkAgg(fig, master=master)
        # canvas.draw()
        # canvas.get_tk_widget().grid(row=0, column=2)

    def rotate(self):

        # print(self.obj.points)

        self.obj.rotate(60, point=self.obj.center_point)
        self.update()

    def increase(self):
        self.obj.move(10, 10)
        self.update()

    def decrease(self):
        self.obj.move(-10, -10)
        self.update()

    def update(self):
        self.canvas_arr = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        self.obj.draw(self.canvas_arr)

        self.img = ImageTk.PhotoImage(Image.fromarray(self.canvas_arr.astype(np.uint8)))

        self.canvas.create_image(0, 0, anchor='nw', image=self.img)

