import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import math

lat_count = 30
long_count = 40

a, b, c = 1, 0.6, 0.6


def init_window(width=800, height=600, title="lab3"):
    if not glfw.init():
        return None

    window = glfw.create_window(width, height, title, None, None)
    if not window:
        glfw.terminate()
        return None

    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)
    glEnable(GL_DEPTH_TEST)
    resize_viewport(width, height)

    return window

def key_callback(window, key, scancode, action, mods):
    global lat_count, long_count
    if action in (glfw.PRESS, glfw.REPEAT):
        if key == glfw.KEY_UP:
            lat_count += 5
            long_count += 5
        elif key == glfw.KEY_DOWN and lat_count > 5 and long_count > 5:
            lat_count -= 5
            long_count -= 5



def resize_viewport(width, height):
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 10)
    glMatrixMode(GL_MODELVIEW)


def draw_ellipsoid(lat_steps, long_steps):
    for i in range(lat_steps):
        theta1 = math.pi * i / lat_steps
        theta2 = math.pi * (i + 1) / lat_steps

        glBegin(GL_LINE_STRIP)
        for j in range(long_steps + 1):
            phi = 2 * math.pi * j / long_steps

            x1 = a * math.sin(theta1) * math.cos(phi)
            y1 = b * math.sin(theta1) * math.sin(phi)
            z1 = c * math.cos(theta1)
            glVertex3f(x1, y1, z1)

            x2 = a * math.sin(theta2) * math.cos(phi)
            y2 = b * math.sin(theta2) * math.sin(phi)
            z2 = c * math.cos(theta2)
            glVertex3f(x2, y2, z2)
        glEnd()



def main():
    window = init_window()
    if not window:
        return

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        glTranslatef(0, 0, -2.5)
        glRotatef(30, 1, 0, 0)

        draw_ellipsoid(lat_count, long_count)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()