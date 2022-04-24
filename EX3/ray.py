from typing import Tuple

import numpy as np

from objects import Object3D


class Ray:
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction

    # The function is getting the collection of objects in the scene and looks for the one with minimum distance.
    # The function should return the nearest object and its distance (in two different arguments)
    def nearest_intersected_object(self, objects) -> Tuple[Object3D, float]:
        nearest_object = None
        min_distance = np.inf
        for obj in objects:
            dist_obj = obj.intersect(self)
            if dist_obj is not None and dist_obj < min_distance:
                nearest_object = dist_obj
        return nearest_object, min_distance
