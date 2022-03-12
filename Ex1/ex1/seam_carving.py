import numpy as np
from enum import Enum
from numba import jit, njit, vectorize, prange
import numba as nb
from numba.pycc import CC


def func_dx(x):
    match len(x.shape):
        case 2:
            return np.hstack((x[:, 1:], np.zeros((x.shape[0], 1)))) - x
        case 3:
            return np.hstack((x[:, 1:, :], np.zeros((x.shape[0], 1, x.shape[2])))) - x


def func_dy(x):
    match len(x.shape):
        case 2:
            return np.vstack((x[1:, :], np.zeros((1, x.shape[1])))) - x
        case 3:
            return np.vstack((x[1:, :, :], np.zeros((1, x.shape[1], x.shape[2])))) - x


def func_gradient(x):
    return func_dx(x), func_dy(x)


def func_magnitude(gradient):
    return np.sqrt(gradient[0] * gradient[0] + gradient[1] * gradient[1])


def get_greyscale_image(image, colour_wts):
    """
    Gets an image and weights of each colour and returns the image in greyscale
    :param image: The original image
    :param colour_wts: the weights of each colour in rgb (ints > 0)
    :returns: the image in greyscale
    """
    greyscale_image = np.uint8(image @ colour_wts)
    return greyscale_image


def reshape_bilinear(image, new_shape):
    """
    Resizes an image to new shape using bilinear interpolation method
    :param image: The original image
    :param new_shape: a (height, width) tuple which is the new shape
    :returns: the image resized to new_shape
    """
    in_height, in_width, _ = image.shape
    out_height, out_width = new_shape
    ###Your code here###
    ###**************###
    x_lin = np.linspace(0, in_height - 1, num=out_height)
    y_lin = np.linspace(0, in_width - 1, num=out_width)
    x_floor, y_floor = x_lin.astype(int), y_lin.astype(int)
    x_ceil, y_ceil = np.ceil(x_lin).astype(int), np.ceil(y_lin).astype(int)
    x_weight = (x_lin - x_floor)[:, None, None]
    y_weight = (y_lin - y_floor)[None, :, None]
    c1 = image[x_floor][:, y_floor]
    c2 = image[x_ceil][:, y_floor]
    c3 = image[x_floor][:, y_ceil]
    c4 = image[x_ceil][:, y_ceil]
    c12 = (1 - x_weight) * c1 + x_weight * c2
    c34 = (1 - x_weight) * c3 + x_weight * c4
    new_image = (1 - y_weight) * c12 + y_weight * c34
    return np.uint8(new_image)


def gradient_magnitude(image, colour_wts):
    """
    Calculates the gradient image of a given image
    :param image: The original image
    :param colour_wts: the weights of each colour in rgb (> 0)
    :returns: The gradient image
    """
    greyscale = get_greyscale_image(image, colour_wts)
    ###Your code here###
    ###**************###
    gradient = func_gradient(greyscale)
    magnitude = np.uint16(func_magnitude(gradient))
    return magnitude


class CarvingScheme(Enum):
    VERTICAL_HORIZONTAL = 0
    HORIZONTAL_VERTICAL = 1
    INTERMITTENT = 2


@njit
def calc_energy(image, forward = False):
    pixel_energies = np.zeros(image.shape, dtype=np.int64)
    pixel_energies[0] = image[0]
    backtrack = np.zeros(image.shape, dtype=np.int64)
    x_len, y_len = image.shape
    for x in range(1, x_len):
        for y in range(y_len):
            y_range = np.array([max(y - 1, 0), y, min(y + 1, y_len - 1)])
            min_energy = min(pixel_energies[x - 1][y_range])
            pixel_energies[x, y] = image[x, y] + min_energy
            backtrack[x, y] = max(y - 1, 0) if min_energy == pixel_energies[x - 1][max(y - 1, 0)] else \
                              y if min_energy == pixel_energies[x - 1][y] else min(y + 1, y_len - 1)
    return pixel_energies, backtrack


def visualise_seams(image, new_shape, carving_scheme, colour):
    """
    Visualises the seams that would be removed when reshaping an image to new image (see example in notebook)
    :param image: The original image
    :param new_shape: a (height, width) tuple which is the new shape
    :param carving_scheme: the carving scheme to be used.
    :param colour: the colour of the seams (an array of size 3)
    :returns: an image where the removed seams have been coloured.
    """
    ###Your code here###
    ###**************###
    match carving_scheme:
        case CarvingScheme.VERTICAL_HORIZONTAL:
            pass
        case CarvingScheme.HORIZONTAL_VERTICAL:
            return visualise_seams(
                image.T, new_shape.T, CarvingScheme.VERTICAL_HORIZONTAL, colour
            ).T
        case CarvingScheme.INTERMITTENT:
            pass

    magnitude = image
    return seam_image


def reshape_seam_craving(image, new_shape, carving_scheme):
    """
    Resizes an image to new shape using seam carving
    :param image: The original image
    :param new_shape: a (height, width) tuple which is the new shape
    :param carving_scheme: the carving scheme to be used.
    :returns: the image resized to new_shape
    """
    ###Your code here###
    ###**************###
    return new_image
