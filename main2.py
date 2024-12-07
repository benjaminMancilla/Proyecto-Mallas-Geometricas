import numpy as np
from scipy.spatial import Delaunay
import pyvista as pv
from noise import pnoise2
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import random
import time

# Configuracion de la semilla global para reproducibilidad
seed = int(time.time())
random.seed(seed)

# Generar desplazamientos aleatorios entre 0 y 10,000
offset_x = random.randint(0, 10000)
offset_y = random.randint(0, 10000)
print(f"Offsets generados: offset_x={offset_x}, offset_y={offset_y}")

# Crear un mapa de colores personalizado
"""""
terrain_cmap = LinearSegmentedColormap.from_list(
    "terrain_neon",
    [
        (0.0, "purple"),   # Tonos bajos
        (0.2, "blue"),     # Transicion a azul
        (0.4, "cyan"),     # Transicion a cian
        (0.6, "lime"),     # Transicion a verde neon
        (0.8, "yellow"),   # Transicion a amarillo brillante
        (1.0, "magenta"),  # Tonos altos
    ],
)
"""""

# Crear un mapa de colores personalizado
#"""
terrain_cmap = LinearSegmentedColormap.from_list(
    "terrain_custom",
    [
        (0.0, "blue"),   # Valores muy bajos (negativos y cercanos a 0)
        (0.2, "blue"),  # Valores bajos, transicion a azul claro
        (0.4, "green"),  # Valores neutros, transicion a verde
        (0.75, "gray"),  # Valores altos intermedios
        (1.0, "white"),  # Valores muy altos
    ],
)
#"""

# Fractal Brownian Noise Function: crea una mesh de octavas por 
# cada especificada y las suma (interpolacion)
# Ademas se modifica la amplitud y la frecuencia de cada octava
# de acuerdo a la persistencia y la lacunarity (gap)
def fbm(x, y, octaves, persistence, lacunarity):
    total = 0
    frequency = 1
    amplitude = 1
    max_value = 0 
    for i in range(octaves):
        total += pnoise2(x * frequency + offset_x,
                         y * frequency + offset_y,
                         repeatx=1024, repeaty=1024) * amplitude
        max_value += amplitude
        amplitude *= persistence
        frequency *= lacunarity

    return total / max_value

def mountain_terrain(x, y, octaves, persistence, lacunarity):
    return 2 * fbm(x*6, y*3, octaves, persistence, lacunarity)

def plains_terrain(x, y, octaves, persistence, lacunarity):
    return ((fbm(x, y, octaves, persistence, lacunarity))**(0.25)) - 0.6

def simple_curve(x, y):
    """
    Define un peso basado en la distancia radial al origen.
    La planicie se encuentra cerca del centro (distancia baja).
    """
    val = (x**2 + y**2)**0.5  # Distancia radial al origen
    start = 0.3  # Radio interno de la planicie
    end = 0.7    # Radio externo donde empiezan las montañas
    if val < start:
        return 1  # Planicie completa
    elif val > end:
        return 0  # Montañas completas
    return (end - val) / (end - start)  # Transicion suave

def combined_terrain(x, y, octaves, persistence, lacunarity):
    m = mountain_terrain(x, y, octaves, persistence, lacunarity)
    p = plains_terrain(x, y, octaves, persistence, lacunarity)
    w = simple_curve(x, y)
    return (1-w)*m + w*p

def combined_noise(x, y, octaves, persistence, lacunarity):
    # Parametros para el movimiento browniano fractal

    return fbm(x, y, octaves, persistence, lacunarity)

def toggle_widgets(value):  # Recibe el estado del boton
    if value:  # Mostrar sliders y barra
        create_sliders(plotter, update_mesh)  # Agregar sliders nuevamente
        plotter.remove_scalar_bar()  # Asegurarse de que no haya duplicados
        # Volver a asignar la barra de colores al actor
        plotter.add_scalar_bar(
            color="white",  # Texto blanco
            title_font_size=12,  # Tamaño del titulo
            label_font_size=10,  # Tamaño de las etiquetas
            outline=False,  # Quitar borde de la barra de colores
        )
    else:  # Ocultar sliders y barra
        plotter.clear_slider_widgets()
        plotter.remove_scalar_bar()  # Asegurarse de eliminar la barra de color

# Generar malla base
n = 200
x = np.linspace(-1, 1, n)
y = np.linspace(-1, 1, n)
xx, yy = np.meshgrid(x, y)
points = np.c_[xx.ravel(), yy.ravel()]
tri = Delaunay(points)
faces_pyvista = np.hstack([[3] + list(face) for face in tri.simplices])

# Limites para la altura z
z_min_target = -0.05  # Profundidad maxima (mar)
z_max_target = 0.2   # Altura maxima (montañas)

