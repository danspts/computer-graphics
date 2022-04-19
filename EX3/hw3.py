from helper_classes import *
import matplotlib.pyplot as plt

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
            # TODO
            origin, direction = [0,0,0,], normalize(Q - camera)
            for _ in range(max_depth):
                traced = Ray(origin, direction)
                if not traced:
                    break

            obj, M, N, col_ray = traced
            origin, direction = M + N * EPSILON, reflected(direction, N)
            col += reflection * col_ray
            reflection *= obj.reflection


            
            # We clip the values between 0 and 1 so all pixel values will make sense.
            image[i, j] = np.clip(color,0,1)

    return image


# Write your own objects and lights
# TODO
def your_own_scene():
    camera = np.array([0,0,1])
    lights = []
    objects = []
    return camera, lights, objects

