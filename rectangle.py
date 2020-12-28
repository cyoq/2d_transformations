from typing import Tuple

from line import Line
from object import Object
from pivot import *


class Rectangle(Object):

    def __init__(self, program, canvas, points):
        super().__init__(program, canvas, points, "Rectangle")

    def choose_pivot(self, canvas, pivot_type):
        canvas.delete("all")
        self.active_pivots = pivot_type
        if self.active_pivots == MP:
            self.pivots = [Pivot(canvas, self.center_point[0], self.center_point[1], self.move, width=8)]
        elif self.active_pivots == SP:
            self.pivots = [
                # 2nd and 4th pivot has different arguments for manual_scale function
                # because x and y's are swapped around
                Pivot(canvas, self.points[0, 0], self.points[0, 1],
                      lambda x, y: self.manual_point_move(x, y, 0), width=8),
                Pivot(canvas, self.points[1, 0], self.points[1, 1],
                      lambda x, y: self.manual_point_move(x, y, 3), width=8),
                Pivot(canvas, self.points[2, 0], self.points[2, 1],
                      lambda x, y: self.manual_point_move(x, y, 2), width=8),
                Pivot(canvas, self.points[3, 0], self.points[3, 1],
                      lambda x, y: self.manual_point_move(x, y, 1), width=8),
            ]
        elif self.active_pivots == RP:
            radius = self.radius()
            stationary_pivot = Pivot(canvas, self.center_point[0], self.center_point[1],
                                     lambda x, y: None, width=8, stationary=True)

            self.pivots = [Pivot(canvas, self.center_point[0] + radius, self.center_point[1],
                                 lambda a: self.rotate(a, point=self.center_point), width=8,
                                 angle_based=True, center=stationary_pivot, radius=radius),
                           stationary_pivot
                           ]
        else:
            raise Exception("No such pivot type!")

        for p in self.pivots:
            p.register_observer(self.program)

        self.recalculate_pivots()

    def manual_point_move(self, dx, dy, i):
        if i == 0:
            self.points[i, 0] += dx
            self.points[i, 1] += dy
            self.points[4, 0] += dx
            self.points[4, 1] += dy
        else:
            self.points[i, 0] += dx
            self.points[i, 1] += dy

    def radius(self):
        midx, midy = self.midpoint()
        vector = (midx - self.points[1, 0], midy - self.points[1, 1])
        return (vector[0] ** 2 + vector[1] ** 2) ** 0.5

    def midpoint(self):
        return ((self.points[0, 0] + self.points[2, 0]) // 2,
                (self.points[0, 1] + self.points[2, 1]) // 2)

    def recalculate_pivots(self):
        if self.active_pivots == MP:
            midx, midy = self.midpoint()
            self.pivots[0].update_pos(midy, midx)
        elif self.active_pivots == SP:
            self.pivots[0].update_pos(self.points[0, 1], self.points[0, 0])
            self.pivots[1].update_pos(self.points[3, 1], self.points[3, 0])
            self.pivots[2].update_pos(self.points[2, 1], self.points[2, 0])
            self.pivots[3].update_pos(self.points[1, 1], self.points[1, 0])
        elif self.active_pivots == RP:
            midx, midy = self.midpoint()
            self.pivots[1].update_pos(midy, midx)
            self.pivots[0].update_pos(midy + self.radius(), midx)
        else:
            raise Exception("No such pivot type!")

    @classmethod
    def create_object(cls, start_point, end_point, program, canvas):
        points = np.array([
            [start_point[0], start_point[1], 1],
            [end_point[0], start_point[1], 1],
            [end_point[0], end_point[1], 1],
            [start_point[0], end_point[1], 1],
            [start_point[0], start_point[1], 1],
        ])
        return cls(program, canvas, points)

    def draw(self, canvas_arr, color):
        for pp, p in zip(self.points, self.points[1:]):
            Line.draw(canvas_arr, pp[0], pp[1], p[0], p[1], color)

    def is_inside(self, x, y):
        if self.points[0, 0] <= x <= self.points[2, 0] and self.points[0, 1] <= y <= self.points[2, 1]:
            return True
        return False

    def move(self, xs, ys):
        super().move(xs, ys)

    def scale(self, x, y):
        super().scale(x, y)

    def rotate(self, angle: int, point: Tuple[int, int] = None):
        super().rotate(angle, point)