# Crear una funcion para generar elcombined_noise terreno
def generate_terrain(octaves, persistence, lacunarity):
    z = np.array([combined_terrain(p[0], p[1], octaves, persistence, lacunarity) for p in points])

    # Calcular los valores minimo y maximo originales de z
    z_min_original = np.min(z)
    z_max_original = np.max(z)
    
    # Normalizar z entre 0 y 1
    z_normalized = (z - z_min_original) / (z_max_original - z_min_original)
    
    # Escalar z al rango deseado
    z_scaled = z_min_target + z_normalized * (z_max_target - z_min_target)
    z_scaled = z_scaled 
    
    points_3d = np.c_[points, z_scaled]
    mesh = pv.PolyData(points_3d, faces_pyvista)
    mesh["height"] = z_scaled  # Asignar alturas como escalares
    return mesh

# Crear un renderizador interactivo
plotter = pv.Plotter()
plotter.show_axes()

# Configuracion inicial de los parametros
octaves = 4
persistence = 0.4
lacunarity = 3
mesh = generate_terrain(octaves, persistence, lacunarity)

plotter.add_checkbox_button_widget(toggle_widgets, value=False, size=30)

def create_sliders(plotter, update_callback):
    # Slider para Octaves
    plotter.add_slider_widget(
        callback=lambda value: update_callback(value, "octaves"),
        rng=[1, 12],  # Rango de octavas
        value=4,      # Valor inicial
        title="Octaves",
        pointa=(0.02, 0.9),  # Posicion inicial
        pointb=(0.12, 0.9),   # Posicion final
        slider_width=0.01,   # Ancho del slider
        tube_width=0.005,    # Ancho del tubo
        title_height=0.02,   # Tamaño del titulo
        title_opacity=0.2,   # Opacidad del texto
        color="white",       # Color del fondo
        title_color="white", # Color del texto
    )

    # Slider para Persistence
    plotter.add_slider_widget(
        callback=lambda value: update_callback(value, "persistence"),
        rng=[0.3, 0.7],  # Rango de persistence
        value=0.4,       # Valor inicial
        title="Persistence",
        pointa=(0.14, 0.9),  # Posicion inicial
        pointb=(0.24, 0.9),   # Posicion final
        slider_width=0.01,   # Ancho del slider
        tube_width=0.005,    # Ancho del tubo
        title_height=0.02,   # Tamaño del titulo
        title_opacity=0.2,   # Opacidad del texto
        color="white",       # Color del fondo
        title_color="white", # Color del texto
    )

    # Slider para Lacunarity
    plotter.add_slider_widget(
        callback=lambda value: update_callback(value, "lacunarity"),
        rng=[1.5, 3.5],  # Rango de lacunarity
        value=3.0,       # Valor inicial
        title="Lacunarity",
        pointa=(0.26, 0.9),  # Posicion inicial
        pointb=(0.36, 0.9),   # Posicion final
        slider_width=0.01,   # Ancho del slider
        tube_width=0.005,    # Ancho del tubo
        title_height=0.02,   # Tamaño del titulo
        title_opacity=0.2,   # Opacidad del texto
        color="white",       # Color del fondo
        title_color="white", # Color del texto
    )



# Configurar el actor inicial sin barra automatica
actor = plotter.add_mesh(
    mesh,
    scalars="height",  # Escala basada en la altura
    cmap=terrain_cmap,  # Usar el mapa de colores personalizado
    show_edges=False,
    smooth_shading=True,
    show_scalar_bar=False,  # Deshabilitar barra de color automatica
)

# Agregar una barra de colores personalizada
plotter.add_scalar_bar(
    color="black",  # Texto blanco
    title_font_size=12,  # Tamaño del titulo
    label_font_size=10,  # Tamaño de las etiquetas
    outline=False,  # Quitar borde de la barra de colores
)

# Funcion de actualizacion dinamica
def update_mesh(value, parameter):
    global octaves, persistence, lacunarity
    # Actualizar el parametro correspondiente
    if parameter == "octaves":
        octaves = int(value)
    elif parameter == "persistence":
        persistence = value
    elif parameter == "lacunarity":
        lacunarity = value
    # Regenerar la malla
    new_mesh = generate_terrain(octaves, persistence, lacunarity)
    actor.mapper.SetInputData(new_mesh)  # Actualizar el mapper del actor
    plotter.remove_scalar_bar()  # Eliminar la barra existente
    plotter.add_scalar_bar(
        color="white",  # Texto blanco
        title_font_size=12,
        label_font_size=10,
        outline=False,
    )
    plotter.render()  # Renderizar la escena actualizada

# Crear los sliders y vincular la funcion de actualizacion
create_sliders(plotter, update_mesh)

# Configurar la visualizacion
plotter.view_isometric()
plotter.set_background("skyblue")  # Fondo negro
#plotter.set_background("black")
plotter.show()






