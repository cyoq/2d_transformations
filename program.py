import tkinter as tk
from typing import Tuple, Type, Optional

from PIL import Image, ImageTk

from consts import ROT_ANGLE
from generator import Generator
from object import Object
from observer import Observer
from pivot import *
from rectangle import Rectangle

font_styles = {
    "simple": ("Courier", 11),
    "heading": ("Courier", 12, "bold"),
    "bold": ("Courier", 11, "bold")
}

# keys for accessing color dictionary
CANVAS = "canvas"
PIVOT = "pivot"
LINE = "line"

name_generator = {
    "Rectangle": Generator().generator()
}


class Program(Observer):

    def __init__(self, master, dimensions: Tuple[int, int], debug=False):
        self.master = master
        self.master.title("2D Transformations")
        self.debug = debug

        self.text_coords = []
        self.show_coords = False
        self.angle = 0

        # second argument is an object type
        self.is_object_creation: Tuple[bool, Optional[Type[Object]]] = (False, None)
        self.start_x = 0
        self.start_y = 0
        self.last_created = None

        self.image = None
        self.current_object: Optional[Type[Object]] = None

        self.color_entries = {
            CANVAS: [],
            PIVOT: [],
            LINE: []
        }
        self.colors = {
            CANVAS: (0, 0, 0),
            PIVOT: (0, 0, 255),
            LINE: (255, 0, 0)
        }

        self.h, self.w = 800, 800

        self.canvas = tk.Canvas(master, width=self.w, height=self.h)

        self.canvas_arr = np.zeros((self.h, self.w, 3), dtype=np.uint8)

        self.objs = {}

        self.obj = Rectangle(self, self.canvas, np.array([
            [20, 20, 1],
            [80, 20, 1],
            [80, 80, 1],
            [20, 80, 1],
            [20, 20, 1],
        ]))

        self.current_object = self.obj

        self.objs[self.obj.id] = self.obj

        self.img = ImageTk.PhotoImage(Image.fromarray(self.canvas_arr))

        # self.canvas.create_image(0, 0, anchor='nw', image=self.img)

        self.canvas.grid(row=0, column=0, rowspan=4)

        # Information frame
        info_frame = tk.Frame(master)
        tk.Label(info_frame, text="Information about the object:", font=font_styles["heading"], foreground="red") \
            .grid(row=0, column=0, sticky=tk.NW, pady=1, columnspan=3)

        tk.Label(info_frame, text="Current object: ", font=font_styles["bold"]) \
            .grid(row=1, column=0, sticky=tk.NW)
        self.object_name_label_var = tk.StringVar()
        self.object_name_label_var.set(self.obj.name)
        self.object_name_label = tk.Label(info_frame, textvariable=self.object_name_label_var,
                                          font=font_styles["simple"])
        self.object_name_label.grid(row=1, column=1, sticky=tk.W)

        tk.Label(info_frame, text="Midpoint coordinates: ", font=font_styles["bold"]) \
            .grid(row=2, column=0, sticky=tk.NW)
        midx, midy = self.obj.midpoint()
        self.mid_label_var = tk.StringVar()
        self.mid_label_var.set("({}, {})".format(midy, midx))
        self.mid_coords = tk.Label(info_frame, textvariable=self.mid_label_var, font=font_styles["simple"])
        self.mid_coords.grid(row=2, column=1, sticky=tk.W)

        tk.Label(info_frame, text="Current angle: ", font=font_styles["bold"]) \
            .grid(row=3, column=0, sticky=tk.NW)
        self.angle_label_var = tk.StringVar()
        self.angle_label_var.set("{} degrees".format(self.obj.angle))
        self.object_angle_label = tk.Label(info_frame, textvariable=self.angle_label_var,
                                           font=font_styles["simple"])
        self.object_angle_label.grid(row=3, column=1, sticky=tk.W)

        tk.Button(info_frame, text="Delete current object", command=self.delete_current_object,
                  font=font_styles["simple"]) \
            .grid(row=4, column=0, pady=2, sticky=tk.NW)

        self.needs_text_coords = tk.IntVar()
        self.needs_text_coords.set(0)
        self.checkbox = tk.Checkbutton(info_frame, text="Show coordinates?", font=font_styles["simple"],
                                       variable=self.needs_text_coords, command=self.check_show_coords)
        self.checkbox.grid(row=5, column=0, sticky=tk.NW)

        info_frame.grid(row=0, column=1, columnspan=3, rowspan=6, sticky=tk.NW)

        # Operation Frame
        operation_frame = tk.Frame(master)
        tk.Label(operation_frame, text="Operations on the object:", font=font_styles["heading"], foreground="red") \
            .grid(row=0, column=0, sticky=tk.NW, pady=1, columnspan=3)

        tk.Label(operation_frame, text="Manipulation modes: ", font=font_styles["bold"]) \
            .grid(row=1, column=0, sticky=tk.NW)

        tk.Button(operation_frame, text="Transformation mode", command=lambda: self.change_pivot_type(SP),
                  font=font_styles["simple"]) \
            .grid(row=2, column=0, sticky=tk.NW, pady=3, padx=3)
        tk.Button(operation_frame, text="Position mode", command=lambda: self.change_pivot_type(MP),
                  font=font_styles["simple"]) \
            .grid(row=2, column=1, sticky=tk.NW, pady=3, padx=3)
        tk.Button(operation_frame, text="Rotation mode", command=lambda: self.change_pivot_type(RP),
                  font=font_styles["simple"]) \
            .grid(row=2, column=2, sticky=tk.NW, pady=3, padx=3)

        tk.Label(operation_frame, text="Input manipulation", font=font_styles["bold"]) \
            .grid(row=3, column=0, sticky=tk.NW)
        tk.Label(operation_frame, text="Move by: ", font=font_styles["bold"]) \
            .grid(row=4, column=0, sticky=tk.NW)

        # TODO: spacing
        # Move
        tk.Label(operation_frame, text="X: ", font=font_styles["bold"]) \
            .grid(row=4, column=1, sticky=tk.NW)
        self.move_entry_x = tk.Entry(operation_frame)
        self.move_entry_x.insert(0, 0)
        self.move_entry_x.grid(row=4, column=2)

        tk.Label(operation_frame, text="Y: ", font=font_styles["bold"]) \
            .grid(row=4, column=3, sticky=tk.NW)
        self.move_entry_y = tk.Entry(operation_frame)
        self.move_entry_y.insert(0, 0)
        self.move_entry_y.grid(row=4, column=4)

        tk.Button(operation_frame, text="Move it!", command=self.move, font=font_styles["simple"]) \
            .grid(row=4, column=5, sticky=tk.N, padx=2, pady=2)

        # Scaling
        tk.Label(operation_frame, text="Scale factor: ", font=font_styles["bold"]) \
            .grid(row=5, column=0, sticky=tk.NW)
        self.scale_entry = tk.Entry(operation_frame)
        self.scale_entry.insert(0, 1)
        self.scale_entry.grid(row=5, column=1)
        tk.Button(operation_frame, text="Scale it!", command=self.scale, font=font_styles["simple"]) \
            .grid(row=5, column=2, sticky=tk.NW)

        # Rotation
        tk.Label(operation_frame, text="Rotation angle(in degrees): ", font=font_styles["bold"]) \
            .grid(row=6, column=0, sticky=tk.NW)
        self.rot_entry = tk.Entry(operation_frame)
        self.rot_entry.insert(0, ROT_ANGLE)
        self.rot_entry.grid(row=6, column=1)
        tk.Button(operation_frame, text="Rotate it!", command=self.rotate, font=font_styles["simple"]) \
            .grid(row=6, column=2, sticky=tk.NW)

        operation_frame.grid(row=1, column=1, columnspan=6, rowspan=7, sticky=tk.NW)

        # Customization frame
        customization_frame = tk.Frame(master)
        customization_frame.grid_rowconfigure(0, minsize=10)
        tk.Label(customization_frame, text="Customization: ", font=font_styles["heading"], foreground="red") \
            .grid(row=0, column=0, sticky=tk.NW, pady=1, columnspan=3)
        #
        tk.Label(customization_frame, text="Change color of canvas: ", font=font_styles["bold"]) \
            .grid(row=1, column=0, sticky=tk.NW)
        # R
        tk.Label(customization_frame, text="R: ", font=font_styles["bold"]) \
            .grid(row=2, column=0, sticky=tk.NW)
        canvas_r_entry = tk.Entry(customization_frame)
        canvas_r_entry.insert(0, 0)
        self.color_entries[CANVAS].append(canvas_r_entry)
        canvas_r_entry.grid(row=2, column=1)
        # G
        tk.Label(customization_frame, text="G: ", font=font_styles["bold"]) \
            .grid(row=2, column=2, sticky=tk.NW)
        canvas_g_entry = tk.Entry(customization_frame)
        canvas_g_entry.insert(0, 0)
        self.color_entries[CANVAS].append(canvas_g_entry)
        canvas_g_entry.grid(row=2, column=3)
        # B
        tk.Label(customization_frame, text="B: ", font=font_styles["bold"]) \
            .grid(row=2, column=4, sticky=tk.NW)
        canvas_b_entry = tk.Entry(customization_frame)
        canvas_b_entry.insert(0, 0)
        self.color_entries[CANVAS].append(canvas_b_entry)
        canvas_b_entry.grid(row=2, column=5)
        tk.Button(customization_frame, text="Change color of it!", command=lambda: self.change_color(CANVAS),
                  font=font_styles["simple"]) \
            .grid(row=2, column=6, sticky=tk.NW)

        tk.Label(customization_frame, text="Change color of lines: ", font=font_styles["bold"]) \
            .grid(row=3, column=0, sticky=tk.NW, padx=2)
        # R
        tk.Label(customization_frame, text="R: ", font=font_styles["bold"]) \
            .grid(row=4, column=0, sticky=tk.NW)
        line_r_entry = tk.Entry(customization_frame)
        line_r_entry.insert(0, self.colors[LINE][0])
        self.color_entries[LINE].append(line_r_entry)
        line_r_entry.grid(row=4, column=1)
        # G
        tk.Label(customization_frame, text="G: ", font=font_styles["bold"]) \
            .grid(row=4, column=2, sticky=tk.NW)
        line_g_entry = tk.Entry(customization_frame)
        line_g_entry.insert(0, 0)
        self.color_entries[LINE].append(line_g_entry)
        line_g_entry.grid(row=4, column=3)
        # B
        tk.Label(customization_frame, text="B: ", font=font_styles["bold"]) \
            .grid(row=4, column=4, sticky=tk.NW)
        line_b_entry = tk.Entry(customization_frame)
        line_b_entry.insert(0, 0)
        self.color_entries[LINE].append(line_b_entry)
        line_b_entry.grid(row=4, column=5)

        tk.Button(customization_frame, text="Change color of it!", command=lambda: self.change_color(LINE),
                  font=font_styles["simple"]) \
            .grid(row=4, column=6, sticky=tk.NW)

        tk.Label(customization_frame, text="Change color of pivot: ", font=font_styles["bold"]) \
            .grid(row=5, column=0, sticky=tk.NW, padx=2)
        # R
        tk.Label(customization_frame, text="R: ", font=font_styles["bold"]) \
            .grid(row=6, column=0, sticky=tk.NW)
        pivot_r_entry = tk.Entry(customization_frame)
        pivot_r_entry.insert(0, 0)
        self.color_entries[PIVOT].append(pivot_r_entry)
        pivot_r_entry.grid(row=6, column=1)
        # G
        tk.Label(customization_frame, text="G: ", font=font_styles["bold"]) \
            .grid(row=6, column=2, sticky=tk.NW)
        pivot_g_entry = tk.Entry(customization_frame)
        pivot_g_entry.insert(0, 0)
        self.color_entries[PIVOT].append(pivot_g_entry)
        pivot_g_entry.grid(row=6, column=3)
        # B
        tk.Label(customization_frame, text="B: ", font=font_styles["bold"]) \
            .grid(row=6, column=4, sticky=tk.NW)
        pivot_b_entry = tk.Entry(customization_frame)
        pivot_b_entry.insert(0, self.colors[PIVOT][2])
        self.color_entries[PIVOT].append(pivot_b_entry)
        pivot_b_entry.grid(row=6, column=5)
        tk.Button(customization_frame, text="Change color of it!", command=lambda: self.change_color(PIVOT),
                  font=font_styles["simple"]) \
            .grid(row=6, column=6, sticky=tk.NW, padx=2)

        customization_frame.grid(row=2, column=1, columnspan=7, rowspan=7, sticky=tk.NW)

        # Object frame
        object_frame = tk.Frame(master)

        tk.Label(object_frame, text="Object creation: ", font=font_styles["heading"], foreground="red") \
            .grid(row=0, column=0, sticky=tk.W, pady=1, columnspan=3)

        tk.Button(object_frame,
                  text="Create a rectangle",
                  command=lambda: self.create_object(Rectangle),
                  font=font_styles["simple"]) \
            .grid(row=1, column=0, sticky=tk.NW, padx=3, pady=2)

        tk.Button(object_frame,
                  text="Create a rectangle",
                  command=lambda: self.create_object(Rectangle),
                  font=font_styles["simple"]) \
            .grid(row=1, column=1, sticky=tk.NW, padx=3, pady=2)

        tk.Button(object_frame,
                  text="Create a rectangle",
                  command=lambda: self.create_object(Rectangle),
                  font=font_styles["simple"]) \
            .grid(row=1, column=2, sticky=tk.NW, padx=3, pady=2)

        object_frame.grid(row=3, column=1, columnspan=6, rowspan=6, sticky=tk.NW)

        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<B1-Motion>", self._on_mouse_motion)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.update()

    @staticmethod
    def over9000(value, minlimit, maxlimit, entry):
        if value < minlimit or value > maxlimit:
            entry.delete(0, 'end')
            entry.insert(0, "over9000")
            return True
        return False

    def delete_current_object(self):
        del self.objs[self.current_object.id]
        objs = list(self.objs.values())
        if len(objs) > 0:
            self.current_object = objs[0]
        else:
            self.current_object = None

        self.update()

    def _on_mouse_down(self, e):
        if self.is_object_creation[0]:
            self.start_x = e.x
            self.start_y = e.y

        for o in self.objs.values():
            if o.is_inside(e.y, e.x):
                self.current_object = o

    def _on_mouse_motion(self, e):
        if self.is_object_creation[0]:
            cls = self.is_object_creation[1]
            self.last_created = cls.create_object((self.start_y, self.start_x), (e.y, e.x), self, self.canvas)
            self.update()

    def _on_mouse_release(self, e):
        if self.is_object_creation[0]:
            if self.current_object is not None:
                self.current_object.choose_pivot(self.canvas, MP)
                self.update()
            self.current_object = self.last_created
            self.objs[self.last_created.id] = self.last_created
            self.last_created = None
            self.is_object_creation = (False, None)
            self.current_object.choose_pivot(self.canvas, MP)
            self.update()

    def create_object(self, cls: Type[Object]):
        self.is_object_creation = (True, cls)

    def check_show_coords(self):
        self.show_coords = self.needs_text_coords.get()
        self.update()

    def change_color(self, key):
        r = int(self.color_entries[key][0].get())
        g = int(self.color_entries[key][1].get())
        b = int(self.color_entries[key][2].get())
        is_r = self.over9000(r, 0, 255, self.color_entries[key][0])
        is_g = self.over9000(g, 0, 255, self.color_entries[key][1])
        is_b = self.over9000(b, 0, 255, self.color_entries[key][2])
        over = is_r or is_g or is_b
        if not over:
            if key == LINE:
                self.current_object.color = (r, g, b)
            else:
                self.colors[key] = (r, g, b)
            self.update()

    def change_pivot_type(self, type):
        self.current_object.choose_pivot(self.canvas, type)
        self.update()

    def rotate(self):
        # messagebox.showerror("Error", "Incorrect button")
        angle = int(self.rot_entry.get())
        self.angle += angle
        self.angle %= 360
        self.current_object.rotate(np.deg2rad(self.angle), point=self.current_object.center_point)
        self.current_object.recalculate_pivots()
        self.update()

    def scale(self):
        scale_factor = float(self.scale_entry.get())
        self.current_object.scale(scale_factor, scale_factor)
        self.update()

    def move(self):
        # TODO: Validation
        x = int(self.move_entry_x.get())
        y = int(self.move_entry_y.get())
        over = False
        if x < 0 or x > self.w:
            self.move_entry_x.delete(0, 'end')
            self.move_entry_x.insert(0, "over9000")
            over = True
        elif y < 0 or y > self.h:
            self.move_entry_y.delete(0, 'end')
            self.move_entry_y.insert(0, "over9000")
            over = True
        if not over:
            self.current_object.move(y, x)
            self.update()

    def notify(self):
        self.update()

    def update(self):
        if self.current_object is not None:
            self.object_name_label_var.set(self.current_object.name)

            midx, midy = self.current_object.center_point
            self.mid_label_var.set("({}, {})".format(midy, midx))

            self.angle_label_var.set("{} degrees".format(int(self.current_object.angle)))
        # It is needed to clear canvas items, so that no memory leak would appear
        self.canvas.delete(self.image)

        self.canvas_arr = np.zeros((self.h, self.w, 3), dtype=np.uint8)
        self.canvas_arr[:] = self.colors[CANVAS]

        for o in self.objs.values():
            o.draw(self.canvas_arr)

        # self.current_object.flood_fill(self.current_object.center_point[0],
        #                                self.current_object.center_point[1],
        #                                self.canvas_arr,
        #                                (0, 0, 0),
        #                                (0, 255, 0),
        #                                (255, 0, 0))

        if self.last_created is not None:
            self.last_created.draw(self.canvas_arr, self.colors[LINE])

        self.img = ImageTk.PhotoImage(Image.fromarray(self.canvas_arr.astype(np.uint8)))

        self.image = self.canvas.create_image(0, 0, anchor='nw', image=self.img)

        for o in self.objs.values():
            for p in o.pivots:
                p.draw(self.colors[PIVOT])

        if self.show_coords:
            for t in self.text_coords:
                self.canvas.delete(t)

            for p in self.current_object.points:
                self.text_coords.append(
                    self.canvas.create_text(p[1] + 10, p[0] - 10,
                                            text="({}, {})".format(p[1], p[0]), font="Times 11", fill="red"))

        # print(self.canvas.find_all(), "length: ", len(self.canvas.find_all()))
