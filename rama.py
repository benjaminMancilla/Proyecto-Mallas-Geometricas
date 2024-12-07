import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import turtle 
import random

f_1 = np.array([[0.0, 0.0], [0.0, 0.16]])
f_2 = np.array([[0.85, 0.04], [-0.04, 0.85]])
fs_2 = np.array([[0.0], [1.6]])
f_3 = np.array([[0.2, -0.26], [0.23, 0.22]])
fs_3 = np.array([[0.0], [1.6]])
f_4 = np.array([[-0.15, 0.28], [0.26, 0.24]])
fs_4 = np.array([[0.0], [0.44]])

#f_1 = np.array([[0.0, 0.0], [0.0, 0.25]])
#f_2 = np.array([[0.75, 0.2], [-0.2, 0.75]])
#fs_2 = np.array([[0.1], [1.5]])
#f_3 = np.array([[0.4, -0.4], [0.4, 0.4]])
#fs_3 = np.array([[-0.2], [1.3]])
#f_4 = np.array([[-0.1, 0.4], [0.4, 0.1]])
#fs_4 = np.array([[0.2], [0.6]])

def barnsley_fern(n):
    x, y = 0,0
    points = []
    for i in range(n):
        f = random.random()
        if f < 0.01:
            new_p = np.dot(f_1, np.array([x, y]))
        elif f < 0.86:
            new_p = np.dot(f_2, np.array([x, y])) + fs_2.flatten()
        elif f < 0.93:
            new_p = np.dot(f_3, np.array([x, y])) + fs_3.flatten()
        else:
            new_p = np.dot(f_4, np.array([x, y])) + fs_4.flatten()
        
        points.append(new_p)
        x, y = new_p[0], new_p[1]

    return np.array(points)

def plot_fern(n):
    result = barnsley_fern(n)
    x = result[:,0]
    y = result[:,1]
    plt.scatter(x, y, s=1, c='g')
    plt.show()

def draw_fern(n):
    result = barnsley_fern(n)
    print(result.shape)
    pen = turtle.Turtle()
    pen.speed(0)
    pen.hideturtle()
    pen.color('green')
    pen.penup()
    for i in range(n):
        x = result[i][0]
        y = result[i][1]
        pen.goto(x*50, y*50-200)
        pen.dot()

    turtle.done()

def plot_fern_vertical(n, scale_x=0.5, scale_y=1.5):
    result = barnsley_fern(n)
    x = result[:, 0] * scale_x  # Ajustar el ancho
    y = result[:, 1] * scale_y  # Ajustar la altura
    plt.scatter(x, y, s=1, c='g')
    plt.gca().set_aspect('equal', adjustable='datalim')  # Asegurar proporciones consistentes
    plt.title("Barnsley Fern (Ajustado)")
    plt.xlabel("X (ajustado)")
    plt.ylabel("Y (ajustado)")
    plt.show()

if __name__ == '__main__':
    #draw_fern(1000)
    plot_fern_vertical(100000, scale_x=2.4, scale_y=1.5)
