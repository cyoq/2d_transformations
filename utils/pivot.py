import tkinter as tk
from collections import deque
from typing import Callable, Tuple, Optional

import numpy as np

from utils.observer import Observable

MP = "M"  # Move pivot
TP = "T"  # Transformation pivot
RP = "R"  # Rotation pivot


class Pivot(Observable):

    def __init__(self,
                 canvas: tk.Canvas,
                 x: int, y: int,
                 f: Callable,
                 width: int = 8,
                 color: str = "blue",
                 stationary: bool = False,
                 angle_based: bool = False,
                 rotation_pivot: "Pivot" = None,
                 distance_to_rot_pivot: int = None,
                 is_moving_on_line=False,
                 axis: str = None):
        """
        Creates a pivot for controlling the object.

        :param canvas: is used for drawing rectangles on the canvas_arr
        :param x: x coordinate
        :param y: y coordinate
        :param f: function which will be called when pivot is moved. By default gets called with 2 arguments: dy and dx.
            When angle_based is on, it is called with 1 argument: angle. When is_moving_on_line is on, then it is called
            with 1 argument: dx or dy, depending on the axis
        :param width: the width of a rectangle
        :param color: color of a rectangle
        :param stationary: turns off the possibility of moving a pivot
        :param angle_based: turns on the rotation movement mode, so that pivot can be moved only by circular trajectory
        :param rotation_pivot: a pivot by which rotation will be done
        :param distance_to_rot_pivot: distance to the rotation pivot from moving pivot
        :param is_moving_on_line: restricts pivot movement only by one axis
        :param axis: axis by which pivot can be moved. Use 'x' or 'y'
        """
        super().__init__()
        self.width = width
        self.color = color
        self.canvas = canvas
        self.canvas_height = int(canvas.cget("height"))
        self.canvas_width = int(canvas.cget("width"))
        self.f = f
        self.angle_based = angle_based
        if angle_based:
            self.angle = 0
        if angle_based is True and rotation_pivot is None and distance_to_rot_pivot is None:
            raise Exception("no rotation_pivot pivot and/or distance_to_rot_pivot for angle based movement!")
        self.rotation_pivot = rotation_pivot
        self.distance_to_rot_point = distance_to_rot_pivot

        if is_moving_on_line and axis is None:
            raise Exception("Cannot create moving on line pivot without an axis!")

        self.is_moving_on_line = is_moving_on_line
        self.axis = axis

        x = x - width // 2
        y = y - width // 2
        self.points = [x, y, x + width, y + width]

        # a queue for storing id of created rectangle which is used in motion binding
        self.history = deque()
        from objects.object import counter
        self.i = next(counter)
        # a tag for canvas_arr binding
        self.tag = "rec" + str(self.i)

        # id for last created rectangle
        self.rec: Optional[int] = None
        # last moved rectangle id after mouse was pressed
        self.last_movable: Optional[int] = None

        self.is_allowed_to_move = False
        self.stationary = stationary
        if not stationary:
            self.canvas.tag_bind(self.tag, '<B1-Motion>', self.move_rect)
            self.canvas.tag_bind(self.tag, "<Motion>", self.check_hand)
            self.canvas.tag_bind(self.tag, "<1>", self.mouse_down)
            # TODO: Bug with cursor
            self.canvas.tag_bind(self.tag, "<ButtonRelease-1>", self.clear_last_movable)

    def clear_last_movable(self, e):
        self.canvas.config(cursor="")
        self.last_movable = None

    def midpoint(self) -> Tuple[int, int]:
        midx, midy = (self.points[0] + self.points[2]) // 2, \
                     (self.points[1] + self.points[3]) // 2
        return midx, midy

    def update_pos(self, x: int, y: int):
        x = x - self.width // 2
        y = y - self.width // 2
        self.points = [x, y, x + self.width, y + self.width]

    def check_hand(self, e):
        bbox = self.canvas.bbox(self.rec)
        # checks whether the mouse is inside the boundaries
        if bbox[0] < e.x < bbox[2] and bbox[1] < e.y < bbox[3]:
            self.canvas.config(cursor="hand2")
        else:
            self.canvas.config(cursor="")

    def move_rect(self, event):
        if self.is_allowed_to_move:
            if not self.angle_based and not self.is_moving_on_line:
                points = self.points
                dx, dy = event.x - points[0], event.y - points[1]
                if self.width < event.x + self.width < self.canvas_width and self.width < event.y + self.width < self.canvas_height:
                    points[0] = event.x
                    points[1] = event.y
                    points[2] = event.x + self.width
                    points[3] = event.y + self.width

                    self.f(dy, dx)
                    self.notify_observers()

            elif self.is_moving_on_line:

                if self.axis == "x":
                    if 0 < event.x + self.width < self.canvas_height:
                        dx = event.x - self.points[0]
                        self.points[0] = event.x
                        self.points[2] = event.x + self.width
                        self.f(dx)
                elif self.axis == "y":
                    if 0 < event.y + self.width < self.canvas_width:
                        dy = event.y - self.points[1]
                        self.points[1] = event.y
                        self.points[3] = event.y + self.width
                        self.f(dy)
                else:
                    raise Exception("Incorrect axis argument! Should be 'x' or 'y'.")

                self.notify_observers()

            else:
                cmidx, cmidy = self.rotation_pivot.midpoint()
                angle = np.arctan2(event.y - cmidy, event.x - cmidx)

                closest = (
                    cmidx + self.distance_to_rot_point * np.cos(angle),
                    cmidy + self.distance_to_rot_point * np.sin(angle))
                if 0 < closest[0] + self.width < self.canvas_width and 0 < closest[1] < self.canvas_height:
                    self.points[0] = closest[0]
                    self.points[1] = closest[1]
                    self.points[2] = closest[0] + self.width
                    self.points[3] = closest[1] + self.width

                    self.f(angle)
                    self.angle = angle
                    self.notify_observers()

    def draw(self, color: Tuple[int, int, int]):

        self.rec = self.canvas.create_rectangle(self.points[0], self.points[1], self.points[2],
                                                self.points[3], fill=Pivot._from_rgb(color), tag=self.tag)

        while len(self.history) != 1 and len(self.history) != 0:
            item = self.history.popleft()
            if item == self.last_movable:
                self.history.append(item)
            else:
                self.canvas.delete(item)

        self.history.append(self.rec)

    def mouse_down(self, e):
        bbox = self.canvas.bbox(self.rec)
        if bbox[0] < e.x < bbox[2] and bbox[1] < e.y < bbox[3]:
            self.last_movable = self.rec
            self.is_allowed_to_move = True
        else:
            self.is_allowed_to_move = False

    def is_inside(self, x: int, y: int) -> bool:
        """
        Checks whether the coordinates are inside of the object.
        """
        return self.points[0] < x < self.points[2] and self.points[1] < y < self.points[3]

    @staticmethod
    def _from_rgb(rgb):
        """
        translates an rgb tuple of int to a tkinter friendly color code
        https://stackoverflow.com/questions/51591456/can-i-use-rgb-in-tkinter/51592104
        """
        r, g, b = rgb
        return f'#{r:02x}{g:02x}{b:02x}'
