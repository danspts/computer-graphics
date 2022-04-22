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
            color = ray_trace(ray, ambient, lights, objects, camera, max_depth)
            image[i, j] = np.clip(color, 0, 1)
    return image

def ray_trace(ray: Ray, ambient, lights : List[LightSource], objects : List[Object3D], camera, max_depth : int):
    color = np.zeros(3)
    if max_depth <= 0:
        return color
    min_distance, nearest_object = ray.nearest_intersected_object(objects)
    if nearest_object is None:
        return color
    color = ambient * nearest_object.ambient
    intersection = ray.origin + min_distance * ray.direction 
    normal_to_surface = nearest_object.normal(intersection)
    shifted_point = intersection + EPSILON * normal_to_surface

    for light in lights:
        ray_to_light = light.get_light_ray(shifted_point)

        min_distance, _ = ray_to_light.nearest_intersected_object(objects)
        intersection_to_light_distance = light.get_distance_from_light(intersection)

        if min_distance < intersection_to_light_distance:
            continue

        recursion_ray = Ray(shifted_point, reflected(ray.direction, normal_to_surface))
        intersection_to_camera = normalize(camera - intersection)
        H = normalize(ray_to_light.direction + intersection_to_camera)

        color = (
            color
            + nearest_object.diffuse * light.get_intensity(intersection) * np.dot(ray_to_light.direction, normal_to_surface)
            + nearest_object.specular * light.get_intensity(intersection) * np.dot(normal_to_surface, H) ** nearest_object.shininess
            + nearest_object.reflection * ray_trace(recursion_ray, ambient, lights, objects, camera, max_depth - 1)
        )
    return color


# Write your own objects and lights
# TODO
def your_own_scene():
    camera = np.array([0,0,1])
    lights = []
    objects = []
    return camera, lights, objects

