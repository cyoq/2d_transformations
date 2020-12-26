from observer import Observable
from collections import deque

MP = "M"  # Move pivot
SP = "S"  # Scale pivot
RP = "R"  # Rotation pivot

def iterator():
    i = 0
    while True:
        i += 1
        yield i

gen = iterator()


class Pivot(Observable):

    def __init__(self, canvas, x, y, f, width=10, color="blue"):
        super().__init__()
        self.width = width
        self.color = color
        self.canvas = canvas
        self.f = f

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
        self.canvas.tag_bind(self.tag, '<B1-Motion>', self.move_rect)
        self.canvas.tag_bind(self.tag, "<Motion>", self.check_hand)
        self.canvas.tag_bind(self.tag, "<1>", self.mouse_down)

        # self.canvas.bind('<B1-Motion>', self.move_rect)
        # self.canvas.bind("<Motion>", self.check_hand)
        # self.canvas.bind("<1>", self.mouse_down)


    def update_pos(self, x, y):
        x = x - self.width // 2
        y = y - self.width // 2
        self.points = [x, y, x + self.width, y + self.width]
        # self.draw()

    def check_hand(self, e):
        bbox = self.canvas.bbox(self.rec)
        # checks whether the mouse is inside the boundaries
        if bbox[0] < e.x < bbox[2] and bbox[1] < e.y < bbox[3]:
            self.canvas.config(cursor="hand2")
        else:
            self.canvas.config(cursor="")

    def move_rect(self, event):
        if self.is_allowed_to_move:

            points = self.points
            dx, dy = event.x - points[0], event.y - points[1]
            points[0] = event.x
            points[1] = event.y
            points[2] = event.x + self.width
            points[3] = event.y + self.width

            self.f(dy, dx)
            self.notify_observers()

    def draw(self):

        # self.canvas.delete(self.rec)

        self.rec = self.canvas.create_rectangle(self.points[0], self.points[1], self.points[2],
                                                self.points[3], fill=self.color, tag=self.tag)

        print("tag:", self.tag)

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
