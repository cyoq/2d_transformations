from typing import Tuple

from pivot import *
from generator import Generator


class Object:

    # TODO: name fix
    _name_counter = Generator().generator()  # counter for giving names

    def __init__(self, program, canvas, points, name: str = "Object"):
        self.points = points
        self.center_point = self.midpoint()
        self.active_pivots = MP
        self.angle = 0
        self.program = program
        self._class_name = name
        self.name = "{}{}".format(self._class_name, next(self._name_counter))
        self.pivots = None
        self.choose_pivot(canvas, self.active_pivots)

    def choose_pivot(self, canvas, pivot_type):
        pass

    def manual_point_move(self, dx, dy, i):
        pass

    def radius(self):
        pass

    def midpoint(self):
        pass

    def recalculate_pivots(self):
        pass

    def is_inside(self, x, y):
        pass

    @classmethod
    def create_object(cls, start_point, end_point, program, canvas):
        pass

    def draw(self, canvas_arr, color):
        pass

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
        # Scaling is done from (0, 0), so that figure won't move
        dx = np.min(self.points[:, 0])
        dy = np.min(self.points[:, 1])
        self.points[:, 0] -= dx
        self.points[:, 1] -= dy

        matrix = np.array([
            [x, 0, 0],
            [0, y, 0],
            [0, 0, 1]
        ])

        self.points = self.points @ matrix
        self.points[:, 0] += dx
        self.points[:, 1] += dy

        max = np.max(self.points)
        min = np.min(self.points)

        if min <= 0 or max >= 600:
            self.points = self.points @ np.linalg.inv(matrix)

        self.points = self.points.astype(int)
        self.center_point = self.midpoint()
        self.recalculate_pivots()

    def rotate(self, angle: int, point: Tuple[int, int] = None):

        if point is not None:
            point_matrix = np.ones((self.points.shape[0], 3))
            point_matrix[:, 0] *= point[0]
            point_matrix[:, 1] *= point[1]

        self.angle += angle
        self.angle %= 360

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
        # self.center_point = self.midpoint()
        self.points = np.rint(self.points).astype(int)  # works well with a point in the center
        # self.recalculate_pivots()
