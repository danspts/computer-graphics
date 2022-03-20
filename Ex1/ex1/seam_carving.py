#! /usr/bin/python3
# Python 3.10.X

import numpy as np
from enum import IntEnum
from numba import njit

GREYSCALE_WT_DEFAULT = np.array([0.299, 0.587, 0.114], dtype=np.float64)
SEAMS_COLOR_DEFAULT = np.array([0, 0, 0], dtype=np.uint8)


class CarvingScheme(IntEnum):
    VERTICAL_HORIZONTAL = 0
    HORIZONTAL_VERTICAL = 1
    INTERMITTENT = 2


class VisualizeScheme(IntEnum):
    HORIZONTAL = True
    VERTICAL = False


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


def get_greyscale_image(image, colour_wts=GREYSCALE_WT_DEFAULT):
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


def gradient_magnitude(image, colour_wts=GREYSCALE_WT_DEFAULT):
    """
    Calculates the gradient image of a given image
    :param image: The original image
    :param colour_wts: the weights of each colour in rgb (> 0)
    :returns: The gradient image
    """
    greyscale = np.int64(get_greyscale_image(image, colour_wts))
    gradient = func_gradient(greyscale)
    magnitude = func_magnitude(gradient)
    return magnitude


def generate_mask(x_len, y_len):
    A_ = np.arange(x_len, dtype=np.int64)[:, None].repeat(y_len, axis=1)
    B_ = np.arange(y_len, dtype=np.int64)[:, None].T.repeat(x_len, axis=0)
    return np.dstack((A_, B_))


def remove_tb_from_mask(traceback, mask):
    shape = mask.shape
    temp_mask = np.full(shape, True, dtype=bool)
    for index in traceback:
        temp_mask[index[0], index[1]] = [False, False]
    new_mask = mask[temp_mask].reshape(shape[0], shape[1] - 1, 2)
    return new_mask


@njit
def traceback(E, prev_pointers, mask):
    x_len = prev_pointers.shape[0]
    masked_arr_pointers = np.zeros((x_len, 2), np.int64)
    arr_pointers = np.zeros((x_len, 2), np.int64)
    next = np.zeros(2, np.int64)
    next[0] = x_len - 1
    next[1] = E[x_len - 1].argmin()
    for i in range(x_len - 1, -1, -1):
        masked_arr_pointers[i] = next
        arr_pointers[i] = mask[next[0], next[1]]
        next = prev_pointers[masked_arr_pointers[i][0], masked_arr_pointers[i][1]]
    return masked_arr_pointers, arr_pointers


@njit(cache=True)
def calc_energy(image, mask):
    x_len, y_len, _ = mask.shape
    pixel = lambda x, y : image[mask[x,y, 0], mask[x,y, 1]] if y >= 0 and y < y_len else 9999 #absurd value if you try to access out of range
    pixel_energies = np.zeros((x_len, y_len), dtype=np.int64)
    pixel_energies[0] = [pixel(0, y) for y in range(y_len)]
    c_t = lambda x, y: np.absolute(pixel(x, max(y - 1, 0)) - pixel(x, min(y + 1, y_len - 1))) # top value
    c_l = lambda x, y: np.absolute(pixel(x, y - 1) - pixel(x - 1, y)) # left value 
    c_r = lambda x, y: np.absolute(pixel(x, y + 1) - pixel(x - 1, y)) # right value
    backtrack = np.zeros(mask.shape, dtype=np.int64)
    for x in range(1, x_len):
        for y in range(y_len):
            energy_options = np.zeros(3, dtype=np.int64)
            energy_options[0] = pixel_energies[x - 1, y - 1] + c_t(x,y) + c_l(x,y)
            energy_options[1] = pixel_energies[x - 1, y] + c_t(x,y) 
            energy_options[2] = pixel_energies[x - 1, y + 1] + c_t(x,y) + c_r(x, y)
            min_energy = np.min(energy_options)
            backtrack[x, y] = [x - 1, y + np.argmin(energy_options) - 1]
            pixel_energies[x, y] = pixel(x, y) + min_energy
    return pixel_energies, backtrack


def carve_vertical(magnitude, new_shape, mask):
    tbs = []
    for _ in range(mask.shape[1] - new_shape[1]):
        Energy, backtrack = calc_energy(magnitude, mask)
        masked_tb, tb = traceback(E=Energy, prev_pointers=backtrack, mask=mask)
        tbs.append(tb)
        mask = remove_tb_from_mask(traceback=masked_tb, mask=mask)
    return mask, tbs


