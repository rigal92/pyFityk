from fityk import Fityk, ExecuteError 
import pandas as pd
import numpy as np
from os.path import isfile
from .support import *
import re


# -----------------------------------------------------------------
# Read from fityk session
# -----------------------------------------------------------------

def get_data(session, dataset):
    """
    Get data from a session
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

def get_functions_DEP(session, dataset):
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


def get_functions(session, dataset):
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
    df = pd.DataFrame(read_function_pars(func) for func in session.get_components(dataset))
    if not df.empty:
        df.columns = ["fid", "fname"] + std_pars + [f"a{n}" for n in range(len(df.columns)-6)] 
    else:
        return None
    return df


def read_fityk(session):
    """
    Read Fityk file and convert it to a python-like structure
    Input
    ------
    session: str or Fityk session
        if the file is a string it opens a session with that filename
        else it uses the Fityk session passed 
    Return
    ------
    list of dict:
        Each element of the list is a dictionary containing:
        - title
        - model (fityk like model) !!!NOT IMPLEMENTED returns None!!! 
        - model_formula (general formula for the model)
        - functions (a pd.DataFrame with the functions parameters)
        - data (a pd.DataFrame with the data)
    """
    if isinstance(session, str):
        f = Fityk()
        f.execute(f"reset; exec '{session}'")
    else:
        f = session
    # title = [f.get_info("title",i) for i in range(f.get_dataset_count())]
    # funcs = [get_functions(f,i) for i in range(f.get_dataset_count())]
    # data = [get_data(f,i) for i in range(f.get_dataset_count())]
    return [
        {
            "title":f.get_info("title",i),
            "model":None,
            "model_formula":f.get_info("gnuplot_formula",i),
            "functions":get_functions(f,i),
            "data":get_data(f,i),
        }
        for i in range(f.get_dataset_count())
    ]
    # title, data, funcs

def read_fityk_text(filename, errors=True):
    """
    Read Fityk file and convert it to a python-like structure.
    It is advisable to use instead of read_fityk.
    Input
    ------
    filename: str
        name of the file
    Return
    ------
    list of dict:
        Each element of the list is a dictionary containing:
        - title
        - model (fityk like model)
        - model_formula (general formula for the model)
        - functions (a pd.DataFrame with the functions parameters)
        - data (a pd.DataFrame with the data)
    """

    def substitute_with_dict(text, pattern, replacements):
        """
        Replace matches of a pattern in the text with values from a replacements dictionary.
        """
        def replacer(match):
            key = match.group(0)
            return replacements.get(key, key)
        return re.sub(pattern, replacer, text)

    with open(filename) as f:
        content = f.read()
    sections = re.split(r'(?=^# ------------)', content, flags=re.IGNORECASE | re.MULTILINE)

    f = Fityk()
    f.execute("set verbosity = -1") 
    f.execute("set numeric_format = '%f'") 
    
    #read sections
    for sec in sections:
        if sec.startswith("# ------------  (un)defines  ------------"):
            defines = sec
            for d in [d for d in defines.split("\n")]:
                f.execute(d)

        if sec.startswith("# ------------  datasets ------------"):
            data = sec.split("\n")

        if sec.startswith("# ------------  variables and functions  ------------"):
            s = sec.split("\n\n")
            par, funcs = s[0], s[1]

            #edit par
            par = dict([x.split(" = ") for x in par.split("\n")[1:]])

            # edit func
            funcs = funcs.strip()
            if(funcs==""):
                funcs = {}
                models = {}
                break             
            else:
                funcs = substitute_with_dict(funcs, r"\$_[0-9]*", par) #replace parameters with their values
                funcs = dict([x.split(" = ") for x in funcs.split("\n")])

        if sec.startswith("# ------------  models  ------------"):
            sec = substitute_with_dict(sec, r"%_[0-9]*", funcs) #replace functions with their values
            sec = sec.split("\n\n")[0].split("\n")[1:]
            models = {int(l[1:l.find(":")]): l.split(" = ")[1] for l in sec}

    for line in data:
        f.execute(line)

    dfs = []
    for i in range((f.get_dataset_count())):
        d = dict()
        d["title"] = f.get_info("title",i)
        if i in models:
            model = models[i]
            f.execute(f"@{i}:F ={model}")
            if errors:
                try:
                    peaks = f.get_info("peaks_err",i)
                except:
                    peaks = f.get_info("peaks",i)
            else:
                    peaks = f.get_info("peaks",i)
            peaks = convert_peaks(peaks)
            d["model"] = model
            d["model_formula"] = f.get_info("gnuplot_formula",i)
            d["functions"] = peaks
        else:
            d["model"] = 0
            d["model_formula"] = 0
            d["functions"] = None
        d["data"] = get_data(f,i)
        f.execute(f"@{i}:F=0")
        dfs.append(d)
    return dfs

# -----------------------------------------------------------------
# Read from text files
# -----------------------------------------------------------------

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
    with open(filename) as f:
        peaks = f.read()
    return convert_peaks(peaks)


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

#-----------------------------------------------------------------
# Save and export
#-----------------------------------------------------------------

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

