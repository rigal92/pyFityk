from fityk import Fityk, ExecuteError 
import pandas as pd
import numpy as np
from os.path import isfile
from .support import *
import re


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

def read_dataset(session, dataset):
    """
    Read data and functions from a Fityk session and convert it to a python-like structure
    Input
    ------
    session: Fityk
        Fityk session
    dataset: int
        dataset id
    Return
    ------
    tuple (dict, dict):
        return functions and y for each dataset
    """
    funcs = read_functions(session, dataset) 
    # data = get_coordinates(session, dataset)
    return funcs, data

def read_fityk(filename):
    """
    Read Fityk file and convert it to a python-like structure
    Input
    ------
    filename: str
        name of the template file
    Return
    ------
    tuple (dict, dict):
        return functions and y for each dataset
    """
    f = Fityk()
    f.execute(f"reset; exec '{filename}'")
    funcs = np.array([read_functions(f,i) for i in range(f.get_dataset_count())])
    data = np.array([get_coordinates(f,i) for i in range(f.get_dataset_count())])
    return funcs, data

def read_fityk_text(filename):
    """
    Read Fityk file and convert it to a python-like structure
    Input
    ------
    filename: str
        name of the template file
    Return
    ------
    tuple (dict, dict):
        return functions and y for each dataset
    """
    with open(filename) as f:
        content = f.read()
    sections = re.split(r'(?=^# ------------)', content, flags=re.IGNORECASE | re.MULTILINE)

    data = None
    funcs = None

    for sec in sections:
        if sec.startswith("# ------------  datasets ------------"):
            data = split_data_text(sec)

    return data


    # funcs = np.array([read_functions(f,i) for i in range(f.get_dataset_count())])
    # data = np.array([get_coordinates(f,i) for i in range(f.get_dataset_count())])
    # return funcs, data

def read_fityk_bis(filename):
    """
    Read Fityk file and convert it to a python-like structure
    Input
    ------
    filename: str
        name of the template file
    Return
    ------
    tuple (dict, dict):
        return functions and y for each dataset
    """
    f = Fityk()
    f.execute(f"reset; exec '{filename}'")
    data = [read_dataset(f,i) for i in range(f.get_dataset_count())]
    return data
