from typing import List, Tuple

import numpy as np
from numpy import linalg as LA
import re

EPSILON = 1e-5
AIR_REFRACTION = 1

# This function gets a vector and returns its normalized form.
def normalize(vector):
    return vector / np.linalg.norm(vector)


# TODO:
# This function gets a vector and the normal of the surface it hit
# This function returns the vector that reflects from the surface
def reflected(vector, normal):
    n = normalize(normal)
    return vector - 2 * vector.dot(n) * n


## Lights
class Object3D:
    def set_material(self, ambient, diffuse, specular, shininess, reflection, refraction=None, refraction_index=1):
        self.ambient = np.float64(ambient)
        self.diffuse = np.float64(diffuse)
        self.specular = np.float64(specular)
        self.shininess = shininess
        self.reflection = reflection
        self.refraction = refraction
        self.refraction_index = refraction_index

    def normal(self, point):
        raise NotImplementedError


class Ray:
    def __init__(self, origin, direction, refraction_index=AIR_REFRACTION):
        self.origin = origin
        self.direction = normalize(direction)
        self.refraction_index = refraction_index

    # The function is getting the collection of objects in the scene and looks for the one with minimum distance.
    # The function should return the nearest object and its distance (in two different arguments)
    def nearest_intersected_object(self, objects: List[Object3D]) -> Tuple[float, Object3D]:
        nearest_object = None
        min_distance = np.inf
        for obj in objects:
            dist_obj, component = obj.intersect(self)
            if component is not None and dist_obj < min_distance:
                nearest_object = component
                min_distance = dist_obj
        return min_distance, nearest_object

    def calc_refraction(self, obj: Object3D, P, N):
        cos_theta = N @ self.direction
        sin_theta_1 = np.sqrt(1 - cos_theta * cos_theta)
        r = self.refraction_index / obj.refraction_index
        sin_theta_2 = r * sin_theta_1
        cos_theta_2 = np.sqrt(1 - sin_theta_2 * sin_theta_2)
        L = ((r * cos_theta - cos_theta_2) * N - self.direction) / r
        if self.refraction_index == AIR_REFRACTION:
            new_index = obj.refraction_index  # enters new medium
        else:
            new_index = AIR_REFRACTION
        return Ray(P, L, new_index)


class LightSource:
    def __init__(self, intensity):
        self.intensity = intensity

    def get_light_ray(self, intersection_point) -> Ray:
        raise NotImplementedError

    def get_distance_from_light(self, intersection) -> float:
        raise NotImplementedError

    def get_intensity(self, intersection) -> float:
        raise NotImplementedError


class DirectionalLight(LightSource):
    def __init__(self, intensity, direction):
        super().__init__(intensity)
        self.direction = normalize(direction)

    # This function returns the ray that goes from the light source to a point
    def get_light_ray(self, intersection_point) -> Ray:
        return Ray(intersection_point, self.direction)

    # This function returns the distance from a point to the light source
    def get_distance_from_light(self, intersection):
        return np.inf

    # This function returns the light intensity at a point
    def get_intensity(self, intersection):
        return self.intensity


class PointLight(LightSource):
    def __init__(self, intensity, position, kc, kl, kq):
        super().__init__(intensity)
        self.position = np.array(position)
        self.kc = kc
        self.kl = kl
        self.kq = kq

    # This function returns the ray that goes from the light source to a point
    def get_light_ray(self, intersection) -> Ray:
        return Ray(intersection, normalize(self.position - intersection))

    # This function returns the distance from a point to the light source
    def get_distance_from_light(self, intersection):
        return np.linalg.norm(intersection - self.position)

    # This function returns the light intensity at a point
    def get_intensity(self, intersection):
        d = self.get_distance_from_light(intersection)
        return self.intensity / (self.kc + self.kl * d + self.kq * d * d)


class SpotLight(PointLight):
    def __init__(self, intensity, position, direction, kc, kl, kq):
        super().__init__(intensity, position, kc, kl, kq)
        self.direction = normalize(direction)

    def get_intensity(self, intersection):
        v = normalize(self.position - intersection)
        return super().get_intensity(intersection) * np.dot(v, self.direction)


