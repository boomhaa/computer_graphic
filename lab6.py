import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *  # Add GLUT import
import numpy as np
from PIL import Image
import time
import math

width, height = 800, 600

y_pos = 2.0
y_vel = 0.0
accel = -9.81
last_time = time.time()

camera_distance = 5.0
camera_angle_x = 30.0
camera_angle_y = 45.0

use_texture = True
light_enabled = True
rotate_cube = True

fps_update_interval = 0.5
fps_last_update = time.time()
fps_frame_count = 0
current_fps = 0


def draw_fps_text(fps):
    """Рисуем текстовый FPS счетчик используя GLUT"""
    # Save matrices
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    # Disable effects that would interfere
    if light_enabled:
        glDisable(GL_LIGHTING)
    if use_texture:
        glDisable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)

    # Draw gray background
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex2f(10, height - 40)
    glVertex2f(110, height - 40)
    glVertex2f(110, height - 10)
    glVertex2f(10, height - 10)
    glEnd()

    # Draw FPS text using GLUT
    glColor3f(1.0, 1.0, 1.0)  # White color
    fps_text = f"FPS: {fps}"

    glRasterPos2f(20, height - 30)
    for char in fps_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))

    # Restore states
    glEnable(GL_DEPTH_TEST)
    if use_texture:
        glEnable(GL_TEXTURE_2D)
    if light_enabled:
        glEnable(GL_LIGHTING)

    # Restore matrices
    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()


def update_fps():
    """Calculate and update the FPS counter"""
    global fps_frame_count, fps_last_update, current_fps

    # Increment frame counter
    fps_frame_count += 1

    # Check if it's time to update the displayed FPS
    current_time = time.time()
    time_diff = current_time - fps_last_update

    # Update FPS approximately every fps_update_interval seconds
    if time_diff >= fps_update_interval:
        current_fps = int(fps_frame_count / time_diff)
        fps_frame_count = 0
        fps_last_update = current_time


def load_texture(path):
    try:
        img = Image.open(path)
        img_data = np.array(list(img.convert("RGB").getdata()), np.uint8)

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR_MIPMAP_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        return tex_id
    except Exception as e:
        print(f"Ошибка загрузки текстуры: {e}")
        texture_data = np.zeros((64, 64, 3), dtype=np.uint8)
        for i in range(64):
            for j in range(64):
                c = 255 if (i // 8 + j // 8) % 2 == 0 else 0
                texture_data[i, j] = [c, c, c]

        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, 64, 64, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        return tex_id


def init_lighting():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_NORMALIZE)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT, GL_AMBIENT_AND_DIFFUSE)

    mat_ambient = [0.2, 0.2, 0.2, 1.0]
    mat_diffuse = [0.8, 0.8, 0.8, 1.0]
    mat_specular = [1.0, 1.0, 1.0, 1.0]
    mat_shininess = [50.0]

    glMaterialfv(GL_FRONT, GL_AMBIENT, mat_ambient)
    glMaterialfv(GL_FRONT, GL_DIFFUSE, mat_diffuse)
    glMaterialfv(GL_FRONT, GL_SPECULAR, mat_specular)
    glMaterialfv(GL_FRONT, GL_SHININESS, mat_shininess)

    light_ambient = [0.2, 0.2, 0.2, 1.0]
    light_diffuse = [0.7, 0.7, 0.7, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    light_position = [3.0, 5.0, 5.0, 1.0]
    spot_direction = [-0.6, -1.0, -1.0]

    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightf(GL_LIGHT0, GL_SPOT_CUTOFF, 30.0)
    glLightfv(GL_LIGHT0, GL_SPOT_DIRECTION, spot_direction)
    glLightf(GL_LIGHT0, GL_SPOT_EXPONENT, 15.0)

    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.5)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.01)


