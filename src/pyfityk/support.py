import numpy as np
import pandas as pd
import re
import os
   
def to_eV(n, wl=532.1):
    """
    Returns a string to convert to eV for a laser of wavelength 
    **wl** a dataset **n**.
    """
    return f"@{n}: X=1.239842e3/{wl} - 1.23984198e-04*x"

def checkfolder(folder):
    """check if folder exists and returns absolut path"""
    path = os.path.abspath(folder)
    if not os.path.isdir(path):
        raise FileNotFoundError('No folder exists at the location specified')
    if not path.endswith("/"):
        path+="/"
    return path

# -----------------------------------------------------------------
# Get data and functions from Fityk session
# -----------------------------------------------------------------

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

def read_function_pars(func):
    """
    Read the function parameters

    Input
    ------
    func: Fityk function
    Return
    ------
    list,
        list of parameters in the format:
        func ID, func name, Center, Height, Area, FWHM, a0...an
        If the function does not have either one of the Center, Height, Area, 
        FWHM parameters that is replaced by a NaN value

    """
    l=[]
    l.append("%" + func.name)
    l.append(func.get_template_name())

    std_pars = ["Center", "Height", "Area", "FWHM"]
    for i in std_pars:
        try:
            l.append(func.get_param_value(i))
        except:
            l.append(np.nan)
    i=0
    while x:=func.get_param(i):
        l.append(func.get_param_value(x))
        i+=1
    return l

def convert_peaks(peaks):
    """
    Converts the output of info peaks in a DataFrame

    Input
    -----------------------------------------------
    peaks: string
        the unformatted peaks as they are returned 
        from info peaks
    Returns
    -----------------------------------------------
    pandas.DataFrame:
        DataFrame containing the functions 
        identifier, name and parameters

    """
    errors = "+/-" in peaks #check if errors are present
    peaks = peaks.strip() #trailing spaces 
    peaks = peaks.replace("+/-","")
    peaks = peaks.replace("?","0")
    peaks = pd.DataFrame([re.split("\s+",s)for s in peaks.split("\n")[1:]]) #split the lines, then columns
    peaks = peaks.replace("x",None)
    peaks.loc[:,2:] = peaks.loc[:,2:].astype(float)

    if(errors):
        pars_cols = [f"a{int(i/2)}" if (not i%2) else f"err_a{int(i/2)}" for i in range(len(peaks.columns)-6)]
    else:
        pars_cols = [f"a{i}" for i in range(len(peaks.columns)-6)]
    peaks.columns = ["fid", "fname", "Center", "Height", "Area", "FWHM"] + pars_cols
    return peaks

# -----------------------------------------------------------------
# Split fityk sections when reading as a fityk as text (NOT IN USE) 
# -----------------------------------------------------------------

def split_data_text(content):
    """
    Split the data part when reading a .fit file as text.

    Input
    ------
    content: str
        text containing the data
    Return
    ------
    list of pd.DataFrame
        each element is a pd.DataFrame containing the data

    """
    sections = re.sub(r".\[[0-9]*\]=", "", content)
    sections = sections.strip().split("\n\n")
    data = [
        pd.DataFrame(
            [
            [float(x) for x in s.split(",")]for s in section.splitlines()[5:]], columns = ["x","y","sigma","active"])
            for section in sections[1:]
            ]
    return data

def split_func_text(content):
    """
    Split the function part when reading a .fit file as text.

    Input
    ------
    content: str
        text containing the data
    Return
    ------
    tuple of dict
        (parameters,functions) tuple. Both are dicts with
        the parameter/function name as key and their value.
        If there are no parameters, it return a tuple of two 
        empty dictionaries.
    """

    s = content.split("\n\n")
    par, func = s[0], s[1]

    if(par == "# ------------  variables and functions  ------------"):
        return {}, {}
    
    #edit par
    par = re.sub(r"( \[[0-9]*:[0-9]*\])|(~)", "", par)
    par = dict([x.split(" = ") for x in par.split("\n")[1:]])
    par = {lab:float(val) for lab, val in par.items()}
    
    #edit func
    func = dict([x.split(" = ") for x in func.split("\n")])

    return par, func

def split_model_text(content, models, pars, funcs):
    """
    Split the model part when reading a .fit file as text.

    Input
    ------
    content: str
        text containing the data
    Return
    ------
    list of pd.DataFrame:
        list of DataFrame containing the functions
        identifier, name and parameters 
    """
    def format_line(fid):
        func = funcs[fid]
        fname, par = func.split("(")
        par = par.rstrip(")").split(", ")
        return [fid, fname] + [pars[p] for p in par]

    s = content.split("\n\n")
    s = s[0].split("\n")[1:]
    for l in s:
        index = int(l[1:l.find(":")])
        fids = l.split(" = ")[1].split(" + ")
        lines = [format_line(fid) for fid in fids]
        df = pd.DataFrame(lines)
        df.columns = columns = ["fid","fname"] + [f"a{i}"for i in range(len(df.columns)-2)]
        models[index] = df
    return models

# -----------------------------------------------------------------
# Functions defines
# -----------------------------------------------------------------

def get_define_functions(session):
    """
    Get all the define funtions in the Fityk **session**
    Returns a dictionary {function name:function definition}

    """
    def count_equals(s):
        """When constants are inserted as logs, exps ecc. sometimes
        fityk calculates its value and shows it in get_info.
        In this cas the outpus is formed by two equal signes with the
        same formula. Taking here just the first version of the formula."""
        # counting ' = ' instead of '=' as the latter is used for paramters defs
        if s.count(" = ")>1:
            s = " = ".join(s.split(" = ")[:2])
        return s

    functions_defs = session.get_info("types").split()
    functions_defs = {f:count_equals(session.get_info(f))for f in functions_defs}
    return functions_defs

def set_define_functions(session, functions):
    """
    Defines new functions in a session.

    Input
    ------
    session: Fityk
        Fityk session
    functions: dict
        dictionary containing the functions in the form 
        {function name:function definition acceptable in Fityk}
        Example:
            'Gaussian': 'Gaussian(height, center, hwhm) = height*exp(-ln(2)*((x-center)/hwhm)^2)'
    """
    present_functions = session.get_info("types")
    for key,f in functions.items():
        if key not in present_functions:
            session.execute("define " + f)

# -----------------------------------------------------------------
# Edit Fityk session
# -----------------------------------------------------------------

def deactivate_points(session, active, dataset):
    """
    Activate, deactivate points
    
    Inputs
    ------
    session: Fityk
        Fityk session
    active: array(bool)
        bolean array for each point of the data
    dataset: int
        dataset index

    """
    for i,val in enumerate(active):
        t = "true" if val else "false"
        session.execute(f"@{dataset}:A[{i}]={t}")


