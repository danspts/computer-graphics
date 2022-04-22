from typing import List, Tuple

import numpy as np
from numpy import linalg as LA

EPSILON = 1e-5

# This function gets a vector and returns its normalized form.
def normalize(vector):
    return vector / np.linalg.norm(vector)


# TODO:
# This function gets a vector and the normal of the surface it hit
# This function returns the vector that reflects from the surface
def reflected(vector, normal):
    n = normalize(normal)
    return vector - 2 * (vector @ n) * n

## Lights

class Object3D:

    def set_material(self, ambient, diffuse, specular, shininess, reflection):
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.reflection = reflection

    def normal(self, point):
        raise NotImplementedError

class LightSource:

    def __init__(self, intensity):
        self.intensity = intensity


class DirectionalLight(LightSource):

    def __init__(self, intensity, direction):
        super().__init__(intensity)
        self.direction = normalize(direction)

    # This function returns the ray that goes from the light source to a point
    def get_light_ray(self,intersection_point):
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
    def get_light_ray(self,intersection):
        return Ray(intersection,normalize(self.position - intersection))

    # This function returns the distance from a point to the light source
    def get_distance_from_light(self,intersection):
        return np.linalg.norm(intersection - self.position)

    # This function returns the light intensity at a point
    def get_intensity(self, intersection):
        d = self.get_distance_from_light(intersection)
        return self.intensity / (self.kc + self.kl*d + self.kq * d * d)


class SpotLight(PointLight):
    def __init__(self, intensity, position, direction, kc, kl, kq):
        super().__init__(intensity, position, kc, kl, kq)
        self.direction = normalize(direction)

    def get_intensity(self, intersection):
        v = normalize(self.position - intersection)
        return super().get_intensity(intersection) * np.dot(v, self.direction)


class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

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





class Plane(Object3D):
    def __init__(self, normal, point):
        self._normal = np.array(normal)
        self.point = np.array(point)

    def intersect(self, ray: Ray):
        v = self.point - ray.origin
        t = (np.dot(v, self._normal) / np.dot(self._normal, ray.direction))
        if t > 0:
            return t, self
        else:
            return None, None

    def normal(self, point):
        return self._normal



class Triangle(Object3D):
    # Triangle gets 3 points as arguments
    def __init__(self, a, b, c):
        self.a = np.array(a)
        self.b = np.array(b)
        self.c = np.array(c)
        self._normal = self.compute_normal()

    def compute_normal(self):
        self.v_ab = self.b - self.a
        self.v_ac = self.c - self.a
        n =  np.cross(self.v_ab, self.v_ac)
        return normalize(n)

    # Hint: First find the intersection on the plane
    # Later, find if the point is in the triangle using barycentric coordinates
    def intersect(self, ray: Ray):
        pvec = np.cross(ray.direction, self.v_ac)
        det = self.v_ab.dot(pvec)

        if abs(det) < EPSILON:  # no intersection
            return None, None

        inv_det = 1.0 / det
        tvec = ray.origin - self.a
        u = tvec.dot(pvec) * inv_det

        if u < 0.0 or u > 1.0:  # if not intersection
            return None, None

        qvec = np.cross(tvec, self.v_ab)
        v = ray.direction.dot(qvec) * inv_det
        if v < 0.0 or u + v > 1.0:  # if not intersection
            return None, None

        t = self.v_ac.dot(qvec) * inv_det
        return t, self

    def normal(self, point):
        return self._normal

class Sphere(Object3D):
    def __init__(self, center, radius: float):
        self.center = center
        self.radius = radius

    def intersect(self, ray: Ray):
        a = np.dot(ray.direction, ray.direction)
        distance = ray.origin - self.center
        b = 2 * np.dot(ray.direction, distance)
        c = np.dot(distance, distance) - self.radius * self.radius
        disc = b * b - 4 * a * c
        if disc > 0:
            distSqrt = np.sqrt(disc)
            q = (-b - distSqrt) / 2.0 if b < 0 else (-b + distSqrt) / 2.0
            t0 = q / a
            t1 = c / q
            t0, t1 = min(t0, t1), max(t0, t1)
            return t1 if t1 >= 0 and t0 < 0 else t0, self
        return None, None

    def normal(self, point):
        return point - self.center


class Mesh(Object3D):
    # Mesh are defined by a list of vertices, and a list of faces.
    # The faces are triplets of vertices by their index number.
    def __init__(self, v_list, f_list):
        self.v_list = v_list
        self.f_list = f_list
        self.triangle_list : List[Triangle] = []
        for p1, p2, p3 in self.f_list:
            self.triangle_list.append(
                Triangle(self.v_list[p1], self.v_list[p2], self.v_list[p3])
            )

    def apply_materials_to_triangles(self):
        for t in self.triangle_list:
            t.set_material(self.ambient,self.diffuse,self.specular,self.shininess,self.reflection)

    # Hint: Intersect returns both distance and nearest object.
    # Keep track of both.
    def intersect(self, ray: Ray):
        return ray.nearest_intersected_object(self.triangle_list)