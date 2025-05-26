from OpenGL.GL import *
import glfw

angle_x = 0.0
angle_y = 0.0
mode = True


def key_callback(window, key, scancode, action, mods):
    global angle_x, angle_y, mode
    if action == glfw.PRESS or action == glfw.REPEAT:
        if key == glfw.KEY_UP:
            angle_x += 5.0
        elif key == glfw.KEY_DOWN:
            angle_x -= 5.0
        elif key == glfw.KEY_LEFT:
            angle_y += 5.0
        elif key == glfw.KEY_RIGHT:
            angle_y -= 5.0
        elif key == glfw.KEY_SPACE:
            mode = not mode


perspective_matrix = [
    0.87, -0.09, 0.98, 0.49,
    0.0, 0.98, 0.35, 0.17,
    0.5, 0.15, -1.7, -0.85,
    0.0, 0.0, 1.0, 2.0
]


def draw_cube(s):
    glPolygonMode(GL_FRONT_AND_BACK, GL_LINE if not mode else GL_FILL)
    glBegin(GL_QUADS)

    glColor3f(1, 0, 1)
    glVertex3f(0.1 + s, 0.1 + s, 0.1 + s)
    glVertex3f(-0.1 - s, 0.1 + s, 0.1 + s)
    glVertex3f(-0.1 - s, -0.1 - s, 0.1 + s)
    glVertex3f(0.1 + s, -0.1 - s, 0.1 + s)
    glColor3f(1, 0, 0)
    glVertex3f(0.1 + s, 0.1 + s, -0.1 - s)
    glVertex3f(-0.1 - s, 0.1 + s, -0.1 - s)
    glVertex3f(-0.1 - s, -0.1 - s, -0.1 - s)
    glVertex3f(0.1 + s, -0.1 - s, -0.1 - s)
    glColor3f(0, 1, 0)
    glVertex3f(0.1 + s, 0.1 + s, 0.1 + s)
    glVertex3f(0.1 + s, 0.1 + s, -0.1 - s)
    glVertex3f(0.1 + s, -0.1 - s, -0.1 - s)
    glVertex3f(0.1 + s, -0.1 - s, 0.1 + s)
    glColor3f(0, 0, 1)
    glVertex3f(-0.1 - s, 0.1 + s, 0.1 + s)
    glVertex3f(-0.1 - s, 0.1 + s, -0.1 - s)
    glVertex3f(-0.1 - s, -0.1 - s, -0.1 - s)
    glVertex3f(-0.1 - s, -0.1 - s, 0.1 + s)
    glColor3f(1, 1, 0)
    glVertex3f(0.1 + s, 0.1 + s, -0.1 - s)
    glVertex3f(-0.1 - s, 0.1 + s, -0.1 - s)
    glVertex3f(-0.1 - s, 0.1 + s, 0.1 + s)
    glVertex3f(0.1 + s, 0.1 + s, 0.1 + s)
    glColor3f(0, 1, 1)
    glVertex3f(0.1 + s, -0.1 - s, -0.1 - s)
    glVertex3f(-0.1 - s, -0.1 - s, -0.1 - s)
    glVertex3f(-0.1 - s, -0.1 - s, 0.1 + s)
    glVertex3f(0.1 + s, -0.1 - s, 0.1 + s)
    glEnd()


def render():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    glMultMatrixf(perspective_matrix)
    glPushMatrix()
    glRotatef(angle_x, 1, 0, 0)
    glRotatef(angle_y, 0, 1, 0)
    draw_cube(0.3)
    glPopMatrix()

    glPushMatrix()
    glTranslatef(0.7, 0.7, 0.7)
    draw_cube(0)
    glPopMatrix()


def main():
    if not glfw.init():
        return

    window = glfw.create_window(800, 800, "Lab 2", None, None)
    glfw.make_context_current(window)
    glfw.set_key_callback(window, key_callback)

    glEnable(GL_DEPTH_TEST)
    glClearColor(1.0, 1.0, 1.0, 1.0)

    while not glfw.window_should_close(window):
        glfw.poll_events()
        render()
        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()