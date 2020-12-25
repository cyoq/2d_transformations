from typing import Tuple, Optional

import numpy as np
from line import Line

class Object:

    def __init__(self, points):
        self.points = points
        self.center_point = self.recalculate_center()

    def recalculate_center(self):
        return (self.points[0, 0] + self.points[2, 0]) // 2, \
                     (self.points[0, 1] + self.points[2, 1]) // 2

    def intervals(self):
        xmin = int(np.min(self.points[:, 0]))
        xmax = int(np.max(self.points[:, 0]))

        ymin = int(np.min(self.points[:, 1]))
        ymax = int(np.max(self.points[:, 1]))

        return xmin, xmax, ymin, ymax

    def draw(self, canvas):
        for pp, p in zip(self.points, self.points[1:]):
            Line.draw(canvas, pp[0], pp[1], p[0], p[1])

    def move(self, xs, ys):
        matrix = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [xs, ys, 1]
        ])

        self.points = self.points @ matrix
        self.center_point = self.recalculate_center()

    def scale(self, x, y):
        matrix = np.array([
            [x, 0, 0],
            [0, y, 0],
            [0, 0, 1]
        ])

        self.points = self.points @ matrix
        self.center_point = self.recalculate_center()

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
        self.points = self.points.astype(int)
