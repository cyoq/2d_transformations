from collections import deque
import numpy as np
from observer import Observable
from generator import gen

MP = "M"  # Move pivot
TP = "T"  # Transformation pivot
RP = "R"  # Rotation pivot


class Pivot(Observable):

    def __init__(self, canvas, x, y, f, width: int = 8, color: str = "blue", stationary=False,
                 angle_based=False, rotation_pivot: "Pivot" = None, distance_to_rot_point: int = None,
                 is_moving_on_line=False, axis: str = None):
        super().__init__()
        self.width = width
        self.color = color
        self.canvas = canvas
        self.canvas_size = (int(canvas.cget("height")), int(canvas.cget("width")))
        self.f = f
        self.angle_based = angle_based
        if angle_based:
            self.angle = 0
        if angle_based is True and rotation_pivot is None and distance_to_rot_point is None:
            raise Exception("no rotation_pivot pivot and/or distance_to_rot_point for angle based movement!")
        self.rotation_pivot = rotation_pivot
        self.distance_to_rot_point = distance_to_rot_point

        if is_moving_on_line and axis is None:
            raise Exception("Cannot create moving on line pivot without an axis!")

        self.is_moving_on_line = is_moving_on_line
        self.axis = axis

        x = x - width // 2
        y = y - width // 2
        self.points = [x, y, x + width, y + width]

        self.history = deque()
        self.i = next(gen)
        self.tag = "rec" + str(self.i)

        self.rec = None
        self.last_movable = None
        # self.rec = self.canvas.create_rectangle(self.points[0], self.points[1], self.points[2],
        #                                         self.points[3], fill=self.color, tag=self.tag)

        self.is_allowed_to_move = False
        self.stationary = stationary
        if not stationary:
            self.canvas.tag_bind(self.tag, '<B1-Motion>', self.move_rect)
            self.canvas.tag_bind(self.tag, "<Motion>", self.check_hand)
            self.canvas.tag_bind(self.tag, "<1>", self.mouse_down)
            # TODO: Bug with cursor
            self.canvas.tag_bind(self.tag, "<ButtonRelease-1>", self.clear_last_movable)

        # self.canvas.bind('<B1-Motion>', self.move_rect)
        # self.canvas.bind("<Motion>", self.check_hand)
        # self.canvas.bind("<1>", self.mouse_down)

    def clear_last_movable(self, e):
        self.canvas.config(cursor="")
        self.last_movable = None

    def midpoint(self):
        midx, midy = (self.points[0] + self.points[2]) // 2, \
                     (self.points[1] + self.points[3]) // 2
        return midx, midy

    def update_pos(self, x, y):
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
                if event.x + self.width < self.canvas_size[1] and event.y + self.width < self.canvas_size[0]:
                    points[0] = event.x
                    points[1] = event.y
                    points[2] = event.x + self.width
                    points[3] = event.y + self.width

                    self.f(dy, dx)
                    self.notify_observers()

            elif self.is_moving_on_line:

                if self.axis == "x":
                    if self.points[2] + self.width < self.canvas_size[1]:
                        dx = event.x - self.points[0]
                        self.points[0] = event.x
                        self.points[2] = event.x + self.width
                        self.f(dx)
                elif self.axis == "y":
                    if self.points[2] + self.width < self.canvas_size[0]:
                        dx = event.y - self.points[1]
                        self.points[1] = event.y
                        self.points[3] = event.y + self.width
                        self.f(dx)
                else:
                    raise Exception("Incorrect axis argument! Should be 'x' or 'y'.")

                self.notify_observers()
            else:
                cmidx, cmidy = self.rotation_pivot.midpoint()
                angle = np.arctan2(event.y - cmidy, event.x - cmidx)

                closest = (cmidx + self.distance_to_rot_point * np.cos(angle), cmidy + self.distance_to_rot_point * np.sin(angle))
                if closest[0] + self.width < self.canvas_size[1] and closest[1] + self.width < self.canvas_size[0]:
                    self.points[0] = closest[0]
                    self.points[1] = closest[1]
                    self.points[2] = closest[0] + self.width
                    self.points[3] = closest[1] + self.width

                    self.f(angle)
                    self.angle = angle
                    self.notify_observers()

    def draw(self, color):

        self.rec = self.canvas.create_rectangle(self.points[0], self.points[1], self.points[2],
                                                self.points[3], fill=self._from_rgb(color), tag=self.tag)

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

    def is_inside(self, x, y):
        if self.points[0] < x < self.points[2] and self.points[1] < y < self.points[3]:
            return True
        return False

    def _from_rgb(self, rgb):
        """
        https://stackoverflow.com/questions/51591456/can-i-use-rgb-in-tkinter/51592104
        translates an rgb tuple of int to a tkinter friendly color code
        """
        r, g, b = rgb
        return f'#{r:02x}{g:02x}{b:02x}'
