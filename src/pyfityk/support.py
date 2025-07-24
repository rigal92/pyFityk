import numpy as np
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

    
def to_eV(n, laser_wl=532.1):
    """Converts to eV for a laser wavelength in nm and a dataset n"""
    return f"@{n}: X=1.239842e3/{laser_wl} - 1.23984198e-04*x"

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


