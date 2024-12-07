import pyglet
from OpenGL import GL
import numpy as np
from fractals import *

# Funciones de transformación
def translate(tx, ty, tz):
    return np.array(
        [[1, 0, 0, tx], [0, 1, 0, ty], [0, 0, 1, tz], [0, 0, 0, 1]], dtype=np.float32
    )

def uniformScale(s):
    return np.array(
        [[s, 0, 0, 0], [0, s, 0, 0], [0, 0, s, 0], [0, 0, 0, 1]], dtype=np.float32
    )

def rotate_x(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array(
        [[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], dtype=np.float32
    )

def rotate_y(angle):
    c, s = np.cos(angle), np.sin(angle)
    return np.array(
        [[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], dtype=np.float32
    )

# Controlador para manejar interactividad
class Controller:
    zoom = 1.0
    x, y, z = 0.0, 0.0, 0.0
    level = 0  # Nivel actual del fractal
    rotation_x = 0.0  # Rotación en eje X
    rotation_y = 0.0  # Rotación en eje Y
    dragging = False  # Estado del clic izquierdo + CTRL


controller = Controller()

# Crear ventana de Pyglet
win = pyglet.window.Window(800, 800, "Tetrahedron Fractal", resizable=False)

# Inicializar vértices e índices del fractal
vertices, indices = generate_sierpinsky3D(n=controller.level)
vertices = vertices.flatten()

# Configurar shaders
vertex_shader_code = """
#version 330
in vec3 position;
uniform mat4 scale;
uniform mat4 translate;
uniform mat4 rotate;
void main() {
    gl_Position = translate * scale * rotate * vec4(position, 1.0);
}
"""

fragment_shader_code = """
#version 330
out vec4 FragColor;
void main() {
    FragColor = vec4(1.0, 1.0, 1.0, 1.0);
}
"""

vertex_shader = pyglet.graphics.shader.Shader(vertex_shader_code, "vertex")
fragment_shader = pyglet.graphics.shader.Shader(fragment_shader_code, "fragment")
shader_program = pyglet.graphics.shader.ShaderProgram(vertex_shader, fragment_shader)

# Crear una lista inicializada para cargar datos en GPU
gpu_data = shader_program.vertex_list_indexed(
    len(vertices) // 3, GL.GL_TRIANGLES, indices.flatten().astype(np.uint32)
)
gpu_data.position[:] = vertices

@win.event
def on_draw():
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
    win.clear()

    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)

    shader_program.use()
    shader_program["scale"] = uniformScale(controller.zoom).reshape(16, 1, order="F")
    shader_program["translate"] = translate(controller.x, controller.y, controller.z).reshape(16, 1, order="F")
    rotation_matrix = rotate_x(controller.rotation_x) @ rotate_y(controller.rotation_y)
    shader_program["rotate"] = rotation_matrix.reshape(16, 1, order="F")

    gpu_data.draw(GL.GL_TRIANGLES)

@win.event
def on_key_press(symbol, modifiers):
    global vertices, indices, gpu_data

    if symbol == pyglet.window.key.UP:
        controller.zoom = min(controller.zoom * 1.1, 10.0)  # Límite superior en zoom
    elif symbol == pyglet.window.key.DOWN:
        controller.zoom = max(controller.zoom / 1.1, 0.1)  # Límite inferior en zoom
    elif symbol == pyglet.window.key.W:
        controller.y += 0.1
    elif symbol == pyglet.window.key.S:
        controller.y -= 0.1
    elif symbol == pyglet.window.key.A:
        controller.x -= 0.1
    elif symbol == pyglet.window.key.D:
        controller.x += 0.1
    elif symbol == pyglet.window.key.RIGHT:
        controller.level += 1
        vertices, indices = generate_sierpinsky3D(n=controller.level)
        vertices = vertices.flatten()
        gpu_data = shader_program.vertex_list_indexed(
            len(vertices) // 3, GL.GL_TRIANGLES, indices.flatten().astype(np.uint32)
        )
        gpu_data.position[:] = vertices
    elif symbol == pyglet.window.key.LEFT:
        if controller.level > 0:
            controller.level -= 1
            vertices, indices = generate_sierpinsky3D(n=controller.level)
            vertices = vertices.flatten()
            gpu_data = shader_program.vertex_list_indexed(
                len(vertices) // 3, GL.GL_TRIANGLES, indices.flatten().astype(np.uint32)
            )
            gpu_data.position[:] = vertices


@win.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    if buttons & pyglet.window.mouse.LEFT and modifiers & pyglet.window.key.MOD_CTRL:
        controller.dragging = True
        controller.rotation_y += dx * 0.01  # Ajustar sensibilidad del movimiento
        controller.rotation_x += dy * 0.01

@win.event
def on_mouse_release(x, y, button, modifiers):
    if button == pyglet.window.mouse.LEFT:
        controller.dragging = False

pyglet.app.run()