from typing import Tuple, Type

import numpy as np
import tkinter as tk

from objects.object import Object, counter
from consts import DEFAULT_COLOR
from utils.pivot import Pivot, MP, TP, RP


class Circle(Object):

    def __init__(self,
                 program: "Program",
                 canvas: tk.Canvas,
                 points: np.ndarray,
                 radius: int,
                 color: Tuple[int, int, int] = DEFAULT_COLOR):
        self.r = radius
        super().__init__(program, canvas, points, color)
        self.name = '%s_%d' % ("Circle", next(counter))

    def choose_pivot(self, canvas: tk.Canvas, pivot_type: str):
        canvas.delete("all")
        self.active_pivots = pivot_type
        if self.active_pivots == MP:
            self.pivots = [
                Pivot(canvas, self.center_point[1], self.center_point[0], self.move)
            ]
        elif self.active_pivots == TP:
            self.pivots = [
                Pivot(canvas, self.center_point[1] + self.r,
                      self.center_point[0],
                      lambda diff: self.manual_pivot_move(diff),
                      is_moving_on_line=True,
                      axis="x"),
            ]
        elif self.active_pivots == RP:
            pass
        else:
            raise Exception("No such pivot pivot_type!")

        for p in self.pivots:
            p.register_observer(self.program)

        self.recalculate_pivots()

    def manual_pivot_move(self, diff, *args):
        if self.r + diff > 0:
            self.r += diff

        self.recalculate_pivots()

    def radius(self) -> int:
        return self.r

    def midpoint(self) -> Tuple[int, int]:
        return self.points[0, 0], self.points[0, 1]

    def recalculate_pivots(self):
        if self.active_pivots == MP:
            self.pivots[0].update_pos(self.center_point[1], self.center_point[0])
        if self.active_pivots == TP:
            self.pivots[0].update_pos(self.center_point[1] + self.r,
                                      self.center_point[0])

    def is_inside(self, x: int, y: int) -> bool:
        vector = (x - self.center_point[0], y - self.center_point[1])
        dist = (vector[0]**2 + vector[1]**2)**0.5
        return dist <= self.r

    def update_rotation_pivot(self, rotation_pivot: Pivot):
        super().update_rotation_pivot(rotation_pivot)

    def rotation_pivot_to_center(self):
        super().rotation_pivot_to_center()

    @classmethod
    def create_object(cls: Type["Object"],
                      start_point: Tuple[int, int],
                      end_point: Tuple[int, int],
                      program: "Program",
                      canvas: tk.Canvas) -> Object:
        points = np.array([
            [*start_point, 1]
        ])

        vector = (start_point[0] - end_point[0], start_point[1] - end_point[1])
        radius = (vector[0]**2 + vector[1]**2)**0.5

        return cls(program, canvas, points, radius)

    def draw(self, canvas_arr: np.ndarray, color: Tuple[int, int, int] = DEFAULT_COLOR):
        if color != DEFAULT_COLOR:
            self.color = color
        self.__draw(canvas_arr, self.color)

    def move(self, xs: int, ys: int):
        super().move(xs, ys)

    def scale(self, x: float, y: float):
        super().scale(x, y)

    def rotate(self, angle: int, point: Tuple[int, int] = None):
        super().rotate(angle, point)

    def shear(self, x: float, y: float):
        super().shear(x, y)

    def __draw(self, canvas_arr: np.ndarray, color: Tuple[int, int, int] = DEFAULT_COLOR):
        shifts = [(-1, 1), (1, 1), (1, -1), (-1, -1)]
        xc, yc = self.points[0, 1], self.points[0, 0]
        x = 0
        y = np.rint(self.radius()).astype(int)
        p = 1 - np.rint(self.radius()).astype(int)

        while x <= y:

            for (xs, ys) in shifts:
                xd, yd = xs * x + xc, ys * y + yc
                if 0 < xd < self.canvas_width and 0 < yd < self.canvas_height:
                    canvas_arr[yd, xd, :] = color

                # Without centre coordinate difference two circle parts will be apart
                # For example this code does not work:
                # canvas_arr[xd, yd, :] = color
                # Because changing x's and y's by places, we mirror our circle part globally and it appears
                # in a top right from the main part
                # So, in order to set two parts together, we calculate the difference between center coordinates
                # Then we subtract it from x coordinate to go left, and add to y to go down
                diff = xc - yc
                if 0 < xd - diff < self.canvas_width and 0 < yd + diff < self.canvas_height:
                    canvas_arr[xd - diff, yd + diff, :] = color

            if p < 0:
                x += 1
                p = p + 2 * x + 1
            else:
                x += 1
                y -= 1
                p = p + 2 * x - 2 * y + 1

