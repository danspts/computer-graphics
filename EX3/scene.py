from typing import List
import numpy as np

import matplotlib.pyplot as plt

from utils import normalize, reflected
from objects import Object3D
from lights import LightSource, PointLight
from constants import EPSILON
from helper_classes import *


EPSILON = 1e-4


def render_scene(camera, ambient, lights, objects, screen_size, max_depth):
    width, height = screen_size
    ratio = float(width) / height
    screen = (-1, 1 / ratio, 1, -1 / ratio)  # left, top, right, bottom

    image = np.zeros((height, width, 3))

    for i, y in enumerate(np.linspace(screen[1], screen[3], height)):
        for j, x in enumerate(np.linspace(screen[0], screen[2], width)):
            pixel = np.array([x, y, 0])
            color = np.zeros(3)

            # This is the main loop where each pixel color is computed.
            ray = Ray(camera, normalize(pixel - camera))
            for _ in range(max_depth):
                traced = trace_ray(ray, objects, lights)
                if not traced:
                    break
                obj, M, N, col_ray = traced
                ray = Ray( M + N * EPSILON, reflected(ray.direction, N))
                col += reflection * col_ray
                reflection *= obj.reflection
            # We clip the values between 0 and 1 so all pixel values will make sense.
            image[i, j] = np.clip(color,0,1)

    return image

def trace_ray(ray: Ray, objects : List[Object3D], lights: List[LightSource], camera, ambient):
    # Find first point of intersection with the scene.
    obj, t = ray.nearest_intersected_object(objects)
    # Return None if the ray does not intersect any object.
    if not obj: 
        return None
    P = ray.origin + t * ray.direction
    # Find properties of the object.
    n = obj.normal
    # v_camera = normalize(camera - P)
    for L in lights:
        if isinstance(L, PointLight):
            light_ray = L.get_light_ray(P)
        else:
            raise ValueError()
        shadow_intersect_obj, _ = light_ray.nearest_intersected_object(objects)
        if shadow_intersect_obj is not obj:
            continue

        # Start computing the color.
        col_ray = ambient
        # Lambert shading (diffuse).
        col_ray += obj.diffuse * n.dot(L.direction) * L.get_intensity(P)
        # # Blinn-Phong shading (specular).
        # col_ray += obj.specular * n.dot(normalize(v_L + v_camera)) ** obj.shininess * L.get_intensity(P)
    return obj, P, n, col_ray




# Write your own objects and lights
# TODO
def your_own_scene():
    camera = np.array([0,0,1])
    lights = []
    objects = []
    return camera, lights, objects


