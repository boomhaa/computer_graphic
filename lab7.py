import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
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
rotate_cube = False

fps_update_interval = 0.5
fps_last_update = time.time()
fps_frame_count = 0
current_fps = 0

perf_data = {
    "original": [],
    "optimized": []
}
perf_start_time = 0
measuring_performance = False
current_mode = "original"

cube_dl = None
floor_dl = None
cube_vao = None
cube_vbo = None


def init_performance_measurement():
    global perf_data, measuring_performance, perf_start_time, current_mode
    perf_data = {"original": [], "optimized": []}
    measuring_performance = True
    perf_start_time = time.time()
    current_mode = "original"
    print("Starting performance measurement...")


def save_performance_data():
    global perf_data
    print("\nPerformance results:")
    print("+----------------+-----------+-----------+")
    print("| Frame          | Original  | Optimized |")
    print("+----------------+-----------+-----------+")

    max_frames = max(len(perf_data["original"]), len(perf_data["optimized"]))
    original_avg = sum(perf_data["original"]) / len(perf_data["original"]) if perf_data["original"] else 0
    optimized_avg = sum(perf_data["optimized"]) / len(perf_data["optimized"]) if perf_data["optimized"] else 0

    for i in range(max_frames):
        orig = perf_data["original"][i] if i < len(perf_data["original"]) else "-"
        opt = perf_data["optimized"][i] if i < len(perf_data["optimized"]) else "-"

        orig_str = f"{orig:8.2f}" if isinstance(orig, (int, float)) else f"{orig:>8}"
        opt_str = f"{opt:8.2f}" if isinstance(opt, (int, float)) else f"{opt:>8}"

        print(f"| Frame {i + 1:8} | {orig_str} | {opt_str} |")

    print("+----------------+-----------+-----------+")
    print(f"| Average FPS    | {original_avg:8.2f} | {optimized_avg:8.2f} |")
    print("+----------------+-----------+-----------+\n")

    improvement = ((optimized_avg - original_avg) / original_avg * 100) if original_avg != 0 else 0
    print(f"Performance improvement: {improvement:.2f}%")

def draw_fps_text(fps):
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

    if light_enabled:
        glDisable(GL_LIGHTING)
    if use_texture:
        glDisable(GL_TEXTURE_2D)
    glDisable(GL_DEPTH_TEST)

    # Background
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex2f(10, height - 40)
    glVertex2f(110, height - 40)
    glVertex2f(110, height - 10)
    glVertex2f(10, height - 10)
    glEnd()

    # Text
    glColor3f(1.0, 1.0, 1.0)
    fps_text = f"FPS: {fps} ({current_mode})"

    glRasterPos2f(20, height - 30)
    for char in fps_text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_12, ord(char))

    glEnable(GL_DEPTH_TEST)
    if use_texture:
        glEnable(GL_TEXTURE_2D)
    if light_enabled:
        glEnable(GL_LIGHTING)

    glMatrixMode(GL_MODELVIEW)
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()


def update_fps():
    global fps_frame_count, fps_last_update, current_fps, measuring_performance, perf_data, current_mode
    global perf_start_time
    fps_frame_count += 1
    current_time = time.time()
    time_diff = current_time - fps_last_update

    if time_diff >= fps_update_interval:
        current_fps = int(fps_frame_count / time_diff)
        fps_frame_count = 0
        fps_last_update = current_time

        if measuring_performance:
            perf_data[current_mode].append(current_fps)

            if current_time - perf_start_time > 5 and current_mode == "original":
                current_mode = "optimized"
                perf_start_time = current_time
            elif current_time - perf_start_time > 5 and current_mode == "optimized":
                measuring_performance = False
                save_performance_data()


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
        print(f"Texture loading error: {e}")
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

    mat_specular = [1.0, 1.0, 1.0, 1.0]
    mat_shininess = [50.0]

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

    # Optimized: Adjust attenuation for better performance
    glLightf(GL_LIGHT0, GL_CONSTANT_ATTENUATION, 0.5)
    glLightf(GL_LIGHT0, GL_LINEAR_ATTENUATION, 0.05)
    glLightf(GL_LIGHT0, GL_QUADRATIC_ATTENUATION, 0.01)


def create_cube_display_list():
    dl = glGenLists(1)
    glNewList(dl, GL_COMPILE)

    glEnable(GL_LIGHTING)
    glColor3f(0.3, 0.3, 0.3)


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

    texcoords = [(0, 0), (1, 0), (1, 1), (0, 1)]

    glBegin(GL_QUADS)
    for face in range(6):
        glNormal3fv(normals[face])
        for i in range(4):
            glTexCoord2fv(texcoords[i])
            glVertex3fv(vertices[face * 4 + i])
    glEnd()

    glEndList()
    return dl


def create_floor_display_list():
    dl = glGenLists(1)
    glNewList(dl, GL_COMPILE)

    glEnable(GL_LIGHTING)
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

    glEndList()
    return dl


