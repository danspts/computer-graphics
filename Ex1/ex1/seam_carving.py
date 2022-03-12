import numpy as np
from enum import Enum
from numba import jit, njit, vectorize, prange
import numba as nb
from numba.pycc import CC

def func_dx(x):
    match len(x.shape):
        case 2:
            return np.hstack((x[:,1:], np.zeros((x.shape[0], 1)))) - x
        case 3:
            return np.hstack((x[:,1:,:], np.zeros((x.shape[0], 1, x.shape[2])))) - x

def func_dy(x):
    match len(x.shape):
        case 2:
            return np.vstack((x[1:,:], np.zeros((1,x.shape[1])))) - x
        case 3:
            return np.vstack((x[1:,:,:], np.zeros((1,x.shape[1],x.shape[2])))) - x

def func_gradient(x) : return func_dx(x), func_dy(x)

def func_magnitude(gradient) : return np.sqrt(gradient[0] * gradient[0] + gradient[1] * gradient[1])

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

    color_dx = func_dx(image)
    x_lin = np.linspace(0, in_height - 1, num = out_width + 1) # the last row and column ae deleted so we adjust by 1
    int_x_lin = np.int64(x_lin)
    y_lin = np.linspace(0, in_width - 1 , num = out_height + 1)
    int_y_lin = np.int64(y_lin)
    x_inter = image[int_x_lin]  + (x_lin - int_x_lin)[:, None,:] * color_dx[int_x_lin]    
    color_dy = func_dy(x_inter)
    y_inter = x_inter[:,int_y_lin] + (y_lin - int_y_lin)[:, None,:] * color_dy[:,int_y_lin]
    return np.uint8(y_inter[:-1,:-1])

    
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
def calc_energy(image):
    pixel_energies = np.zeros(image.shape, dtype=np.int64)
    x_len, y_len = image.shape
    for x in range(x_len):
        for y in range(y_len):
            y_range = np.array([max(y - 1, 0), y,  min(y + 1, x_len - 1)])
            pixel_energies[x, y] = image[x, y] + np.min(pixel_energies[x - 1][y_range])
    return pixel_energies

  
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
            return visualise_seams(image.T, new_shape.T, CarvingScheme.VERTICAL_HORIZONTAL, colour).T
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
