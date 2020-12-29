from typing import Tuple

from object import Object, DEFAULT_COLOR
from pivot import *


class Ellipse(Object):
    def __init__(self, program, canvas, points, rx, ry, color=DEFAULT_COLOR):
        self.rx = rx
        self.ry = ry
        super().__init__(program, canvas, points, color)
        self.name = '%s_%d' % ("Ellipse", next(self._counter))

    def choose_pivot(self, canvas, pivot_type):
        print(self.center_point)
        canvas.delete("all")
        self.active_pivots = pivot_type
        if self.active_pivots == MP:
            self.pivots = [
                Pivot(canvas, self.center_point[1], self.center_point[0], self.move)
            ]
        elif self.active_pivots == SP:
            self.pivots = [
                Pivot(canvas, self.center_point[1],
                      self.center_point[0] - self.ry,
                      lambda diff: self.manual_point_move(diff, "y"),
                      is_moving_on_line=True,
                      axis="y"),
                Pivot(canvas, self.center_point[1] + self.rx,
                      self.center_point[0],
                      lambda diff: self.manual_point_move(diff, "x"),
                      is_moving_on_line=True,
                      axis="x"),
            ]
        elif self.active_pivots == RP:
            pass
        else:
            raise Exception("No such pivot type!")

        for p in self.pivots:
            p.register_observer(self.program)

        self.recalculate_pivots()

    def manual_point_move(self, diff, axis):
        print(self.rx, self.ry)
        if axis == "y":
            if self.ry - diff > 0:
                self.ry -= diff
        elif axis == "x":
            if self.rx + diff > 0:
                self.rx += diff

        self.recalculate_pivots()

    def radius(self):
        return self.rx, self.ry

    def midpoint(self):
        return self.points[0, 0], self.points[0, 1]

    def recalculate_pivots(self):
        if self.active_pivots == SP:
            self.pivots[0].update_pos(self.center_point[1],
                      self.center_point[0] - self.ry)
            self.pivots[1].update_pos(self.center_point[1] + self.rx,
                      self.center_point[0])

    def is_inside(self, x, y):
        dx = (self.center_point[0] - x) / self.rx
        dy = (self.center_point[1] - y) / self.ry
        if dx**2 + dy**2 <= 1:
            return True
        return False

    @classmethod
    def create_object(cls, start_point, end_point, program, canvas):
        points = np.array([
            [start_point[0], start_point[1], 1],
        ])
        ry = end_point[0] - start_point[0]
        rx = end_point[1] - start_point[1]
        return cls(program, canvas, points, rx, ry)

    def draw(self, canvas_arr, color=DEFAULT_COLOR):
        if color != DEFAULT_COLOR:
            self.color = color
        self.__draw(canvas_arr, self.color)

    def move(self, xs, ys):
        super().move(xs, ys)

    def scale(self, x, y):
        super().scale(x, y)

    def rotate(self, angle: int, point: Tuple[int, int] = None) -> None:
        super().rotate(angle, point)

    def __draw(self, canvas_arr, color):
        yc, xc = self.center_point
        rx, ry = self.rx, self.ry
        shifts = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        x, y = 0, ry
        p = ry ** 2 - rx ** 2 * ry + 0.25 * rx ** 2
        # need to fill 2 pixels which are in a
        # middle x and in a distance ry and -ry
        canvas_arr[yc + y, xc + x, :] = color
        canvas_arr[yc - y, xc - x, :] = color

        while ry ** 2 * x <= rx ** 2 * y:
            if p < 0:
                x += 1
                p += 2 * ry ** 2 * x + ry ** 2
            else:
                x += 1
                y -= 1
                p += 2 * ry ** 2 * x + ry ** 2 - 2 * rx ** 2 * y

            for (xs, ys) in shifts:
                xd, yd = xs * x + xc, ys * y + yc
                canvas_arr[yd, xd, :] = color

        if ry ** 2 * x >= rx ** 2 * y:
            p = ry ** 2 * (x + 0.5) ** 2 + rx ** 2 * (y - 1) ** 2 - rx ** 2 * ry ** 2

        while y >= 0:
            if p > 0:
                y -= 1
                p += -2 * rx ** 2 * y + rx ** 2
            else:
                x += 1
                y -= 1
                p += -2 * rx ** 2 * y + rx ** 2 + 2 * ry ** 2 * x

            for (xs, ys) in shifts:
                xd, yd = xs * x + xc, ys * y + yc
                canvas_arr[yd, xd, :] = color