def init_vertex_array_object():
    global cube_vao, cube_vbo

    vertices = np.array([
        [-0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 0.0],
        [0.5, -0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 1.0, 1.0],
        [-0.5, 0.5, 0.5, 0.0, 0.0, 1.0, 0.0, 1.0],

        [-0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 0.0],
        [-0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 1.0, 0.0],
        [0.5, 0.5, -0.5, 0.0, 0.0, -1.0, 1.0, 1.0],
        [0.5, -0.5, -0.5, 0.0, 0.0, -1.0, 0.0, 1.0],

        [-0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 0.0],
        [-0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 1.0, 0.0],
        [0.5, 0.5, 0.5, 0.0, 1.0, 0.0, 1.0, 1.0],
        [0.5, 0.5, -0.5, 0.0, 1.0, 0.0, 0.0, 1.0],

        [-0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 0.0, 0.0],
        [0.5, -0.5, -0.5, 0.0, -1.0, 0.0, 1.0, 0.0],
        [0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 1.0, 1.0],
        [-0.5, -0.5, 0.5, 0.0, -1.0, 0.0, 0.0, 1.0],

        [0.5, -0.5, -0.5, 1.0, 0.0, 0.0, 0.0, 0.0],
        [0.5, 0.5, -0.5, 1.0, 0.0, 0.0, 1.0, 0.0],
        [0.5, 0.5, 0.5, 1.0, 0.0, 0.0, 1.0, 1.0],
        [0.5, -0.5, 0.5, 1.0, 0.0, 0.0, 0.0, 1.0],

        [-0.5, -0.5, -0.5, -1.0, 0.0, 0.0, 0.0, 0.0],
        [-0.5, -0.5, 0.5, -1.0, 0.0, 0.0, 1.0, 0.0],
        [-0.5, 0.5, 0.5, -1.0, 0.0, 0.0, 1.0, 1.0],
        [-0.5, 0.5, -0.5, -1.0, 0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float32)

    cube_vao = glGenVertexArrays(1)
    glBindVertexArray(cube_vao)

    cube_vbo = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, cube_vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    stride = 8 * 4

    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))

    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * 4))

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)


def draw_cube_original(rotation_angle):
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

    texcoords = [(0, 0), (1, 0), (1, 1), (0, 1)]

    glBegin(GL_QUADS)
    for face in range(6):
        glNormal3fv(normals[face])
        for i in range(4):
            glTexCoord2fv(texcoords[i])
            glVertex3fv(vertices[face * 4 + i])
    glEnd()


def draw_cube_optimized(rotation_angle):
    if light_enabled:
        glEnable(GL_LIGHTING)
    else:
        glDisable(GL_LIGHTING)
        glColor3f(0.8, 0.8, 0.8)

    glBindVertexArray(cube_vao)
    glDrawArrays(GL_QUADS, 0, 24)
    glBindVertexArray(0)


def draw_floor_original():
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


def draw_floor_optimized():
    glCallList(floor_dl)


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
        y_vel = -y_vel


def key_callback(window, key, scancode, action, mods):
    global use_texture, light_enabled, rotate_cube, y_pos, y_vel
    global camera_distance, camera_angle_x, camera_angle_y, measuring_performance

    if action == glfw.PRESS:
        if key == glfw.KEY_T:
            use_texture = not use_texture
            print(f"Texturing {'enabled' if use_texture else 'disabled'}")
        elif key == glfw.KEY_L:
            light_enabled = not light_enabled
            if light_enabled:
                glEnable(GL_LIGHTING)
                print("Lighting enabled")
            else:
                glDisable(GL_LIGHTING)
                print("Lighting disabled")
        elif key == glfw.KEY_MINUS:
            camera_distance += 0.5
            print(f"Camera distance: {camera_distance}")
        elif key == glfw.KEY_EQUAL:
            camera_distance = max(1.0, camera_distance - 0.5)
            print(f"Camera distance: {camera_distance}")
        elif key == glfw.KEY_R:
            rotate_cube = not rotate_cube
            print(f"Rotation {'enabled' if rotate_cube else 'disabled'}")
        elif key == glfw.KEY_P:
            init_performance_measurement()
            print("Performance measurement started")


def main():
    global cube_dl, floor_dl, cube_vao, cube_vbo, current_mode

    if not glfw.init():
        print("Failed to initialize GLFW")
        return

    glutInit()
    window = glfw.create_window(width, height, "OpenGL Optimization Lab", None, None)
    if not window:
        print("Failed to create GLFW window")
        glfw.terminate()
        return

    glfw.make_context_current(window)
    glfw.swap_interval(0)
    glfw.set_key_callback(window, key_callback)

    glViewport(0, 0, width, height)
    glEnable(GL_DEPTH_TEST)

    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)

    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, width / height, 0.1, 100.0)

    texture_id = load_texture("./tex.bmp")
    init_lighting()

    cube_dl = create_cube_display_list()
    floor_dl = create_floor_display_list()
    init_vertex_array_object()

    rotation_angle = 0.0

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        if light_enabled:
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
        else:
            glDisable(GL_LIGHTING)

        if use_texture:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture_id)
        else:
            glDisable(GL_TEXTURE_2D)

        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        x = camera_distance * math.sin(math.radians(camera_angle_y)) * math.cos(math.radians(camera_angle_x))
        y = camera_distance * math.sin(math.radians(camera_angle_x))
        z = camera_distance * math.cos(math.radians(camera_angle_y)) * math.cos(math.radians(camera_angle_x))
        gluLookAt(x, y, z, 0, 0, 0, 0, 1, 0)

        update_position()
        update_fps()

        if current_mode == "optimized":
            draw_floor_optimized()
        else:
            draw_floor_original()

        glPushMatrix()
        glTranslatef(0.0, y_pos, 0.0)
        if rotate_cube:
            rotation_angle += 1.0
            glRotatef(rotation_angle, 1, 1, 1)

        if current_mode == "optimized":
            draw_cube_optimized(rotation_angle)
        else:
            draw_cube_original(rotation_angle)
        glPopMatrix()

        draw_fps_text(current_fps)

        glfw.swap_buffers(window)
        glfw.poll_events()


    glDeleteLists(cube_dl, 1)
    glDeleteLists(floor_dl, 1)
    glDeleteVertexArrays(1, [cube_vao])
    glDeleteBuffers(1, [cube_vbo])
    glfw.terminate()


if __name__ == "__main__":
    main()