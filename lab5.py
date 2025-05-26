import glfw
from OpenGL.GL import *
from OpenGL.GLU import *


INSIDE = 0
LEFT, RIGHT, BOTTOM, TOP, NEAR, FAR = 1, 2, 4, 8, 16, 32


xmin, xmax = -1, 1
ymin, ymax = -1, 1
zmin, zmax = -1, 1


angle_x, angle_y = 0, 0


def compute_outcode(x, y, z):
    code = INSIDE
    if x < xmin:
        code |= LEFT
    elif x > xmax:
        code |= RIGHT
    if y < ymin:
        code |= BOTTOM
    elif y > ymax:
        code |= TOP
    if z < zmin:
        code |= NEAR
    elif z > zmax:
        code |= FAR
    return code


def cohen_sutherland_clip_external(p1, p2):
    x0, y0, z0 = p1
    x1, y1, z1 = p2
    outcode0 = compute_outcode(x0, y0, z0)
    outcode1 = compute_outcode(x1, y1, z1)


    if outcode0 == 0 and outcode1 == 0:
        return []

    if (outcode0 & outcode1) != 0:
        return [(p1, p2)]

    result_segments = []


    if outcode0 == 0 and outcode1 != 0:
        intersection = find_boundary_intersection(p1, p2)
        if intersection:
            result_segments.append((intersection, p2))
    elif outcode0 != 0 and outcode1 == 0:
        intersection = find_boundary_intersection(p2, p1)
        if intersection:
            result_segments.append((p1, intersection))
    else:
        temp_p1, temp_p2 = list(p1), list(p2)
        accept = False
        done = False

        while not done:
            outcode0 = compute_outcode(temp_p1[0], temp_p1[1], temp_p1[2])
            outcode1 = compute_outcode(temp_p2[0], temp_p2[1], temp_p2[2])

            if (outcode0 & outcode1) != 0:
                done = True
            elif outcode0 == 0 and outcode1 == 0:
                accept = True
                done = True
            else:
                outcode_out = outcode1 if outcode1 > outcode0 else outcode0


                if outcode_out & LEFT:
                    x = xmin
                    y = temp_p1[1] + (temp_p2[1] - temp_p1[1]) * (xmin - temp_p1[0]) / (temp_p2[0] - temp_p1[0])
                    z = temp_p1[2] + (temp_p2[2] - temp_p1[2]) * (xmin - temp_p1[0]) / (temp_p2[0] - temp_p1[0])
                elif outcode_out & RIGHT:
                    x = xmax
                    y = temp_p1[1] + (temp_p2[1] - temp_p1[1]) * (xmax - temp_p1[0]) / (temp_p2[0] - temp_p1[0])
                    z = temp_p1[2] + (temp_p2[2] - temp_p1[2]) * (xmax - temp_p1[0]) / (temp_p2[0] - temp_p1[0])
                elif outcode_out & BOTTOM:
                    y = ymin
                    x = temp_p1[0] + (temp_p2[0] - temp_p1[0]) * (ymin - temp_p1[1]) / (temp_p2[1] - temp_p1[1])
                    z = temp_p1[2] + (temp_p2[2] - temp_p1[2]) * (ymin - temp_p1[1]) / (temp_p2[1] - temp_p1[1])
                elif outcode_out & TOP:
                    y = ymax
                    x = temp_p1[0] + (temp_p2[0] - temp_p1[0]) * (ymax - temp_p1[1]) / (temp_p2[1] - temp_p1[1])
                    z = temp_p1[2] + (temp_p2[2] - temp_p1[2]) * (ymax - temp_p1[1]) / (temp_p2[1] - temp_p1[1])
                elif outcode_out & NEAR:
                    z = zmin
                    x = temp_p1[0] + (temp_p2[0] - temp_p1[0]) * (zmin - temp_p1[2]) / (temp_p2[2] - temp_p1[2])
                    y = temp_p1[1] + (temp_p2[1] - temp_p1[1]) * (zmin - temp_p1[2]) / (temp_p2[2] - temp_p1[2])
                elif outcode_out & FAR:
                    z = zmax
                    x = temp_p1[0] + (temp_p2[0] - temp_p1[0]) * (zmax - temp_p1[2]) / (temp_p2[2] - temp_p1[2])
                    y = temp_p1[1] + (temp_p2[1] - temp_p1[1]) * (zmax - temp_p1[2]) / (temp_p2[2] - temp_p1[2])


                if outcode_out == outcode0:
                    boundary_point = temp_p1.copy()
                    temp_p1 = [x, y, z]
                    intersection_point = (x, y, z)
                    result_segments.append((tuple(boundary_point), intersection_point))
                else:
                    boundary_point = temp_p2.copy()
                    temp_p2 = [x, y, z]
                    intersection_point = (x, y, z)
                    result_segments.append((intersection_point, tuple(boundary_point)))

    return result_segments


