import itertools

from line import Line
from object import Object, DEFAULT_COLOR, counter
from pivot import *


class Rectangle(Object):

    def __init__(self,
                 program: "Program",
                 canvas: tk.Canvas,
                 points: np.ndarray,
                 color: Tuple[int, int, int] = DEFAULT_COLOR):
        super().__init__(program, canvas, points, color=color)
        self.name = '%s_%d' % ("Rectangle", next(counter))

    def choose_pivot(self, canvas: tk.Canvas, pivot_type: str):
        canvas.delete("all")
        self.active_pivots = pivot_type
        if self.active_pivots == MP:
            self.pivots = [Pivot(canvas, self.center_point[0], self.center_point[1], self.move)]
        elif self.active_pivots == TP:
            self.pivots = [
                # 2nd and 4th pivot has different arguments for manual_scale function
                # because x and y's are swapped around
                Pivot(canvas, self.points[0, 0], self.points[0, 1],
                      lambda x, y: self.manual_pivot_move(x, y, 0)),
                Pivot(canvas, self.points[1, 0], self.points[1, 1],
                      lambda x, y: self.manual_pivot_move(x, y, 3)),
                Pivot(canvas, self.points[2, 0], self.points[2, 1],
                      lambda x, y: self.manual_pivot_move(x, y, 2)),
                Pivot(canvas, self.points[3, 0], self.points[3, 1],
                      lambda x, y: self.manual_pivot_move(x, y, 1)),
            ]
        elif self.active_pivots == RP:
            radius = self.radius()
            stationary_pivot = Pivot(canvas,
                                     self.center_point[0],
                                     self.center_point[1],
                                     lambda x, y: None,
                                     stationary=True)

            self.pivots = [Pivot(canvas,
                                 self.center_point[0] + radius,
                                 self.center_point[1],
                                 lambda a: self.rotate(a, point=self.center_point),
                                 angle_based=True,
                                 rotation_pivot=stationary_pivot,
                                 distance_to_rot_pivot=radius),
                           stationary_pivot
                           ]
        else:
            raise Exception("No such pivot pivot_type!")

        for p in self.pivots:
            p.register_observer(self.program)

        self.recalculate_pivots()

    def manual_pivot_move(self, dx: int, dy: int, i: int):
        if i == 0:
            self.points[i, 0] += dx
            self.points[i, 1] += dy
            self.points[4, 0] += dx
            self.points[4, 1] += dy
        else:
            self.points[i, 0] += dx
            self.points[i, 1] += dy

        self.start_points = self.points

    def radius(self) -> int:
        midx, midy = self.midpoint()
        vector = (midx - self.points[1, 0], midy - self.points[1, 1])
        return (vector[0] ** 2 + vector[1] ** 2) ** 0.5

    def midpoint(self) -> Tuple[int, int]:
        return ((self.points[0, 0] + self.points[2, 0]) // 2,
                (self.points[0, 1] + self.points[2, 1]) // 2)

    def update_rotation_pivot(self, rotation_pivot: Pivot):
        self.is_rot_pivot_changed = True
        if self.active_pivots != RP:
            raise Exception("Point must be set when rotation mode is on!")
        if not rotation_pivot.stationary:
            raise Exception("Pivot must be stationary!")
        self.pivots[0].rotation_pivot = rotation_pivot
        points = rotation_pivot.points
        self.pivots[0].f = lambda angle: self.rotate(angle, point=(points[1], points[2]))
        self.pivots[1] = rotation_pivot
        self.recalculate_pivots()

    def rotation_pivot_to_center(self):
        self.pivots[1].points[0] = self.center_point[0]
        self.pivots[1].points[1] = self.center_point[1]

        self.pivots[0].f = lambda angle: self.rotate(angle, point=self.center_point)
        self.is_rot_pivot_changed = False
        self.recalculate_pivots()

    def recalculate_pivots(self):
        if self.active_pivots == MP:
            midx, midy = self.midpoint()
            self.pivots[0].update_pos(midy, midx)
        elif self.active_pivots == TP:
            self.pivots[0].update_pos(self.points[0, 1], self.points[0, 0])
            self.pivots[1].update_pos(self.points[3, 1], self.points[3, 0])
            self.pivots[2].update_pos(self.points[2, 1], self.points[2, 0])
            self.pivots[3].update_pos(self.points[1, 1], self.points[1, 0])
        elif self.active_pivots == RP:
            midx, midy = self.midpoint()
            if not self.is_rot_pivot_changed:
                self.pivots[1].update_pos(midy, midx)
            self.pivots[0].update_pos(midy + self.radius(), midx)
        else:
            raise Exception("No such pivot pivot_type!")

    @classmethod
    def create_object(cls,
                      start_point: Tuple[int, int],
                      end_point: Tuple[int, int],
                      program: "Program",
                      canvas: tk.Canvas) -> "Rectangle":
        points = np.array([
            [start_point[0], start_point[1], 1],
            [end_point[0], start_point[1], 1],
            [end_point[0], end_point[1], 1],
            [start_point[0], end_point[1], 1],
            [start_point[0], start_point[1], 1],
        ])
        return cls(program, canvas, points)

    def draw(self, canvas_arr: np.ndarray, color: Tuple[int, int, int] = DEFAULT_COLOR):
        if color != DEFAULT_COLOR:
            self.color = color
        for pp, p in zip(self.points, self.points[1:]):
            Line.draw(self.canvas_width,
                      self.canvas_height,
                      canvas_arr, pp[0], pp[1], p[0], p[1], self.color)

    def is_inside(self, x: int, y: int) -> bool:
        if self.points[0, 0] <= x <= self.points[2, 0] and self.points[0, 1] <= y <= self.points[2, 1]:
            return True
        for p in self.pivots:
            if p.is_inside(x, y):
                return True
        return False

    def flood_fill(self, x, y, canvas_arr, target_color, replacement_color, outline_color):
        """
        Very slow. Use cautiously!
        """
        if np.all(canvas_arr[x, y, :] == outline_color) or np.all(canvas_arr[x, y, :] == replacement_color):
            return

        if np.all(canvas_arr[x, y, :] != target_color):
            return

        queue = deque()
        queue.append((x, y))

        while queue:
            item = queue.pop()

            if np.all(canvas_arr[item[0], item[1]] == target_color):
                canvas_arr[item[0], item[1]] = replacement_color

                queue.append((item[0] - 1, item[1]))
                queue.append((item[0] + 1, item[1]))

                queue.append((item[0], item[1] + 1))
                queue.append((item[0], item[1] - 1))

                # queue.append((item[0] + 1, item[1] + 1))
                # queue.append((item[0] - 1, item[1] + 1))
                #
                # queue.append((item[0] + 1, item[1] - 1))
                # queue.append((item[0] - 1, item[1] - 1))

    def move(self, xs: int, ys: int):
        super().move(xs, ys)

    def scale(self, x: float, y: float):
        super().scale(x, y)

    def rotate(self, angle: int, point: Tuple[int, int] = None):
        super().rotate(angle, point)