def visualise_seams(
    image,
    new_shape,
    show_horizontal: VisualizeScheme,
    colour,
    greyscale_wt=GREYSCALE_WT_DEFAULT,
):
    """
    Visualises the seams that would be removed when reshaping an image to new image (see example in notebook)
    :param image: The original image
    :param new_shape: a (height, width) tuple which is the new shape
    :param carving_scheme: the carving scheme to be used.
    :param colour: the colour of the seams (an array of size 3)
    :returns: an image where the removed seams have been coloured.
    """
    delete_tbs = []
    match show_horizontal:
        case VisualizeScheme.VERTICAL:
            delete_tbs, *_ = get_seams(
                image,
                new_shape,
                CarvingScheme.VERTICAL_HORIZONTAL,
                colour_wts=greyscale_wt,
                concat=False,
            )
        case VisualizeScheme.HORIZONTAL:
            _, delete_tbs, _ = get_seams(
                image,
                new_shape,
                CarvingScheme.HORIZONTAL_VERTICAL,
                colour_wts=greyscale_wt,
                concat=False,
            )
        # case VisualizeScheme.BOTH:
        #     delete_tbs = get_seams(image, new_shape, CarvingScheme.VERTICAL_HORIZONTAL, colour_wts=greyscale_wt)
    return overwrite_tb_pixels(tbs=delete_tbs, image=image, colour=colour)


def get_seams(
    image,
    new_shape,
    carving_scheme,
    colour_wts=GREYSCALE_WT_DEFAULT,
    concat=True,
    mask=None,
):
    grad_magnitude = gradient_magnitude(image, colour_wts)
    tbs_vertical = []
    tbs_horizontal = []
    if mask is None:
        mask = generate_mask(grad_magnitude.shape[0], grad_magnitude.shape[1])
    match carving_scheme:
        case CarvingScheme.VERTICAL_HORIZONTAL:
            mask, tbs_vertical = carve_vertical(grad_magnitude, new_shape, mask)
            grad_magnitude_T = grad_magnitude.T
            mask_T = np.flip(np.transpose(mask, (1, 0, 2)), axis=2)
            mask_T, tbs_horizontal_temp = carve_vertical(
                grad_magnitude_T, new_shape[::-1], mask_T
            )
            if tbs_horizontal_temp:
                tbs_horizontal = list(np.flip(tbs_horizontal_temp, axis=2))
            mask = np.flip(np.transpose(mask_T, (1, 0, 2)), axis=2)
        case CarvingScheme.HORIZONTAL_VERTICAL:
            mask_T = np.flip(np.transpose(mask, (1, 0, 2)), axis=2)
            tbs_vertical_flipped, tbs_horizontal_flipped, mask_T = get_seams(
                np.transpose(image, (1, 0, 2)),
                new_shape[::-1],
                CarvingScheme.VERTICAL_HORIZONTAL,
                colour_wts,
                concat=False,
                mask=mask_T,
            )
            mask = np.flip(np.transpose(mask_T, (1, 0, 2)), axis=2)
            tbs_vertical = (
                list(np.flip(tbs_horizontal_flipped, axis=2))
                if tbs_vertical_flipped
                else []
            )
            tbs_horizontal = (
                list(np.flip(tbs_vertical_flipped, axis=2))
                if tbs_horizontal_flipped
                else []
            )
        case CarvingScheme.INTERMITTENT:
            for i in range(
                1, max(image.shape[0] - new_shape[0], image.shape[1] - new_shape[1]) + 1
            ):
                new_x, new_y = max(new_shape[0], image.shape[0] - i), max(
                    new_shape[1], image.shape[1] - i
                )
                tbs_vertical_temp, tbs_horizontal_temp, mask = get_seams(
                    image,
                    (new_x, new_y),
                    CarvingScheme.VERTICAL_HORIZONTAL,
                    colour_wts,
                    concat=False,
                    mask=mask,
                )
                tbs_vertical.extend(tbs_vertical_temp)
                tbs_horizontal.extend(tbs_horizontal_temp)
    if concat:
        tbs_vertical.extend(tbs_horizontal)
        return tbs_vertical
    else:
        return tbs_vertical, tbs_horizontal, mask


def overwrite_tb_pixels(image, tbs, colour=[0, 0, 0]):
    
    image_copy = image.copy()
    for tb in tbs:
        for index in tb:
            image_copy[index[0], index[1]] = colour
    return image_copy


def reshape_seam_carving(
    image, new_shape, carving_scheme, colour_wts=GREYSCALE_WT_DEFAULT
):
    """
    Resizes an image to new shape using seam carving
    :param image: The original image
    :param new_shape: a (height, width) tuple which is the new shape
    :param carving_scheme: the carving scheme to be used.
    :param colour_wts: greyscale color weights if a different ration is desired
    :returns: the image resized to new_shape
    """
    *_, mask = get_seams(image, new_shape, carving_scheme, colour_wts, concat=False)
    new_image = np.zeros((new_shape[0], new_shape[1], 3), dtype=np.int64)
    for x in range(mask.shape[0]):
        for y in range(mask.shape[1]):
            new_image[x, y] = image[mask[x, y, 0], mask[x, y, 1]]
    return np.array(new_image, dtype=np.uint8)
