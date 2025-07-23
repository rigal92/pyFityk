from fityk import Fityk, ExecuteError 
import pandas as pd
import numpy as np
from os.path import isfile
from io import StringIO
from .support import points_to_arrays, get_func_y, checkfolder, convert_peaks

def get_data(session, dataset):
    """
    Export data
    -----------------------------------------------------------------
    Inputs
    ------
    session
        fityk object
    dataset: int
        dataset number
    Return
    ------
    pd.DataFrame:
        pandas Dataframe with x,y,f0..fn,ftot columns
    """
    xy = pd.DataFrame(points_to_arrays(session.get_data(dataset)), columns=["x","y","active"])
    x = xy["x"]
    funcs = np.array([get_func_y(x,f) for f in session.get_components(dataset)])
    if len(funcs)>0:
        df = pd.concat([xy, pd.DataFrame(funcs.T, columns=[f"f{i}" for i in range(funcs.shape[0])])], axis=1)
        df["ftot"] = funcs.sum(axis=0)
        return df
    else:
        return xy
def get_functions(session, dataset):
    """
    Extract dataset peaks
    -----------------------------------------------------------------
    Inputs
    ------
    session
        fityk object
    dataset: int
        dataset number
    Return
    ------
    pd.DataFrame
        functions table. Functions errors are included if possible.
        An empty table is returned if there are no functions for 
        the dataset. 
    """
    if len(session.get_components(dataset))==0:
        return pd.DataFrame()
    # try:
        # funcs = pd.read_table(StringIO(session.get_info("peaks_err",dataset)))
    # except ExecuteError as e:
    if True:
        funcs = pd.read_table(StringIO(session.get_info("peaks",dataset)))
    funcs = convert_peaks(funcs)
    return funcs

def read_function_info(func):

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
    std_pars = ["Center", "Height", "Area", "FWHM"]
    df = pd.DataFrame(read_function_info(func) for func in session.get_components(dataset))
    df.columns = ["fid", "fname"] + std_pars + [f"a{n}" for n in range(len(df.columns)-6)] 
    return df
    # return [read_function_info(func) for func in session.get_components(dataset)]



def export_data(session, outfolder):
    """
    Export data
    -----------------------------------------------------------------
    Inputs
    ------
    session
        fityk object
    outfolder: string
        output folder
    """
    outfolder = checkfolder(outfolder)
    f = session
    for i in range(f.get_dataset_count()):
        funcs=f.get_components(i)
        s_func = "".join([f"F[{n}](x), " for n in range(len(funcs))])
        title = f.get_info("title",i)
        s = f"@{i}: print all:x ,y, {s_func} F(x) >'{outfolder}{title}.dat'"
        f.execute(s)

def export_peaks(session, outfolder, errors = False):
    """
    Export peaks    -----------------------------------------------------------------
    Inputs
    ------
    session
        fityk object
    outfolder: string
        output folder
    errors:
        flag to export or not the parameter errors
    """
    outfolder = checkfolder(outfolder)
    f = session
    for i in range(f.get_dataset_count()):
        funcs=f.get_components(i)
        if len(funcs)==0:
            continue
        title = f.get_info("title",i)
        command = "peaks_err" if errors else "peaks"
        s = f"@{i}: info {command} >'{outfolder}{title}.peaks'"
        try:
            f.execute(s)
        except ExecuteError as e:
            s = e.__str__()
            if s == "No parametrized functions are used in the model.":
                print(f"WARNING! No parametrized functions are used in the model for dataset @{i}. Exporting peaks without errors.")
                s = f"@{i}: info peaks >'{outfolder}{title}.peaks'"
                f.execute(s)

    def read_peaks(filename):
        """
        Reads a .peak fityk file and formats

        Input
        -----------------------------------------------
        filename:str
            file containg the fit results
        Returns
        -----------------------------------------------
        pandas.DataFrame:
            DataFrame containing the functions 
            identifier, name and parameters  
        """
        #x is used for the quantities that do not have clearly defined one of the standard parameters (Center,Height...). They will be replaced by NaN
        return convert_peaks(pd.read_table(filename,na_values = "x"))


def save_session(session, filename):
    """Save session after checking if filename exists"""
    filename = ".".join(filename.split(".")[:-1]) + ".fit"
    while(isfile(filename)):    
        print(f"{filename} already exists, replace it? (y)/n")
        if(input()=="n"):
            print(f"Type new file name or c to cancel?")
            if((filename:=input())=="c"):
                print("WARNING! Session not saved.")
                return
        else:
            break
    session.execute("info state >'%s'" % filename)

def read_map(file, style = "jasko", split=250):
    """
    Read a mapping file uploading spectra in fityk.
    -----------------------------------------------------------------
    file: str
        name of the file 
    style: str, default="jasko"
        identify the formatting style of the mapping file
        Accepted values:
            - "jasko"
    split: int, default=250
        split files in *split* spectra files in order to reduce fitting 
        time



    """
    fk = Fityk()
    if style == "jasko":
        with open(file) as f:
            _ = [next(f) for i in range(13)]
            xmap = list(map(float,next(f).split("\t")[1:]) )
            ymap = list(map(float,next(f).split("\t")[1:]) )
            points = len(xmap)
        for i,(x,y) in enumerate(zip(xmap,ymap)):
            s = f"@+ < '{file}:1:{i+2}::'"
            fk.execute(s)
            # rename dataset using positions
            s = f"@{(fk.get_dataset_count()-1)}: title = '{x}:{y}'"
            fk.execute(s)
            if split and (((((i+1)%split) == 0) and i!=0) or i==(points-1)):
                if "." in file:
                    pos = file.rfind(".")
                    fname = file[:pos] + f"_{i+1}" + file[pos:]
                else:
                    fname = file + f"_{i}"
                save_session(fk,fname)
                fk.execute("reset")
    else:
        raise ValueError(f"Style {style} not recognized.")
        
    if not split:
        save_session(fk,file)

