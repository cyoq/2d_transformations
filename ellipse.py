from object import Object, DEFAULT_COLOR, counter
from pivot import *


class Ellipse(Object):
    def __init__(self, program: "Program",
                 canvas: tk.Canvas,
                 points: np.ndarray,
                 rx: int,
                 ry: int,
                 color: Tuple[int, int, int] = DEFAULT_COLOR):
        self.rx = rx
        self.ry = ry
        super().__init__(program, canvas, points, color)
        self.name = '%s_%d' % ("Ellipse", next(counter))

    def choose_pivot(self, canvas: tk.Canvas, pivot_type: str):
        print(self.center_point)
        canvas.delete("all")
        self.active_pivots = pivot_type
        if self.active_pivots == MP:
            self.pivots = [
                Pivot(canvas, self.center_point[1], self.center_point[0], self.move)
            ]
        elif self.active_pivots == TP:
            self.pivots = [
                Pivot(canvas, self.center_point[1],
                      self.center_point[0] - self.ry,
                      lambda diff: self.manual_pivot_move(diff, "y"),
                      is_moving_on_line=True,
                      axis="y"),
                Pivot(canvas, self.center_point[1] + self.rx,
                      self.center_point[0],
                      lambda diff: self.manual_pivot_move(diff, "x"),
                      is_moving_on_line=True,
                      axis="x"),
            ]
        elif self.active_pivots == RP:
            pass
        else:
            raise Exception("No such pivot pivot_type!")

        for p in self.pivots:
            p.register_observer(self.program)

        self.recalculate_pivots()

    def manual_pivot_move(self, diff: int, axis: str):
        print(self.rx, self.ry)
        if axis == "y":
            if self.ry - diff > 0:
                self.ry -= diff
        elif axis == "x":
            if self.rx + diff > 0:
                self.rx += diff

        self.recalculate_pivots()

    def radius(self) -> Tuple[int, int]:
        return self.rx, self.ry

    def midpoint(self) -> Tuple[int, int]:
        return self.points[0, 0], self.points[0, 1]

    def recalculate_pivots(self):
        if self.active_pivots == MP:
            self.pivots[0].update_pos(self.center_point[1], self.center_point[0])
        if self.active_pivots == TP:
            self.pivots[0].update_pos(self.center_point[1],
                                      self.center_point[0] - self.ry)
            self.pivots[1].update_pos(self.center_point[1] + self.rx,
                                      self.center_point[0])

    def is_inside(self, x: int, y: int) -> bool:
        dx = (self.center_point[0] - x) / self.rx
        dy = (self.center_point[1] - y) / self.ry
        return dx ** 2 + dy ** 2 <= 1

    @classmethod
    def create_object(cls,
                      start_point: Tuple[int, int],
                      end_point: Tuple[int, int],
                      program: "Program",
                      canvas: tk.Canvas):
        points = np.array([
            [start_point[0], start_point[1], 1],
        ])
        ry = end_point[0] - start_point[0]
        rx = end_point[1] - start_point[1]
        return cls(program, canvas, points, rx, ry)

    def draw(self, canvas_arr: np.ndarray, color: Tuple[int, int, int] = DEFAULT_COLOR):
        if color != DEFAULT_COLOR:
            self.color = color
        self.__draw(canvas_arr, self.color)

    def move(self, xs: int, ys: int):
        super().move(xs, ys)

    def scale(self, x: float, y: float):
        super().scale(x, y)

    def rotate(self, angle: int, point: Tuple[int, int] = None):
        super().rotate(angle, point)

    def __draw(self, canvas_arr: np.ndarray, color: Tuple[int, int, int]):
        """ Draws an ellipse using midpoint Bresenham algorithm """
        yc, xc = self.center_point
        rx, ry = self.rx, self.ry
        shifts = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        x, y = 0, ry
        p = ry ** 2 - rx ** 2 * ry + 0.25 * rx ** 2

        while ry ** 2 * x <= rx ** 2 * y:
            for (xs, ys) in shifts:
                xd, yd = xs * x + xc, ys * y + yc
                if yd < self.canvas_height and xd < self.canvas_width:
                    canvas_arr[yd, xd, :] = color

            if p < 0:
                x += 1
                p += 2 * ry ** 2 * x + ry ** 2
            else:
                x += 1
                y -= 1
                p += 2 * ry ** 2 * x + ry ** 2 - 2 * rx ** 2 * y

        if ry ** 2 * x >= rx ** 2 * y:
            p = ry ** 2 * (x + 0.5) ** 2 + rx ** 2 * (y - 1) ** 2 - rx ** 2 * ry ** 2

        while y >= 0:
            for (xs, ys) in shifts:
                xd, yd = xs * x + xc, ys * y + yc
                if yd < self.canvas_height and xd < self.canvas_width:
                    canvas_arr[yd, xd, :] = color

            if p > 0:
                y -= 1
                p += -2 * rx ** 2 * y + rx ** 2
            else:
                x += 1
                y -= 1
                p += -2 * rx ** 2 * y + rx ** 2 + 2 * ry ** 2 * x


