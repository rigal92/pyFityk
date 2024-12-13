from fityk import Fityk, ExecuteError 
import pandas as pd
import numpy as np
from os.path import isfile
from .support import points_to_arrays, get_func_y, checkfolder


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

def read_map(file, style = "jasko"):
    """
    Read a mapping file uploading spectra in fityk.
    -----------------------------------------------------------------
    file: str
        name of the file 
    style: str, default="jasko"
        identify the formatting style of the mapping file
        Accepted values:
            - "jasko"



    """
    fk = Fityk()
    if style == "jasko":
        with open(file) as f:
            _ = [next(f) for i in range(13)]
            xmap = map(float,next(f).split("\t")[1:]) 
            ymap = map(float,next(f).split("\t")[1:]) 

        for i,(x,y) in enumerate(zip(xmap,ymap)):
            s = f"@+ < '{file}:1:{i+2}::'"
            fk.execute(s)
            # rename dataset using positions
            s = f"@{(fk.get_dataset_count()-1)}: title = '{x}:{y}'"
            fk.execute(s)
    else:
        raise ValueError(f"Style {style} not recognized.")
        
    save_session(fk,file)

