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


def ray_trace(
    ray: Ray,
    ambient,
    lights: List[LightSource],
    objects: List[Object3D],
    max_depth: int,
):
    color = np.zeros(3)
    if max_depth <= 0:
        return color
    t, nearest_object = ray.nearest_intersected_object(objects)
    if nearest_object is None:
        return color
    color = ambient * nearest_object.ambient
    P = ray.origin + t * ray.direction
    n = normalize(nearest_object.normal(P))
    if n.dot(ray.direction) > 0:
        n *= -1.0
    shifted_P = P + EPSILON * n
    V = normalize(ray.origin - shifted_P)
    for light in lights:
        ray_to_light = light.get_light_ray(shifted_P)
        min_distance, _ = ray_to_light.nearest_intersected_object(objects)
        if 0 < min_distance < light.get_distance_from_light(P):
            continue
        L = ray_to_light.direction
        R = normalize(reflected(L, n))
        color = color + np.multiply(light.get_intensity(P), (
            nearest_object.diffuse * L.dot(n)
            + nearest_object.specular * V.dot(R) ** nearest_object.shininess
        ))
    reflection_ray = Ray(shifted_P, normalize(reflected(V, n)))
    return color + nearest_object.reflection * ray_trace(
        reflection_ray, ambient, lights, objects, max_depth - 1
    )


# Write your own objects and lights
# TODO
def your_own_scene():
    camera = np.array([0, 0, 1])
    lights = []
    objects = []
    return camera, lights, objects
