import itertools
from typing import Tuple, Type

import tkinter as tk

from pivot import *
from program import Program

DEFAULT_COLOR = (255, 0, 0)

counter = itertools.count()


class Object:

    def __init__(self, program: Program,
                 canvas: tk.Canvas,
                 points: np.ndarray,
                 color: Tuple[int, int, int] = DEFAULT_COLOR):
        self.canvas_size = (int(canvas.cget("height")), int(canvas.cget("width")))
        self.points = points
        self.center_point = self.midpoint()
        self.active_pivots = MP
        self.angle = 0
        self.program = program
        self.color = color
        self.start_points = points
        self.rotation_pivot = self.center_point
        self.is_rot_pivot_changed = False
        i = next(counter)
        self.name = '%s_%d' % ("Object", i)
        self.id = i
        self.pivots = None
        self.choose_pivot(canvas, self.active_pivots)

    def choose_pivot(self, canvas: tk.Canvas, pivot_type: str):
        pass

    def manual_point_move(self, *args, **kwargs):
        pass

    def radius(self) -> int:
        pass

    def midpoint(self) -> Tuple[int, int]:
        pass

    def recalculate_pivots(self):
        pass

    def is_inside(self, x: int, y: int) -> bool:
        pass

    def update_rotation_pivot(self, rotation_pivot: Pivot):
        pass

    def rotation_pivot_to_center(self):
        pass

    @classmethod
    def create_object(cls: Type["Object"],
                      start_point: Tuple[int, int],
                      end_point: Tuple[int, int],
                      program: Program,
                      canvas: tk.Canvas) -> Type["Object"]:
        pass

    def draw(self, canvas_arr: np.ndarray, color: Tuple[int, int, int] = DEFAULT_COLOR):
        pass

    # def fill(self, color=DEFAULT_COLOR):
    #     pass

    # TODO: bug with move
    def move(self, xs: int, ys: int):
        matrix = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [xs, ys, 1]
        ])

        self.points = self.points @ matrix
        max = np.max(self.points)
        min = np.min(self.points)

        if min <= 0 or max >= self.canvas_size[0]:
            self.points = self.points @ np.linalg.inv(matrix)
            self.points = self.points.astype(int)

        self.start_points = self.points
        self.center_point = self.midpoint()
        self.recalculate_pivots()

    def scale(self, x: float, y: float):
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

        if min <= 0 or max >= self.canvas_size[0]:
            self.points = self.points @ np.linalg.inv(matrix)

        self.points = self.points.astype(int)
        self.start_points = self.points
        self.center_point = self.midpoint()
        self.recalculate_pivots()

    def rotate(self, angle: int, point: Tuple[int, int] = None):
        """
        :param angle: angle by which object should be rotated, counting from the starting position, when angle is 0.
            Angle must be given in radians.
        :param point: point by which will be done rotation
        :return: None
        """

        if point is not None:
            point_matrix = np.ones((self.points.shape[0], 3))
            point_matrix[:, 0] *= point[0]
            point_matrix[:, 1] *= point[1]

        old_angle = self.angle
        self.angle = np.rint(np.rad2deg(angle))

        # a = np.deg2rad(self.angle)
        a = angle

        matrix = np.array([
            [np.cos(a), np.sin(a), 0],
            [-np.sin(a), np.cos(a), 0],
            [0, 0, 1]
        ])

        if point is None:
            self.points = self.start_points @ matrix
        else:
            self.points = point_matrix + ((self.start_points - point_matrix) @ matrix)

        max = np.max(self.points)
        min = np.min(self.points)

        if min <= 0 or max >= self.canvas_size[0]:
            self.points = (self.points - point_matrix) @ np.linalg.inv(matrix) + point_matrix
            self.angle = old_angle
        # self.points = self.points.astype(np.int32)
        self.points = np.rint(self.points).astype(int)  # works well with a point in the rotation_pivot
