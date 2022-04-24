from typing import List

import matplotlib.pyplot as plt

from helper_classes import *


def render_scene(camera, ambient, lights, objects, screen_size, max_depth):
    width, height = screen_size
    ratio = float(width) / height
    screen = (-1, 1 / ratio, 1, -1 / ratio)  # left, top, right, bottom

    image = np.zeros((height, width, 3))

    for i, y in enumerate(np.linspace(screen[1], screen[3], height)):
        for j, x in enumerate(np.linspace(screen[0], screen[2], width)):
            pixel = np.array([x, y, 0])
            ray = Ray(camera, normalize(pixel - camera))
            color = ray_trace(ray, ambient, lights, objects, max_depth)
            image[i, j] = np.clip(color, 0, 1)
    return image


def ray_trace(ray: Ray, ambient: Tuple[float, float, float], lights: List[LightSource], objects: List[Object3D], max_depth: int):
    color = np.zeros(3)
    if max_depth <= 0:
        return color
    t, obj = ray.nearest_intersected_object(objects)
    if obj is None and t > 0:
        return color
    color += ambient * obj.ambient
    P = ray.origin + t * ray.direction  # intersection
    n = obj.normal(P)
    if n @ ray.direction > 0:  # ray must be in the opposite direction from the normal
        n *= -1
    V = reflected(ray.direction, n)
    _P = P + EPSILON * n
    for light in lights:
        ray_to_light = light.get_light_ray(_P)
        d, _ = ray_to_light.nearest_intersected_object(objects)
        if d and d < light.get_distance_from_light(_P):
            continue
        L = ray_to_light.direction  # Reflection of the vector from intersection to light
        color += light.get_intensity(_P) * (L @ n * obj.diffuse + (L @ V) ** obj.shininess * obj.specular)
    return (
        color
        + obj.reflection * ray_trace(ray.calc_refraction(obj, _P, n), ambient, lights, objects, max_depth - 1) if obj.reflection else 0
        + obj.refraction * ray_trace(Ray(_P, V), ambient, lights, objects, max_depth - 1) if obj.refraction else 0
    )


# Write your own objects and lights
# TODO
def your_own_scene():
    camera = np.array([0, 0, 1])
    lights = []
    objects = []
    return camera, lights, objects
