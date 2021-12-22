from math import sqrt


def distance(u, v):
    return sqrt((u[0] - v[0]) ** 2 + (u[1] - v[1]) ** 2)
