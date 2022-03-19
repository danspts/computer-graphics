import numpy as np
from enum import Enum
from numba import njit


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
class VisualizeScheme(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    BOTH = 2


def generate_mask(x_len, y_len):
    A_ = np.arange(x_len, dtype=np.int64)[:,None].repeat(y_len, axis =1)
    B_ = np.arange(y_len, dtype=np.int64)[:,None].T.repeat(x_len, axis =0)
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
    pixel_energies = np.zeros((x_len, y_len), dtype=np.int64)
    print("check1")
    for i in range(y_len):
        pixel_energies[i] = [image[index[0], index[1]] for index in mask[i]]
    print("check2")
    backtrack = np.zeros(mask.shape, dtype=np.int64)
    print(backtrack.shape)
    for x in range(1, x_len):
        for y in range(y_len):
            y_range = np.array([max(y - 1, 0), y, min(y + 1, y_len - 1)])
            min_energy = min([pixel_energies[x - 1, y] for y in y_range])
            pixel_energies[x, y] = image[mask[x, y, 0], mask[x, y, 1]] + min_energy
            backtrack[x, y] = [x - 1, max(y - 1, 0)] if min_energy == pixel_energies[x - 1, max(y - 1, 0)] else \
                              [x - 1,y] if min_energy == pixel_energies[x - 1,y] else [x - 1, min(y + 1, y_len - 1)]
    return pixel_energies, backtrack

def carve_vertical(magnitude, new_shape , mask):
    tbs = []
    print(mask.shape[1] - new_shape[1])
    for _ in range(mask.shape[1] - new_shape[1]):
        Energy, backtrack = calc_energy(magnitude, mask)
        masked_tb, tb = traceback(E = Energy, prev_pointers = backtrack, mask=mask)
        tbs.append(tb)
        mask = remove_tb_from_mask(traceback=masked_tb, mask=mask)
    return mask, tbs


def visualise_seams(image, new_shape, visualize_scheme, colour, greyscale_wt):
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
    delete_tbs = []
    match visualize_scheme:
        case VisualizeScheme.VERTICAL:
            delete_tbs, *_ = get_seams(image, new_shape, CarvingScheme.VERTICAL_HORIZONTAL, colour_wts=greyscale_wt,concat=False)
        case VisualizeScheme.HORIZONTAL:
            delete_tbs, *_ = get_seams(image, new_shape, CarvingScheme.HORIZONTAL_VERTICAL, colour_wts=greyscale_wt,concat=False)
        case VisualizeScheme.BOTH:
            delete_tbs = get_seams(image, new_shape, CarvingScheme.VERTICAL_HORIZONTAL, colour_wts=greyscale_wt)
    return overwrite_tb_pixels(tbs=delete_tbs, image=image, colour=colour)

def get_seams(image, new_shape, carving_scheme, colour_wts, concat = True, mask = None):
    grad_magnitude = gradient_magnitude(image, colour_wts)
    tbs_vertical = []
    tbs_horizontal = []
    if mask is None:
        mask = generate_mask(grad_magnitude.shape[0], grad_magnitude.shape[1])
    match carving_scheme:
        case CarvingScheme.VERTICAL_HORIZONTAL:
            mask, tbs_vertical = carve_vertical(grad_magnitude, new_shape, mask)
            grad_magnitude_T = grad_magnitude.T
            mask_T = np.flip(np.transpose(mask, (1, 0, 2)), axis = 2)
            mask_T, tbs_horizontal_temp = carve_vertical(grad_magnitude_T, new_shape[::-1], mask_T)
            if tbs_horizontal_temp:
                tbs_horizontal = list(np.flip(tbs_horizontal_temp, axis = 2))
            mask = np.flip(np.transpose(mask_T, (1, 0, 2)), axis = 2)
        case CarvingScheme.HORIZONTAL_VERTICAL:
            mask_T = np.flip(np.transpose(mask, (1, 0, 2)), axis = 2)
            tbs_vertical_flipped, tbs_horizontal_flipped, mask_T = get_seams(
                np.transpose(image, (1, 0, 2)), new_shape[::-1], CarvingScheme.VERTICAL_HORIZONTAL, colour_wts, concat=False, mask=mask_T
            ) 
            mask = np.flip(np.transpose(mask_T, (1, 0, 2)), axis = 2)
            tbs_vertical = list(np.flip(tbs_vertical_flipped, axis = 2)) if tbs_vertical_flipped else []
            tbs_horizontal = list(np.flip(tbs_horizontal_flipped, axis = 2)) if tbs_horizontal_flipped else []
        case CarvingScheme.INTERMITTENT:
            for i in range(1, max(image.shape[0] - new_shape[0], image.shape[1] - new_shape[1]) + 1):
                new_x, new_y = min(new_shape[0], image.shape[0] - i), min(new_shape[0], image.shape[0] - i)
                tbs_vertical_temp , tbs_horizontal_temp, mask = get_seams(image, (new_x, new_y), carving_scheme, colour_wts, concat = False, mask = mask)
                tbs_vertical.extend(tbs_vertical_temp)
                tbs_horizontal.extend(tbs_horizontal_temp)
    if concat:
        tbs_vertical.extend(tbs_horizontal)
        return tbs_vertical
    else:
        return tbs_vertical, tbs_horizontal, mask

def overwrite_tb_pixels(image, tbs, colour = [0, 0, 0]):
    image_copy = image.copy()
    for tb in tbs:
        for index in tb:
            image_copy[index[0], index[1]] = colour
    return image_copy
    
def reshape_seam_carving(image, new_shape, carving_scheme, colour_wts):
    """
    Resizes an image to new shape using seam carving
    :param image: The original image
    :param new_shape: a (height, width) tuple which is the new shape
    :param carving_scheme: the carving scheme to be used.
    :returns: the image resized to new_shape
    """
    ###Your code here###
    ###**************###
    seams = get_seams(image, new_shape, carving_scheme, colour_wts )
    temp_mask = np.full(image.shape, True, dtype=bool)
    for tb in seams:
        for index in tb:
            temp_mask[index[0], index[1]] = [False, False, False]
    image = image[temp_mask].reshape((new_shape[0], new_shape[1], 3))
    return image
