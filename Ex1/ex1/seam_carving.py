import numpy as np
from enum import Enum
# from numba import njit


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
    return np.array([func_dx(x), func_dy(x)])


def func_magnitude(gradient):
    return np.sqrt(np.sum(gradient * gradient, axis=0))


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
    greyscale = np.int64(get_greyscale_image(image, colour_wts))
    ###Your code here###
    ###**************###
    gradient = func_gradient(greyscale)
    magnitude = func_magnitude(gradient)
    return magnitude


class CarvingScheme(Enum):
    VERTICAL_HORIZONTAL = 0
    HORIZONTAL_VERTICAL = 1
    INTERMITTENT = 2

def generate_mask(x_len, y_len):
    A_ = np.arange(x_len, dtype=np.int64)[:,None].repeat(y_len, axis =1)
    B_ = np.arange(y_len, dtype=np.int64)[:,None].T.repeat(x_len, axis =0)
    return np.dstack((A_, B_))

def remove_tb_from_mask(traceback, mask):
    shape = mask.shape
    temp_mask = np.full(shape, True, dtype=bool)
    for index in traceback:
        temp_mask[tuple(index)] = False
    new_mask = mask[temp_mask].reshape(shape[0], shape[1] - 1, 2)
    return new_mask

# @njit
def traceback(E, prev_pointers):
    y_len = E.shape[0]
    arr_pointers = np.zeros((y_len, 2), np.int64)
    start = [y_len - 1, E[y_len - 1].argmin()]
    arr_pointers[y_len - 1] = start
    for i in range(y_len - 2, -1, -1):
        arr_pointers[i] = prev_pointers[tuple(arr_pointers[i + 1])]
    return arr_pointers

def calc_energy(image, mask):
    x_len, y_len, _ = mask.shape
    pixel_energies = np.zeros((x_len, y_len), dtype=np.int64)
    pixel_energies[0] = [image[tuple(index)] for index in mask[0]]
    backtrack = np.zeros(mask.shape, dtype=np.int64)
    print(backtrack.shape)
    for x in range(1, x_len):
        for y in range(y_len):
            y_range = np.array([max(y - 1, 0), y, min(y + 1, y_len - 1)])
            min_energy = min(pixel_energies[x - 1, y_range])
            pixel_energies[x, y] = image[tuple(mask[x, y])] + min_energy
            backtrack[x, y] = [x - 1, max(y - 1, 0)] if min_energy == pixel_energies[x - 1, max(y - 1, 0)] else \
                              [x - 1,y] if min_energy == pixel_energies[x - 1,y] else [x - 1, min(y + 1, y_len - 1)]
    return pixel_energies, backtrack

def carve_vertical(image, new_shape, magnitude, mask):
    tbs = []
    print(image.shape[1] - new_shape[1])
    for _ in range(image.shape[1] - new_shape[1]):
        print(_)
        Energy, backtrack = calc_energy(magnitude, mask)
        print(f"Energy.shape = ", Energy.shape)
        tb = traceback(E = Energy, prev_pointers = backtrack)
        tbs.append(tb)
        mask = remove_tb_from_mask(traceback=tb, mask=mask)
    return mask, tbs

def visualise_seams(image, new_shape, carving_scheme, colour, colour_wts, concat = True):
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
    grad_magnitude = gradient_magnitude(image, colour_wts)
    tbs_vertical = []
    tbs_horizontal = []

    match carving_scheme:
        case CarvingScheme.VERTICAL_HORIZONTAL:
            mask = generate_mask(image.shape[0], image.shape[1])
            mask, tbs_vertical = carve_vertical(image, new_shape, grad_magnitude, mask)
            grad_magnitude_T, image_T = grad_magnitude.T, image.transpose((1, 0, 2))
            mask_T = np.flip(np.transpose(mask, (1, 0, 2)), axis = 2)
            new_shape_T = new_shape[::-1]
            mask_T, tbs_horizontal_temp = carve_vertical(image_T, new_shape_T, grad_magnitude_T, mask_T)
            tbs_horizontal = np.flip(tbs_horizontal_temp, axis = 2)
        case CarvingScheme.HORIZONTAL_VERTICAL:
            tbs_vertical_flipped, tbs_horizontal_flipped = visualise_seams(
                np.transpose(image, (1, 0, 2)), new_shape[::-1], CarvingScheme.VERTICAL_HORIZONTAL, colour, colour_wts, concat=False
            )
            tbs_vertical = list(np.flip(tbs_vertical_flipped, axis = 2))
            tbs_horizontal = list(np.flip(tbs_horizontal_flipped, axis = 2))
        case CarvingScheme.INTERMITTENT:
            pass

    if concat:
        tbs_vertical.extend( tbs_horizontal)
        return tbs_vertical
    else:
        return tbs_vertical, tbs_horizontal


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
