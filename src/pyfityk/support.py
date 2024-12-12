import numpy as np

def points_to_arrays(data):
    """
    Returns a list of points from the data

    Input
    ------
    data
        fityk data
    Return
    ------
    np.array
        list of pairs [x,y]

    """
    return np.array([[i.x,i.y] for i in data])

def get_func_y(x, func):
    """
    Returns the values of the function calculated in the x values  
    -----------------------------------------------------------------
    Input
    ------
    x: array-like
        x values
    func: fityk function
        function
    
    Return
    ------
    list
        y values calculated


    """
    return [func.value_at(i) for i in x]