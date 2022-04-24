from ast import Raise
from typing import List, Callable
from enum import Enum

import matplotlib.pyplot as plt

from helper_classes import *


class RenderModel(Enum):
    phong = 0
    blinn_phong = 1
    default = phong


def render_scene(camera, ambient, lights, objects, screen_size, max_depth, render_model: RenderModel = RenderModel.default):
    width, height = screen_size
    ratio = float(width) / height
    screen = (-1, 1 / ratio, 1, -1 / ratio)  # left, top, right, bottom

    image = np.zeros((height, width, 3))

    match render_model:
        case RenderModel.blinn_phong:
            model_func = lambda n, D, L, V, a: normalize(L - D).dot(n) ** (a / 4)
        case RenderModel.phong:
            model_func = lambda n, D, L, V, a: (L @ V) ** a
    for i, y in enumerate(np.linspace(screen[1], screen[3], height)):
        for j, x in enumerate(np.linspace(screen[0], screen[2], width)):
            pixel = np.array([x, y, 0])
            ray = Ray(camera, normalize(pixel - camera))
            color = ray_trace(ray, ambient, lights, objects, max_depth, model_func)
            image[i, j] = np.clip(color, 0, 1)
    return image


def render_scene_blinn(*args):
    return render_scene(*args, render_model=RenderModel.blinn_phong)


def ray_trace(
    ray: Ray,
    ambient: Tuple[float, float, float],
    lights: List[LightSource],
    objects: List[Object3D],
    max_depth: int,
    model_func: Callable,
):
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
            if _ is obj:
                raise ValueError
            continue
        L = ray_to_light.direction  # Reflection of the vector from intersection to light
        color += light.get_intensity(_P) * (
            L @ n * obj.diffuse + model_func(n, ray.direction, L, V, obj.shininess) * obj.specular
        )
    return (
        color + obj.reflection * ray_trace(Ray(_P, V), ambient, lights, objects, max_depth - 1, model_func)
        if obj.reflection
        else 0 + obj.refraction * ray_trace(ray.calc_refraction(obj, _P, n), ambient, lights, objects, max_depth - 1, model_func)
        if obj.refraction
        else 0
    )


# Write your own objects and lights
# TODO
def your_own_scene():
    camera = np.array([0, 0, 1])

    p1 = [0.2, 0.175, -0.5]
    p2 = [0, 0.6, 0]

    spheres = [Sphere(rotation_z(p2, i * 72), 0.1) for i in range(5)]
    for s in spheres:
        s.set_material([0.93, 1, 0.54], [0.93, 1, 0.54], [0.3, 0.3, 0.3], 100, 1, 0.5, 1.333)

    v_list = [
        [0, 0, 0],
        p1,
        p2,
        rotation_z(p1, -72),
        rotation_z(p2, 72),
        rotation_z(p1, 72),
        rotation_z(p2, 72 * 2),
        rotation_z(p1, 72 * 2),
        rotation_z(p2, -72),
        rotation_z(p1, -72 * 2),
        rotation_z(p2, -72 * 2),
    ]
    f_list = [[0, 1, 2], [0, 1, 4], [0, 4, 5], [0, 5, 6], [0, 6, 7], [0, 2, 3], [0, 3, 8], [0, 8, 9], [0, 9, 10], [0, 10, 7]]

    mesh = Mesh(v_list, f_list)
    mesh.set_material([1, 1, 0.22], [1, 1, 0.21], [1, 1, 1], 10, 0.5)
    mesh.apply_materials_to_triangles()

    floor = Plane([0, 1, 0], [0, -1, 0])
    floor.set_material([0.2, 0.2, 0.2], [0.2, 0.2, 0.2], [1, 1, 1], 1000, 0.5)
    background = Plane([0, 0, 1], [0, 0, -10])
    background.set_material([0.4, 1, 0.9], [0.5, 1, 1], [0, 0, 0], 1000, 0.5)

    objects = [mesh, background, floor] + spheres  # , sphere_a, sphere_b, floor, background]

    light1 = PointLight(intensity=np.array([1, 1, 1]), position=np.array([0.6, 0.5, -5]), kc=0.1, kl=0.1, kq=0.1)
    light2 = DirectionalLight(intensity=np.array([0.8, 0.8, 0.8]), direction=np.array([1, 1, 1]))

    lights = [light1, light2]

    ambient = np.array([0.1, 0.2, 0.3])

    return camera, lights, objects, ambient
