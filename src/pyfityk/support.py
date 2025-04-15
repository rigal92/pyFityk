import numpy as np
import pandas as pd
import os 

def checkfolder(folder):
    """check if folder exists and returns absolut path"""
    path = os.path.abspath(folder)
    if not os.path.isdir(path):
        raise FileNotFoundError('No folder exists at the location specified')
    if not path.endswith("/"):
        path+="/"
    return path


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
        array of pairs [x,y]

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
    np.array
        y values calculated
    """
    return np.array([func.value_at(i) for i in x])

    
def to_eV(n):
    """Converts to eV for 532.1nm a dataset n"""
    return f"@{n}: X=1.239842e3/532.1 - 1.23984198e-04*x"

def convert_peaks(peaks):
    """
    converts a pandas DataFrame of peaks into a easier
    python formatting

    Input
    -----------------------------------------------
    peaks:pd.DataFrame
        the unformatted peaks as they are returned 
        from info peaks
    Returns
    -----------------------------------------------
    pandas.DataFrame:
        DataFrame containing the functions 
        identifier, name and parameters  

    """
    #split function name and id 
    peaks = pd.concat(
        [
            pd.DataFrame([x.split() for x in peaks.loc[:,"# PeakType"]], columns = ["fid","fname"]),
            peaks
        ], 
        axis=1)

    #split the parameters that are placed all together by Fityk and replace ? by 0 for unknown errors 
    errors = "+/-" in peaks.loc[:,"parameters..."][0]
    pars = pd.DataFrame([map(float,x.replace("+/-","").replace("?","0").split()) if isinstance(x, str) else x for x in peaks.loc[:,"parameters..."]])
    if(errors):
        pars.columns = [f"a{int(i/2)}" if (not i%2) else f"err_a{int(i/2)}" for i in range(len(pars.columns))]
    else:
        pars.columns = [f"a{i}" for i in range(len(pars.columns))]

    #adds the parameters 
    peaks = peaks.join(pars)

    #drop useless columns 
    peaks.drop(columns = ["# PeakType",'parameters...'],inplace = True)

    return peaks
