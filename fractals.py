import numpy as np

def generate_sierpinsky3D(n=0):
    """
    Genera los vértices e índices de un fractal tetraédrico.
    :param n: Nivel de iteración del fractal.
    :return: (vértices, índices) del fractal generado.
    """
    # Define los vértices del tetraedro inicial
    v0 = np.array([0.0, 0.0, 0.0])  # Vértice inferior
    v1 = np.array([1.0, 0.0, 0.0])  # Vértice derecho
    v2 = np.array([0.5, np.sqrt(3) / 2, 0.0])  # Vértice izquierdo
    v3 = np.array([0.5, np.sqrt(3) / 6, np.sqrt(2) / np.sqrt(3)])  # Vértice superior

    base_tetrahedron = [v0, v1, v2, v3]

    # Función recursiva para subdividir el tetraedro
    def subdivide(vertices, level):
        if level == 0:
            return [vertices]
        
        # Calcula los puntos medios de las aristas
        mid01 = (vertices[0] + vertices[1]) / 2
        mid02 = (vertices[0] + vertices[2]) / 2
        mid03 = (vertices[0] + vertices[3]) / 2
        mid12 = (vertices[1] + vertices[2]) / 2
        mid13 = (vertices[1] + vertices[3]) / 2
        mid23 = (vertices[2] + vertices[3]) / 2

        # Subtetraedros (en las esquinas)
        t1 = [vertices[0], mid01, mid02, mid03]
        t2 = [mid01, vertices[1], mid12, mid13]
        t3 = [mid02, mid12, vertices[2], mid23]
        t4 = [mid03, mid13, mid23, vertices[3]]

        # Subdivide cada subtetraedro
        return (
            subdivide(t1, level - 1)
            + subdivide(t2, level - 1)
            + subdivide(t3, level - 1)
            + subdivide(t4, level - 1)
        )

    # Genera el fractal recursivamente
    tetrahedra = subdivide(base_tetrahedron, n)

    # Aplanar los datos de los vértices e índices
    vertices = []
    indices = []
    for i, tetra in enumerate(tetrahedra):
        start_index = len(vertices)
        vertices.extend(tetra)
        indices.extend(
            [
                [start_index, start_index + 1, start_index + 2],
                [start_index, start_index + 1, start_index + 3],
                [start_index, start_index + 2, start_index + 3],
                [start_index + 1, start_index + 2, start_index + 3],
            ]
        )

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

import numpy as np

import numpy as np

def generate_tetrahedron(n=0):
    """
    Genera un fractal tridimensional colocando tetraedros escalados dentro del original.
    :param n: Nivel de iteración del fractal.
    :return: (vértices, índices) del fractal generado.
    """
    # Define los vértices del tetraedro inicial
    v0 = np.array([0.0, 0.0, 0.0])  # Vértice inferior
    v1 = np.array([1.0, 0.0, 0.0])  # Vértice derecho
    v2 = np.array([0.5, np.sqrt(3) / 2, 0.0])  # Vértice izquierdo
    v3 = np.array([0.5, np.sqrt(3) / 6, np.sqrt(2) / np.sqrt(3)])  # Vértice superior

    base_tetrahedron = [v0, v1, v2, v3]

    # Función para escalar y trasladar un tetraedro
    def transform_tetrahedron(vertices, scale, translation):
        return [scale * vertex + translation for vertex in vertices]

    # Función recursiva para construir el fractal
    def subdivide(vertices, level):
        if level == 0:
            return [vertices]

        # Escalar el tetraedro por 1/2
        scale = 0.5

        # Centros de los nuevos tetraedros
        new_tetrahedra = [
            transform_tetrahedron(vertices, scale, vertices[0]),  # Escalar y mover a v0
            transform_tetrahedron(vertices, scale, vertices[1]),  # Escalar y mover a v1
            transform_tetrahedron(vertices, scale, vertices[2]),  # Escalar y mover a v2
            transform_tetrahedron(vertices, scale, vertices[3]),  # Escalar y mover a v3
        ]

        # Subdivide recursivamente
        result = []
        for tetra in new_tetrahedra:
            result.extend(subdivide(tetra, level - 1))
        return result

    # Generar el fractal
    tetrahedra = subdivide(base_tetrahedron, n)

    # Aplanar los datos de vértices e índices
    vertices = []
    indices = []
    for i, tetra in enumerate(tetrahedra):
        start_index = len(vertices)
        vertices.extend(tetra)
        indices.extend(
            [
                [start_index, start_index + 1, start_index + 2],
                [start_index, start_index + 1, start_index + 3],
                [start_index, start_index + 2, start_index + 3],
                [start_index + 1, start_index + 2, start_index + 3],
            ]
        )

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)
