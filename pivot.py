from observer import Observable


class Pivot(Observable):

    def __init__(self, canvas, x, y, f, width=10, color="blue"):
        super().__init__()
        self.width = width
        self.color = color
        self.f = f
        x = x - width // 2
        y = y - width // 2
        self.points = [x, y, x + width, y + width]
        self.rec = canvas.create_rectangle(self.points[0], self.points[1], self.points[2],
                                           self.points[3], fill=color)
        self.canvas = canvas
        self.is_allowed_to_move = False
        self.canvas.bind('<B1-Motion>', self.move_rect)
        self.canvas.bind("<Motion>", self.check_hand)
        self.canvas.bind("<1>", self.mouse_down)

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
            self.rec = self.canvas.create_rectangle(points[0], points[1], points[2],
                                                    points[3], fill=self.color)

    def mouse_down(self, e):
        bbox = self.canvas.bbox(self.rec)
        if bbox[0] < e.x < bbox[2] and bbox[1] < e.y < bbox[3]:
            self.is_allowed_to_move = True
        else:
            self.is_allowed_to_move = False
