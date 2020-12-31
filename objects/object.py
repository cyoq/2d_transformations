import itertools
from typing import Type

from consts import DEFAULT_COLOR
from utils.pivot import *

# Global counter for object names, in order to differentiate them
counter = itertools.count()


class Object:

    def __init__(self,
                 program: "Program",
                 canvas: tk.Canvas,
                 points: np.ndarray,
                 color: Tuple[int, int, int] = DEFAULT_COLOR):
        """
        Creates an object, which can be seen on the canvas_arr. It is possible to move, rotate and transform the object.


        :param program: is used for registering the pivots as observables. Use class Program.
        :param canvas: is used for drawing pivots
        :param points: should describe the object structure in the canvas_arr. It should be a numpy array where each row has 3 columns: [x y 1]
        :param color: color which will be used for drawing the outlines of the object
        """
        self.canvas_height = int(canvas.cget("height"))
        self.canvas_width = int(canvas.cget("width"))
        self.points = points
        self.center_point = self.midpoint()
        self.active_pivots = MP
        self.angle = 0  # angle of the object in degrees
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
        """
        Changes the pivots on the screen. Update should be used after calling this function.

        :param pivot_type: might be MP - movement pivots, TP - transformation pivots, RP - rotation pivots
        """
        pass

    def manual_pivot_move(self, *args, **kwargs):
        """
        Implements the actions when pivots are moved on the screen.
        Update should be used after calling this function.
        """
        pass

    def radius(self) -> int:
        """
        Gives a radius of the object
        """
        pass

    def midpoint(self) -> Tuple[int, int]:
        """
        Gives a middle point coordinates of the object.
        """
        pass

    def recalculate_pivots(self):
        """
        Recalculates the positions of pivots. Update should be used after calling this function.
        """
        pass

    def is_inside(self, x: int, y: int) -> bool:
        """
        Checks whether the coordinates are inside of the object
        """
        pass

    def update_rotation_pivot(self, rotation_pivot: Pivot):
        """
        Updates current rotation pivot to the new one. Update should be used after calling this function.
        :param rotation_pivot: it must be stationary to use in this method
        """
        pass

    def rotation_pivot_to_center(self):
        """
        Returns stationary rotation pivot to the center of the object.
        Update should be used after calling this function.
        """
        pass

    @classmethod
    def create_object(cls: Type["Object"],
                      start_point: Tuple[int, int],
                      end_point: Tuple[int, int],
                      program: "Program",
                      canvas: tk.Canvas) -> Type["Object"]:
        """
        Creates a new object instance.

        :param program: program is needed to register observers on pivots
        """
        pass

    def draw(self, canvas_arr: np.ndarray, color: Tuple[int, int, int] = DEFAULT_COLOR):
        """
        Method for drawing a shape on the numpy array as a canvas_arr

        :param canvas_arr: numpy array as canvas_arr which represents the whole scene
        :param color: color, which will be used for outlines
        """
        pass

    # TODO: bug with move
    def move(self, xs: int, ys: int):
        """
        Moves the object using movement matrix.
        Update should be used after calling this function.

        :param xs: movement by x coordinate
        :param ys: movement by y coordinate
        """
        matrix = np.array([
            [1, 0, 0],
            [0, 1, 0],
            [xs, ys, 1]
        ])

        self.points = self.points @ matrix

        self.start_points = self.points
        self.center_point = self.midpoint()
        self.recalculate_pivots()

    def scale(self, x: float, y: float):
        """
        Scales the object using scaling matrix.
        Update should be used after calling this function.

        :param x: scaling by x coordinate
        :param y: scaling by y coordinate
        """
        # Scaling is done from (0, 0), so that figure won't move after scaling
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

        self.points = self.points.astype(int)
        self.start_points = self.points
        self.center_point = self.midpoint()
        self.recalculate_pivots()

    def rotate(self, angle: int, point: Tuple[int, int] = None):
        """
        Rotates the object using rotation matrix.
        Update should be used after calling this function.

        :param angle: angle by which object should be rotated, counting from the starting position, when angle is 0.
            Angle must be given in radians.
        :param point: point by which will be done rotation
        """

        if point is not None:
            point_matrix = np.ones((self.points.shape[0], 3))
            point_matrix[:, 0] *= point[0]
            point_matrix[:, 1] *= point[1]

        self.angle = np.rint(np.rad2deg(angle))

        a = -angle

        matrix = np.array([
            [np.cos(a), np.sin(a), 0],
            [-np.sin(a), np.cos(a), 0],
            [0, 0, 1]
        ])

        if point is None:
            self.points = self.start_points @ matrix
        else:
            self.points = point_matrix + ((self.start_points - point_matrix) @ matrix)

        # self.points = self.points.astype(np.int32)
        self.points = np.rint(self.points).astype(int)  # works well with a point in the rotation_pivot
        self.center_point = self.midpoint()