class Plane(Object3D):
    def __init__(self, normal, point):
        self._normal = normalize(np.array(normal, dtype=np.float64))
        self.point = np.array(point, dtype=np.float64)

    def intersect(self, ray: Ray):
        v = self.point - ray.origin
        denom = np.dot(self._normal, ray.direction)
        if abs(denom) < EPSILON:
            return None, None
        t = np.dot(v, self._normal) / denom
        if t > 0:
            return t, self
        else:
            return None, None

    def normal(self, point):
        return self._normal


class Triangle(Object3D):
    # Triangle gets 3 points as arguments
    def __init__(self, a, b, c):
        self.a = np.array(a, dtype=np.float64)
        self.b = np.array(b, dtype=np.float64)
        self.c = np.array(c, dtype=np.float64)
        self._normal = self.compute_normal()

    def compute_normal(self):
        self.v_ab = self.b - self.a
        self.v_ac = self.c - self.a
        n = np.cross(self.v_ab, self.v_ac)
        return normalize(n)

    def intersect(self, ray: Ray):
        # Möller–Trumbore intersection
        p = np.cross(ray.direction, self.v_ac)
        det = self.v_ab.dot(p)

        if abs(det) < EPSILON:  # no intersection
            return None, None

        inv_det = 1.0 / det
        r = ray.origin - self.a
        u = r.dot(p) * inv_det

        if u < 0 or u > 1:  # if not intersection
            return None, None

        q = np.cross(r, self.v_ab)
        v = ray.direction.dot(q) * inv_det
        if v < 0.0 or u + v > 1.0:  # if not intersection
            return None, None

        t = self.v_ac.dot(q) * inv_det
        if t > EPSILON:
            return t, self
        else:
            return None, None

    def normal(self, point):
        return self._normal


class Sphere(Object3D):
    def __init__(self, center, radius: float):
        self.center = center
        self.radius = radius

    def intersect(self, ray: Ray):
        _r = self.center - ray.origin
        if (v := _r.dot(ray.direction)) >= 0:
            if (d_2 := _r @ _r - v * v) >= 0:
                if (diff := self.radius * self.radius - d_2) >= 0:
                    return v - np.sqrt(diff), self
        return None, None

    def normal(self, point):
        return normalize(point - self.center)


class Mesh(Object3D):
    # Mesh are defined by a list of vertices, and a list of faces.
    # The faces are triplets of vertices by their index number.
    def __init__(self, v_list, f_list):
        self.v_list = v_list
        self.f_list = f_list
        self.triangle_list: List[Triangle] = []
        for p1, p2, p3 in self.f_list:
            self.triangle_list.append(Triangle(self.v_list[p1], self.v_list[p2], self.v_list[p3]))

    def apply_materials_to_triangles(self):
        for t in self.triangle_list:
            t.set_material(
                self.ambient,
                self.diffuse,
                self.specular,
                self.shininess,
                self.reflection,
                self.refraction,
                self.refraction_index,
            )

    # Hint: Intersect returns both distance and nearest object.
    # Keep track of both.
    def intersect(self, ray: Ray):
        return ray.nearest_intersected_object(self.triangle_list)


def rotation_z(point: Tuple[float, float, float], degrees: float):
    deg = np.deg2rad(degrees)
    matrix = np.array([[np.cos(deg), np.sin(deg), 0], [-np.sin(deg), np.cos(deg), 0], [0, 0, 1]])
    return (matrix @ np.array(point))


def read_obj(filename: str) -> Mesh:
    vectors = []
    faces = []
    with open(filename, "r") as reader:
        for l in reader:
            args = re.findall(r"\S+", l)
            if not args:
                continue
            match args[0]:
                case "v":
                    vectors.append(args[1:])
                case "f":
                    faces.append(args[1:])
    return Mesh(np.array(vectors, float), np.array(faces, int) - 1)
