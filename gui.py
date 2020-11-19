import tkinter as tk
from typing import Tuple

import numpy as np
from PIL import ImageTk, Image


class Program:

    def __init__(self, master, dimensions: Tuple[int, int]):
        self.image_array = np.zeros((dimensions[0], dimensions[1]))
        self.master = master
        self.master.title("2D Transformation")

        self.label = tk.Label(self.master, text="My first GUI!")
        self.label.pack()

        self.button = tk.Button(self.master, text="Press me!", command=lambda: print("Greetings!"))
        self.button.pack()

        # TODO: Validation
        self.entry = tk.Entry(master=self.master)
        self.entry.pack()

        self.change_checker_btn = tk.Button(self.master, text="change checker pattern",
                                            command=lambda: self.update_canvas(lambda: self.draw_checkerboard(
                                                int(self.entry.get()))))
        self.change_checker_btn.pack()

        h, w = self.image_array.shape
        self.canvas = tk.Canvas(self.master, width=w, height=h)
        self.draw_checkerboard(100)
        self.image = None
        self.convert_image_from_array()
        self.img_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self.image)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.quit_btn = tk.Button(self.master, text="Close", command=self.master.quit)
        self.quit_btn.pack()

    def convert_image_from_array(self):
        # can pass only 2d array to Image
        self.image = ImageTk.PhotoImage(master=self.master, image=Image.fromarray(self.image_array))

    def draw_checkerboard(self, width):
        self.image_array[:] = 0
        h, w = self.image_array.shape
        color = True
        for row in range(h):
            for col in range(w):
                if color:
                    self.image_array[row, col] = 255
                if col % width == 0:
                    color = not color

            if row % width == 0:
                color = not color

    def update_canvas(self, f):
        f()
        self.convert_image_from_array()
        self.canvas.itemconfig(self.img_on_canvas, image=self.image)
