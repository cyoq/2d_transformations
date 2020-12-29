import tkinter as tk

from program import Program


def main():
    root = tk.Tk()

    my_gui = Program(root, (800, 800))
    root.update()
    root.mainloop()


if __name__ == '__main__':
    main()


