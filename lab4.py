import glfw
from OpenGL.GL import *
import numpy as np
import sys

window_width, window_height = 800, 600
frame_buffer = np.ones((window_height, window_width, 3), dtype=np.float32)
polygon_points = []
is_drawing = False


def bresenham_line(x0, y0, x1, y1):

    points = []
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    x, y = x0, y0
    sx = -1 if x0 > x1 else 1
    sy = -1 if y0 > y1 else 1

    if dx > dy:
        err = dx / 2.0
        while x != x1:
            points.append((x, y))
            err -= dy
            if err < 0:
                y += sy
                err += dx
            x += sx
    else:
        err = dy / 2.0
        while y != y1:
            points.append((x, y))
            err -= dx
            if err < 0:
                x += sx
                err += dy
            y += sy

    points.append((x, y))
    return points


def rasterize_polygon(points):

    if len(points) < 3:
        return

    edges = []
    for i in range(len(points)):
        x0, y0 = map(int, points[i])
        x1, y1 = map(int, points[(i + 1) % len(points)])
        if y0 == y1:
            continue
        if y0 > y1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        edges.append((x0, y0, x1, y1))

    if not edges:
        return

    min_y = min(e[1] for e in edges)
    max_y = max(e[3] for e in edges)
    aet = []

    for y in range(min_y, max_y + 1):
        for edge in edges:
            x0, y0, x1, y1 = edge
            if y0 == y:
                dx = x1 - x0
                dy = y1 - y0
                inv_m = dx / dy if dy != 0 else 0
                aet.append((y1, x0, inv_m))

        aet.sort(key=lambda e: e[1])

        for i in range(0, len(aet), 2):
            if i + 1 >= len(aet):
                break
            x_start = int(round(aet[i][1]))
            x_end = int(round(aet[i + 1][1]))
            x_start = max(0, min(x_start, window_width - 1))
            x_end = max(0, min(x_end, window_width - 1))
            if x_start <= x_end:
                frame_buffer[y, x_start:x_end + 1] = [0.0, 1.0, 0.0]

        aet = [e for e in aet if e[0] > y]
        for i in range(len(aet)):
            y_max, x, inv_m = aet[i]
            aet[i] = (y_max, x + inv_m, inv_m)


def apply_weighted_average_filter(buffer):

    height, width, _ = buffer.shape
    filtered_buffer = np.copy(buffer)


    weights = np.array([[1, 2],
                        [2, 4]], dtype=np.float32)
    weights /= np.sum(weights)

    for y in range(height - 1):
        for x in range(width - 1):

            region = buffer[y:y + 2, x:x + 2]

            for c in range(3):
                filtered_buffer[y, x, c] = np.sum(region[:, :, c] * weights)

    return filtered_buffer


def update_frame_buffer():
    glDrawPixels(window_width, window_height, GL_RGB, GL_FLOAT, frame_buffer)


def clear_frame_buffer():
    global frame_buffer, polygon_points
    frame_buffer = np.ones((window_height, window_width, 3), dtype=np.float32)
    polygon_points = []


def window_resize_callback(window, width, height):
    global window_width, window_height, frame_buffer
    window_width, window_height = width, height
    glViewport(0, 0, width, height)
    frame_buffer = np.ones((height, width, 3), dtype=np.float32)


def mouse_button_callback(window, button, action, mods):
    global polygon_points, is_drawing

    if button == glfw.MOUSE_BUTTON_LEFT and action == glfw.PRESS:
        x, y = glfw.get_cursor_pos(window)
        y = window_height - y

        if not is_drawing:
            clear_frame_buffer()
            polygon_points = [(x, y)]
            is_drawing = True
        else:
            polygon_points.append((x, y))


def key_callback(window, key, scancode, action, mods):
    global frame_buffer, polygon_points, is_drawing

    if action == glfw.PRESS:
        if key == glfw.KEY_C:
            clear_frame_buffer()
            is_drawing = False
        elif key == glfw.KEY_F:
            frame_buffer = apply_weighted_average_filter(frame_buffer)
        elif key == glfw.KEY_ENTER:
            if len(polygon_points) >= 3:
                polygon_points.append(polygon_points[0])
                rasterize_polygon(polygon_points)
                is_drawing = False
        elif key == glfw.KEY_ESCAPE:
            glfw.set_window_should_close(window, True)


def main():
    if not glfw.init():
        sys.exit(1)

    window = glfw.create_window(window_width, window_height, "lab4", None, None)
    if not window:
        glfw.terminate()
        sys.exit(2)

    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, window_resize_callback)
    glfw.set_mouse_button_callback(window, mouse_button_callback)
    glfw.set_key_callback(window, key_callback)

    glClearColor(1.0, 1.0, 1.0, 1.0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glOrtho(0, window_width, 0, window_height, -1, 1)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT)

        if polygon_points:
            for x, y in polygon_points:
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        px, py = int(x) + dx, int(y) + dy
                        if 0 <= px < window_width and 0 <= py < window_height:
                            frame_buffer[py, px] = [1.0, 0.0, 0.0]

            for i in range(len(polygon_points) - 1):
                x0, y0 = polygon_points[i]
                x1, y1 = polygon_points[i + 1]
                for x, y in bresenham_line(int(x0), int(y0), int(x1), int(y1)):
                    if 0 <= x < window_width and 0 <= y < window_height:
                        frame_buffer[y, x] = [1.0, 0.0, 0.0]

        update_frame_buffer()
        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()