def find_boundary_intersection(p_in, p_out):

    x0, y0, z0 = p_in
    x1, y1, z1 = p_out
    out = compute_outcode(x1, y1, z1)


    if x1 - x0 != 0:
        t_left = (xmin - x0) / (x1 - x0)
        t_right = (xmax - x0) / (x1 - x0)
    else:
        t_left = t_right = -1

    if y1 - y0 != 0:
        t_bottom = (ymin - y0) / (y1 - y0)
        t_top = (ymax - y0) / (y1 - y0)
    else:
        t_bottom = t_top = -1

    if z1 - z0 != 0:
        t_near = (zmin - z0) / (z1 - z0)
        t_far = (zmax - z0) / (z1 - z0)
    else:
        t_near = t_far = -1

    t_max = -1
    if out & LEFT and t_left >= 0 and t_left <= 1:
        t_max = t_left
    elif out & RIGHT and t_right >= 0 and t_right <= 1:
        t_max = t_right
    elif out & BOTTOM and t_bottom >= 0 and t_bottom <= 1:
        t_max = t_bottom
    elif out & TOP and t_top >= 0 and t_top <= 1:
        t_max = t_top
    elif out & NEAR and t_near >= 0 and t_near <= 1:
        t_max = t_near
    elif out & FAR and t_far >= 0 and t_far <= 1:
        t_max = t_far

    if t_max >= 0:
        x = x0 + t_max * (x1 - x0)
        y = y0 + t_max * (y1 - y0)
        z = z0 + t_max * (z1 - z0)
        return (x, y, z)
    return None

def draw_segment(p1, p2, color=(1, 1, 1)):
    glColor3f(*color)
    glBegin(GL_LINES)
    glVertex3f(*p1)
    glVertex3f(*p2)
    glEnd()


def draw_box():
    glColor3f(1, 1, 1)
    glBegin(GL_LINES)
    corners = [
        (xmin, ymin, zmin), (xmax, ymin, zmin),
        (xmax, ymax, zmin), (xmin, ymax, zmin),
        (xmin, ymin, zmax), (xmax, ymin, zmax),
        (xmax, ymax, zmax), (xmin, ymax, zmax),
    ]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    for i, j in edges:
        glVertex3f(*corners[i])
        glVertex3f(*corners[j])
    glEnd()


def input_segments():
    n = int(input("Введите количество отрезков: "))
    segments = []
    for i in range(n):
        print(f"\nОтрезок {i + 1}:")
        p1 = tuple(map(float, input("Точка 1: ").split()))
        p2 = tuple(map(float, input("Точка 2: ").split()))
        segments.append((p1, p2))
    return segments


def key_callback(window, key, scancode, action, mods):
    global angle_x, angle_y
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_LEFT:
            angle_y -= 5
        elif key == glfw.KEY_RIGHT:
            angle_y += 5
        elif key == glfw.KEY_UP:
            angle_x -= 5
        elif key == glfw.KEY_DOWN:
            angle_x += 5


def main():
    global angle_x, angle_y

    if not glfw.init():
        return

    window = glfw.create_window(800, 600, "lab5", None, None)
    if not window:
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 800 / 600, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)

    segments = input_segments()
    external_segments = []

    for p1, p2 in segments:
        clipped = cohen_sutherland_clip_external(p1, p2)
        external_segments.extend(clipped)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5.0)
        glRotatef(angle_x, 1, 0, 0)
        glRotatef(angle_y, 0, 1, 0)

        draw_box()

        for p1, p2 in external_segments:
            draw_segment(p1, p2, color=(1, 0, 0))

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
