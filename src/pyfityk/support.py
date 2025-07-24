import numpy as np
import pandas as pd
import re
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
        array [x,y,active]

    """
    return np.array([[i.x,i.y, i.is_active] for i in data])

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

def get_coordinates(fityk, dataset):
    return np.array([(x.x, x.y, x.is_active) for x in fityk.get_data(dataset)]).T

def read_function_info(func):
    def list_params(f):
        l=[]
        i=0
        while x:=f.get_param(i):
            l.append(f.get_param_value(x))
            i+=1
        return l
    return func.get_template_name(),list_params(func)

def read_functions(session, dataset):
    """
    Read all the fuctions of a dataset in the session
    
    Input
    ------
    session: Fityk
        Fityk session
    dataset: int
        dataset index
    Return
    ------
    dict:
        dictionary with the function name as a key and
        the parameters as the value
    """
    return dict(read_function_info(func) for func in session.get_components(dataset))



def split_data_text(content):
    sections = re.split(r'(?=^use)', content, flags=re.IGNORECASE | re.MULTILINE)
    data = [
        [[float(x) for x in re.sub(r".\[[0-9]*\]=", "", s).split(",")] 
                for s in section.splitlines() if s.startswith("X[")]
        for section in sections[1:]
        ]
    # data = for a 
    return data
        
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
