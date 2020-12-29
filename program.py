import webbrowser
from typing import Type, List

from PIL import Image, ImageTk

from circle import Circle
from consts import ROT_ANGLE
from ellipse import Ellipse
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
CANVAS = "canvas_arr"
PIVOT = "pivot"
LINE = "line"


class Program(Observer):

    def __init__(self, master, dimensions: Tuple[int, int]):
        self.object_iter = 0
        self.master = master
        self.master.title("2D Transformations")

        self.text_coords: List[int] = []
        self.show_coords: bool = False
        self.angle: int = 0

        # second argument is an object pivot_type
        self.is_object_creation: Tuple[bool, Optional[Type[Object]]] = (False, None)
        self.start_x: int = 0
        self.start_y: int = 0
        self.last_created: Optional[Type[Object]] = None

        self.is_rotation_pivot_change: bool = False

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

        self.canvas_arr: np.ndarray = np.zeros((self.h, self.w, 3), dtype=np.uint8)

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

        # ellipse = Ellipse(self, self.canvas_arr, np.array([[400, 400, 1]]), 40, 100)
        # self.objs[ellipse.id] = ellipse

        circle = Circle(self, self.canvas, np.array([[500, 400, 1]]), 100)
        self.objs[circle.id] = circle

        self.img = ImageTk.PhotoImage(Image.fromarray(self.canvas_arr))

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

        tk.Button(info_frame, text="Next object >>", command=self.__next_object, font=font_styles["simple"]) \
            .grid(row=1, column=2, sticky=tk.NW, padx=2)

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

        tk.Button(info_frame, text="Delete current object", command=self.__delete_current_object,
                  font=font_styles["simple"]) \
            .grid(row=4, column=0, pady=2, sticky=tk.NW)

        self.needs_text_coords = tk.IntVar()
        self.needs_text_coords.set(0)
        self.checkbox = tk.Checkbutton(info_frame, text="Show coordinates?", font=font_styles["simple"],
                                       variable=self.needs_text_coords, command=self.__check_show_coords)
        self.checkbox.grid(row=5, column=0, sticky=tk.NW)

        info_frame.grid(row=0, column=1, columnspan=3, rowspan=6, sticky=tk.NW)

        # Operation Frame
        operation_frame = tk.Frame(master)
        tk.Label(operation_frame, text="Operations on the object:", font=font_styles["heading"], foreground="red") \
            .grid(row=0, column=0, sticky=tk.NW, pady=1, columnspan=3)

        tk.Label(operation_frame, text="Manipulation modes: ", font=font_styles["bold"]) \
            .grid(row=1, column=0, sticky=tk.NW)

        tk.Button(operation_frame, text="Transformation mode", command=lambda: self.__change_pivot_type(TP),
                  font=font_styles["simple"]) \
            .grid(row=2, column=0, sticky=tk.NW, pady=3, padx=3)
        tk.Button(operation_frame, text="Position mode", command=lambda: self.__change_pivot_type(MP),
                  font=font_styles["simple"]) \
            .grid(row=2, column=1, sticky=tk.NW, pady=3, padx=3)
        tk.Button(operation_frame, text="Rotation mode", command=lambda: self.__change_pivot_type(RP),
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

        tk.Button(operation_frame, text="Move it!", command=self.__move, font=font_styles["simple"]) \
            .grid(row=4, column=5, sticky=tk.N, padx=2, pady=2)

        # Scaling
        tk.Label(operation_frame, text="Scale factor: ", font=font_styles["bold"]) \
            .grid(row=5, column=0, sticky=tk.NW)

        tk.Label(operation_frame, text="X: ", font=font_styles["bold"]) \
            .grid(row=5, column=1, sticky=tk.NW)
        self.scale_entry_x = tk.Entry(operation_frame)
        self.scale_entry_x.insert(0, 1)
        self.scale_entry_x.grid(row=5, column=2)

        tk.Label(operation_frame, text="Y: ", font=font_styles["bold"]) \
            .grid(row=5, column=3, sticky=tk.NW)
        self.scale_entry_y = tk.Entry(operation_frame)
        self.scale_entry_y.insert(0, 1)
        self.scale_entry_y.grid(row=5, column=4)
        tk.Button(operation_frame, text="Scale it!", command=self.__scale, font=font_styles["simple"]) \
            .grid(row=5, column=5, sticky=tk.NW)

        # Rotation
        tk.Label(operation_frame, text="Rotation angle(in degrees): ", font=font_styles["bold"]) \
            .grid(row=6, column=0, sticky=tk.NW)
        self.rot_entry = tk.Entry(operation_frame)
        self.rot_entry.insert(0, ROT_ANGLE)
        self.rot_entry.grid(row=6, column=1)
        tk.Button(operation_frame, text="Rotate it!", command=self.__rotate, font=font_styles["simple"]) \
            .grid(row=6, column=2, sticky=tk.NW)

        operation_frame.grid(row=1, column=1, columnspan=6, rowspan=7, sticky=tk.NW)

        # Customization frame
        customization_frame = tk.Frame(master)
        customization_frame.grid_rowconfigure(0, minsize=10)
        tk.Label(customization_frame, text="Customization: ", font=font_styles["heading"], foreground="red") \
            .grid(row=0, column=0, sticky=tk.NW, pady=1, columnspan=3)
        #
        tk.Label(customization_frame, text="Change color of canvas_arr: ", font=font_styles["bold"]) \
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
        tk.Button(customization_frame, text="Change color of it!", command=lambda: self.__change_color(CANVAS),
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

        tk.Button(customization_frame, text="Change color of it!", command=lambda: self.__change_color(LINE),
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
        tk.Button(customization_frame, text="Change color of it!", command=lambda: self.__change_color(PIVOT),
                  font=font_styles["simple"]) \
            .grid(row=6, column=6, sticky=tk.NW, padx=2)

        customization_frame.grid(row=2, column=1, columnspan=7, rowspan=7, sticky=tk.NW)

        # Object frame
        object_frame = tk.Frame(master)

        tk.Label(object_frame, text="Object creation: ", font=font_styles["heading"], foreground="red") \
            .grid(row=0, column=0, sticky=tk.W, pady=1, columnspan=3)

        tk.Button(object_frame,
                  text="Create a rectangle",
                  command=lambda: self.__create_object(Rectangle),
                  font=font_styles["simple"]) \
            .grid(row=1, column=0, sticky=tk.NW, padx=3, pady=2)

        tk.Button(object_frame,
                  text="Create an ellipse",
                  command=lambda: self.__create_object(Ellipse),
                  font=font_styles["simple"]) \
            .grid(row=1, column=1, sticky=tk.NW, padx=3, pady=2)

        tk.Button(object_frame,
                  text="Create a circle",
                  command=lambda: self.__create_object(Circle),
                  font=font_styles["simple"]) \
            .grid(row=1, column=2, sticky=tk.NW, padx=3, pady=2)

        tk.Button(object_frame,
                  text="Change rotation pivot",
                  command=self.__change_rotation_pivot,
                  font=font_styles["simple"]) \
            .grid(row=2, column=0, sticky=tk.NW, padx=3, pady=2)

        tk.Button(object_frame,
                  text="Rotation pivot to object's center",
                  command=self.__rotation_pivot_to_center,
                  font=font_styles["simple"]) \
            .grid(row=2, column=1, sticky=tk.NW, padx=3, pady=2)

        object_frame.grid(row=3, column=1, columnspan=6, rowspan=6, sticky=tk.NW)

        tk.Label(master, text="Created by: ", font=font_styles["bold"]) \
            .grid(row=3, column=2, sticky=tk.S)

        github = tk.Label(master, text="cyoq", font=font_styles["simple"], fg="blue", cursor="hand2")
        github.grid(row=3, column=3, sticky=tk.S)
        github.bind("<Button-1>", lambda e: webbrowser.open_new("https://github.com/cyoq"))

        self.canvas.bind("<ButtonPress-1>", self.__on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.__on_mouse_motion)
        self.canvas.bind("<ButtonRelease-1>", self.__on_mouse_release)
        self.__update()

    @staticmethod
    def __over9000(value: int, minlimit: int, maxlimit: int, entry: tk.Entry) -> bool:
        if value < minlimit or value > maxlimit:
            entry.delete(0, 'end')
            entry.insert(0, "over9000")
            return True
        return False

    def __next_object(self):
        n = len(self.objs)
        if n > 1:
            self.object_iter %= n
            obj_list = list(self.objs.values())
            if obj_list[self.object_iter] is self.current_object:
                self.object_iter += 1
                self.object_iter %= n

            self.current_object = obj_list[self.object_iter]
            self.object_iter += 1
            self.__update()

    def __delete_current_object(self):
        if self.current_object is not None:
            del self.objs[self.current_object.id]
            objs = list(self.objs.values())
            if len(objs) > 0:
                self.current_object = objs[0]
            else:
                self.current_object = None

            self.__update()

    def __on_mouse_down(self, e):
        if self.is_object_creation[0]:
            self.start_x = e.x
            self.start_y = e.y

        for o in self.objs.values():
            if o.is_inside(e.y, e.x):
                self.current_object = o
                self.__update()
                break

        if self.is_rotation_pivot_change:
            new_rot_pivot = Pivot(self.canvas, e.x, e.y, lambda x, y: None, stationary=True)
            self.current_object.update_rotation_pivot(new_rot_pivot)

    def __on_mouse_motion(self, e):
        if self.is_object_creation[0]:
            cls = self.is_object_creation[1]
            self.last_created = cls.create_object((self.start_y, self.start_x), (e.y, e.x), self, self.canvas)
            self.__update()

    def __on_mouse_release(self, e):
        if self.is_object_creation[0]:
            if self.current_object is not None:
                self.current_object.choose_pivot(self.canvas, MP)
                self.__update()
            self.current_object = self.last_created
            self.objs[self.last_created.id] = self.last_created
            self.last_created = None
            self.is_object_creation = (False, None)
            self.current_object.choose_pivot(self.canvas, MP)
            self.__update()

        if self.is_rotation_pivot_change:
            self.is_rotation_pivot_change = False
            self.__update()

    def __change_rotation_pivot(self):
        self.is_rotation_pivot_change = True

    def __rotation_pivot_to_center(self):
        if self.current_object is not None:
            self.current_object.rotation_pivot_to_center()
            self.__update()

    def __create_object(self, cls: Type[Object]):
        self.is_object_creation = (True, cls)

    def __check_show_coords(self):
        self.show_coords = self.needs_text_coords.get()
        self.__update()

    def __change_color(self, key: str):
        r = int(self.color_entries[key][0].get())
        g = int(self.color_entries[key][1].get())
        b = int(self.color_entries[key][2].get())
        is_r = self.__over9000(r, 0, 255, self.color_entries[key][0])
        is_g = self.__over9000(g, 0, 255, self.color_entries[key][1])
        is_b = self.__over9000(b, 0, 255, self.color_entries[key][2])
        over = is_r or is_g or is_b
        if not over:
            if key == LINE:
                self.current_object.color = (r, g, b)
            else:
                self.colors[key] = (r, g, b)
            self.__update()

    def __change_pivot_type(self, pivot_type: str) -> None:
        self.current_object.choose_pivot(self.canvas, pivot_type)
        self.__update()

    def __rotate(self):
        angle = int(self.rot_entry.get())
        self.angle += angle
        self.angle %= 360
        self.current_object.rotate(np.deg2rad(self.angle), point=self.current_object.center_point)
        self.current_object.recalculate_pivots()
        self.__update()

    def __scale(self):
        x = float(self.scale_entry_x.get())
        y = float(self.scale_entry_y.get())
        self.current_object.scale(x, y)
        self.__update()

    def __move(self):
        # TODO: Validation
        x = int(self.move_entry_x.get())
        y = int(self.move_entry_y.get())
        is_x = self.__over9000(x, -self.w, self.w, self.move_entry_x)
        is_y = self.__over9000(y, -self.h, self.h, self.move_entry_y)
        over = is_x or is_y
        if not over:
            self.current_object.move(y, x)
            self.__update()

    def notify(self):
        self.__update()

    def __update(self):

        if self.current_object is not None:
            self.object_name_label_var.set(self.current_object.name)

            midx, midy = self.current_object.center_point
            self.mid_label_var.set("({}, {})".format(midy, midx))

            self.angle_label_var.set("{} degrees".format(int(self.current_object.angle)))
        else:
            self.object_name_label_var.set("-")
            self.mid_label_var.set("({}, {})".format("-", "-"))
            self.angle_label_var.set("{} degrees".format("-"))

        # It is needed to clear canvas_arr items, so that no memory leak would appear
        self.canvas.delete(self.image)

        self.canvas_arr = np.zeros((self.h, self.w, 3), dtype=np.uint8)
        self.canvas_arr[:] = self.colors[CANVAS]

        for o in self.objs.values():
            o.draw(self.canvas_arr)

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

            if self.current_object:
                for p in self.current_object.points:
                    self.text_coords.append(
                        self.canvas.create_text(p[1] + 10, p[0] - 10,
                                                text="({}, {})".format(p[1], p[0]), font="Times 11", fill="red"))

        # print(self.canvas_arr.find_all(), "length: ", len(self.canvas_arr.find_all()))
