import tkinter as tk

from gui import Program


def main():
    root = tk.Tk()

    my_gui = Program(root, (600, 600))

    root.update()
    root.mainloop()


if __name__ == '__main__':
    main()
