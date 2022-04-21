import numpy as np

from ray import Ray
from utils import normalize, refleted

class Object3D:

    def __init__(self):
        self.normal = None
        raise NotImplementedError("Not Implemented - abstract class")


    def set_material(self, ambient, diffuse, specular, shininess, reflection):
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess
        self.reflection = reflection
    
    def intersect(self, ray: Ray):
        raise NotImplementedError("Not Implemented - abstract class")


class Plane(Object3D):
    def __init__(self, normal, point):
        self.normal = np.array(normal)
        self.point = np.array(point)

    def intersect(self, ray: Ray):
        v = self.point - ray.origin
        t = (np.dot(v, self.normal) / np.dot(self.normal, ray.direction))
        if t > 0:
            return t
        else:
            return None



class Triangle(Object3D):
    # Triangle gets 3 points as arguments
    def __init__(self, a, b, c):
        self.a = np.array(a)
        self.b = np.array(b)
        self.c = np.array(c)
        self.normal = self.compute_normal()

    def compute_normal(self):
        v1 = self.b - self.a
        v2 = self.c - self.a
        n = np.array(np.cross(v1, v2))
        return n

    # Hint: First find the intersection on the plane
    # Later, find if the point is in the triangle using barycentric coordinates
    def intersect(self, ray: Ray):
        plane = Plane(self.normal,self.a)
        t = plane.intersect(ray)
        if t is None:
            return None
        areaABC = normalize(np.cross((self.b - self.a),(self.c - self.a)))
        p = ray.origin + t * ray.direction
        alpha = normalize(np.cross((self.b - p),(self.c - p))) / areaABC
        beta = normalize(np.cross((self.c - p),(self.a - p))) / areaABC
        if 0 < alpha + beta < 1 and 0 < alpha < 1 and 0 < beta < 1 :
            return t
        else:
            return None

class Sphere(Object3D):
    def __init__(self, center, radius: float):
        self.center = center
        self.radius = radius

    def intersect(self, ray: Ray):
        a = np.dot(ray.direction,ray.direction)
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
            return t1 if t1 >= 0 and t0 < 0 else t0
        return None


class Mesh(Object3D):
    # Mesh are defined by a list of vertices, and a list of faces.
    # The faces are triplets of vertices by their index number.
    def __init__(self, v_list, f_list):
        self.v_list = v_list
        self.f_list = f_list
        self.triangle_list = []
        for p1, p2, p3 in self.f_list:
            self.triangle_list.append(Triangle(self.v_list[p1], self.v_list[p2], self.v_list[p3]))

    def apply_materials_to_triangles(self):
        for t in self.triangle_list:
            t.set_material(self.ambient,self.diffuse,self.specular,self.shininess,self.reflection)

    # Hint: Intersect returns both distance and nearest object.
    # Keep track of both.
    def intersect(self, ray: Ray):
        for triangle in self.triangle_list:
            if d := triangle.intersect(ray):
                return d, triangle
        return None
