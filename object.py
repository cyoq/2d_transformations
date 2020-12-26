from typing import Tuple, Optional

import numpy as np

from line import Line
from pivot import *


class Object:

    def __init__(self, program, canvas, points):
        self.points = points
        self.center_point = self.midpoint()
        self.active_pivots = MP
        self.program = program
        self.pivots = None
        self.choose_pivot(canvas, self.active_pivots)

    def choose_pivot(self, canvas, pivot_type):
        canvas.delete("all")
        self.active_pivots = pivot_type
        if self.active_pivots == MP:
            self.pivots = [Pivot(canvas, self.center_point[0], self.center_point[1], self.move,width=8)]
        elif self.active_pivots == SP:
            self.pivots = [
                # 2nd and 4th pivot has different arguments for manual_scale function
                # because x and y's are swapped around
                Pivot(canvas, self.points[0, 0], self.points[0, 1], lambda x, y: self.manual_point_move(x, y, 0), width=8),
                Pivot(canvas, self.points[1, 0], self.points[1, 1], lambda x, y: self.manual_point_move(x, y, 3), width=8),
                Pivot(canvas, self.points[2, 0], self.points[2, 1], lambda x, y: self.manual_point_move(x, y, 2), width=8),
                Pivot(canvas, self.points[3, 0], self.points[3, 1], lambda x, y: self.manual_point_move(x, y, 1), width=8),
            ]
        elif self.active_pivots == RP:
            self.pivots = []
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
            pass
        else:
            raise Exception("No such pivot type!")

    def draw(self, canvas):
        # for sp in self.pivots:
        #     sp.draw()
        for pp, p in zip(self.points, self.points[1:]):
            Line.draw(canvas, pp[0], pp[1], p[0], p[1])

    def move(self, xs, ys):
        matrix = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [xs, ys, 1]
        ])

        self.points = self.points @ matrix
        max = np.max(self.points)
        min = np.min(self.points)

        if min <= 0 or max >= 600:
            self.points = self.points @ np.linalg.inv(matrix)
            self.points = self.points.astype(int)

        self.center_point = self.midpoint()
        self.recalculate_pivots()

    def scale(self, x, y):
        matrix = np.array([
            [x, 0, 0],
            [0, y, 0],
            [0, 0, 1]
        ])

        self.points = self.points @ matrix
        self.center_point = self.midpoint()
        self.recalculate_pivots()

    def rotate(self, angle: int, point: Optional[Tuple[int]] = None):
        if point is not None:
            point_matrix = np.ones((self.points.shape[0], 3))
            point_matrix[:, 0] *= point[0]
            point_matrix[:, 1] *= point[1]

        a = np.deg2rad(angle)

        matrix = np.array([
            [np.cos(a), np.sin(a), 0],
            [-np.sin(a), np.cos(a), 0],
            [0, 0, 1]
        ])

        if point is None:
            self.points = self.points @ matrix
        else:
            self.points = point_matrix + ((self.points - point_matrix) @ matrix)
        # self.points = self.points.astype(np.int32)
        self.points = np.rint(self.points).astype(int)  # works well with a point in the center
