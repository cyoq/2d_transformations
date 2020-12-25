
class Line:

    @staticmethod
    def draw(canvas, x_start, y_start, x_end, y_end):
        dx = abs(x_end - x_start)
        dy = abs(y_end - y_start)

        xs = 1 if x_start < x_end else -1
        ys = 1 if y_start < y_end else -1

        x = x_start
        y = y_start

        if dx > dy:
            pn = 2 * dy - dx
            while x != x_end:
                if pn > 0:
                    x += xs
                    y += ys
                    pn = pn + 2 * dy - 2 * dx
                else:
                    x += xs
                    pn = pn + 2 * dy
                # place for drawing
                canvas[x, y, :] = (255, 0, 0)
        else:
            pn = 2 * dx - dy
            while y != y_end:
                if pn > 0:
                    x += xs
                    y += ys
                    pn = pn + 2 * dx - 2 * dy
                else:
                    y += ys
                    pn = pn + 2 * dx
                # place for drawing
                canvas[x, y, :] = (255, 0, 0)
