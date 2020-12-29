from typing import Tuple

import numpy as np


class Line:

    @staticmethod
    def draw(canvas_width: int,
             canvas_height: int,
             canvas_arr: np.ndarray,
             x_start: int,
             y_start: int,
             x_end: int,
             y_end: int,
             color: Tuple[int, int, int] = (255, 0, 0)):
        """ Creates a line using Bresenham midpoint algorithm"""
        dx = abs(x_end - x_start)
        dy = abs(y_end - y_start)

        xs = 1 if x_start < x_end else -1
        ys = 1 if y_start < y_end else -1

        x = x_start
        y = y_start

        if dx > dy:
            pn = 2 * dy - dx
            while x != x_end:
                if pn > 0:
                    x += xs
                    y += ys
                    pn = pn + 2 * dy - 2 * dx
                else:
                    x += xs
                    pn = pn + 2 * dy
                # place for drawing
                if x < canvas_height and y < canvas_width:
                    canvas_arr[x, y, :] = color
        else:
            pn = 2 * dx - dy
            while y != y_end:
                if pn > 0:
                    x += xs
                    y += ys
                    pn = pn + 2 * dx - 2 * dy
                else:
                    y += ys
                    pn = pn + 2 * dx
                # place for drawing
                if x < canvas_height and y < canvas_width:
                    canvas_arr[x, y, :] = color
