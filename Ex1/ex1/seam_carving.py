import numpy as np
from enum import Enum

func_dx = lambda x : (np.c_[np.zeros(x.shape[0]), x] - np.c_[ x, np.zeros(x.shape[0])])[:,1:]
func_dy = lambda x : func_dx(x.T).T
func_gradient = lambda x : np.array([func_dx(x), func_dy(x)])
func_magnitude = lambda x : np.sqrt((x * x).sum(axis = 0))

def get_greyscale_image(image, colour_wts):
    """
    Gets an image and weights of each colour and returns the image in greyscale
    :param image: The original image
    :param colour_wts: the weights of each colour in rgb (ints > 0)
    :returns: the image in greyscale
    """
    greyscale_image = image @ colour_wts
    return np.uint8(greyscale_image)
    
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
    def scaled_color(color):
        color_dx = func_dx(color)
        x_lin = np.linspace(0, in_height - 1, num = out_width)
        int_x_lin = np.int64(x_lin)
        y_lin = np.linspace(0, in_width - 1 , num = out_height)
        int_y_lin = np.int64(y_lin)
        x_inter = color[int_x_lin]  - (x_lin - int_x_lin)[:, None] * color_dx[int_x_lin]    
        color_dy = func_dy(x_inter)
        y_inter = x_inter.T[int_y_lin] - (y_lin - int_y_lin)[:, None] * color_dy.T[int_y_lin]
        return np.uint8(y_inter.T)
    r_T, g_T, b_T = image.T
    colors = r_T.T, g_T.T, b_T.T
    new_image = np.array([scaled_color(color).T for color in colors])
    return new_image.T
    
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
    magnitude = func_magnitude(gradient)
    return magnitude

class CarvingScheme(Enum):
    VERTICAL_HORIZONTAL = 0
    HORIZONTAL_VERTICAL = 1
    INTERMITTENT = 2


def calc_energy(pixel_energies : np.array) ->  np.array:
    pixel_energies = np.int64(pixel_energies)
    previous_seam_energies_row = list(pixel_energies[0])
    history = [previous_seam_energies_row]
    y_length, x_length = pixel_energies
    for y in range(1, y_length):
        pixel_energies_row = pixel_energies[y]
        seam_energies_row = []
        for x, pixel_energy in enumerate(pixel_energies_row):
            x_range = {max(x - 1, 0), x,  min(x + 1, x_length - 1)}
            min_seam_energy = pixel_energy + \
                min(previous_seam_energies_row[x_i] for x_i in x_range)
            seam_energies_row.append(min_seam_energy)
        previous_seam_energies_row = seam_energies_row
        history.append(previous_seam_energies_row)
    return np.array(history)

  
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
            pass
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