def draw_cube(rotation_angle=0.0):
    vertices = [
        (-0.5, -0.5, 0.5), (0.5, -0.5, 0.5), (0.5, 0.5, 0.5), (-0.5, 0.5, 0.5),
        (-0.5, -0.5, -0.5), (-0.5, 0.5, -0.5), (0.5, 0.5, -0.5), (0.5, -0.5, -0.5),
        (-0.5, 0.5, -0.5), (-0.5, 0.5, 0.5), (0.5, 0.5, 0.5), (0.5, 0.5, -0.5),
        (-0.5, -0.5, -0.5), (0.5, -0.5, -0.5), (0.5, -0.5, 0.5), (-0.5, -0.5, 0.5),
        (0.5, -0.5, -0.5), (0.5, 0.5, -0.5), (0.5, 0.5, 0.5), (0.5, -0.5, 0.5),
        (-0.5, -0.5, -0.5), (-0.5, -0.5, 0.5), (-0.5, 0.5, 0.5), (-0.5, 0.5, -0.5)
    ]

    normals = [
        (0, 0, 1), (0, 0, -1),
        (0, 1, 0), (0, -1, 0),
        (1, 0, 0), (-1, 0, 0)
    ]

    colors = [
        (1.0, 0.0, 0.0), (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0), (1.0, 1.0, 0.0),
        (1.0, 0.0, 1.0), (0.0, 1.0, 1.0)
    ]

    texcoords = [
        (0, 0), (1, 0), (1, 1), (0, 1)
    ]
    glBegin(GL_QUADS)
    for face in range(6):
        glNormal3fv(normals[face])
        if not use_texture:
            glColor3fv(colors[face])
        else:
            glColor3f(1.0, 1.0, 1.0)

        for i in range(4):
            if use_texture:
                glTexCoord2fv(texcoords[i])
            glVertex3fv(vertices[face * 4 + i])
    glEnd()


def draw_floor():
    glDisable(GL_LIGHTING)
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(-5.0, -1.0, -5.0)
    glVertex3f(5.0, -1.0, -5.0)
    glVertex3f(5.0, -1.0, 5.0)
    glVertex3f(-5.0, -1.0, 5.0)
    glEnd()

    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_LINES)
    for i in range(-5, 6):
        glVertex3f(i, -0.99, -5.0)
        glVertex3f(i, -0.99, 5.0)
        glVertex3f(-5.0, -0.99, i)
        glVertex3f(5.0, -0.99, i)
    glEnd()

    if light_enabled:
        glEnable(GL_LIGHTING)


def update_position():
    global y_pos, y_vel, last_time
    current_time = time.time()
    dt = current_time - last_time
    last_time = current_time

    dt = min(dt, 0.1)

    y_vel += accel * dt
    y_pos += y_vel * dt

    if y_pos <= -0.5:
        y_pos = -0.5
        y_vel = -y_vel * 1.001


def key_callback(window, key, scancode, action, mods):
    global use_texture, light_enabled, rotate_cube, y_pos, y_vel
    global camera_distance, camera_angle_x, camera_angle_y

    if action == glfw.PRESS:
        if key == glfw.KEY_T:
            use_texture = not use_texture
            print(f"Текстурирование {'включено' if use_texture else 'выключено'}")
        elif key == glfw.KEY_L:
            light_enabled = not light_enabled
            if light_enabled:
                glEnable(GL_LIGHTING)
                print("Освещение включено")
            else:
                glDisable(GL_LIGHTING)
                print("Освещение выключено")
        elif key == glfw.KEY_MINUS or key == glfw.KEY_KP_SUBTRACT:
            camera_distance += 0.5
            print(f"Камера отдалена: {camera_distance}")
        elif key == glfw.KEY_EQUAL or key == glfw.KEY_KP_ADD:
            camera_distance = max(1.0, camera_distance - 0.5)
            print(f"Камера приближена: {camera_distance}")
        elif key == glfw.KEY_R:
            rotate_cube = not rotate_cube
            print(f"Вращение {'включено' if rotate_cube else 'выключено'}")


def main():
    global texture_id
    rotation_angle = 0.0

    if not glfw.init():
        print("Не удалось инициализировать GLFW")
        return

    glutInit()
    window = glfw.create_window(width, height, "lab6", None, None)
    if not window:
        print("Не удалось создать окно GLFW")
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.swap_interval(0)
    glfw.set_key_callback(window, key_callback)

    glViewport(0, 0, width, height)
    glEnable(GL_DEPTH_TEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 100.0)

    texture_id = load_texture("./tex.bmp")
    init_lighting()

    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        x = camera_distance * math.sin(math.radians(camera_angle_y)) * math.cos(math.radians(camera_angle_x))
        y = camera_distance * math.sin(math.radians(camera_angle_x))
        z = camera_distance * math.cos(math.radians(camera_angle_y)) * math.cos(math.radians(camera_angle_x))

        gluLookAt(x, y, z, 0, 0, 0, 0, 1, 0)

        update_position()
        update_fps()

        draw_floor()

        if use_texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture_id)
        else:
            glDisable(GL_TEXTURE_2D)

        glPushMatrix()
        glTranslatef(0.0, y_pos, 0.0)
        draw_cube(rotation_angle)
        glPopMatrix()

        # Update rotation angle
        if rotate_cube:
            rotation_angle += 1.0

        draw_fps_text(current_fps)

        glfw.swap_buffers(window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()