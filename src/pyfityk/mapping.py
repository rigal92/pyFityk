from fityk import Fityk
from pyfityk.io import read_fityk_text
from pyfityk.support import get_define_functions, set_define_functions, deactivate_points, read_functions
from sklearn.metrics.pairwise import euclidean_distances
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import re


# -----------------------------------------------------------------
# Help functions
# -----------------------------------------------------------------

def match_template(data_y, template_data):
    dist = euclidean_distances(template_data, data_y)
    return dist.argmin(axis=0)

# -----------------------------------------------------------------
# Fitting
# -----------------------------------------------------------------

def fitSpectrum(session, buffer_session, x, y, template, dataset, fit=True):
    """
    Fit a spectrum using a buffer session and adds is to another session.
    
    Inputs
    ------
    session: Fityk
    buffer_session: Fityk
    x,y: array like of floats
    template: dict
        a template element returned from pyfityk.io.read_fityk
    dataset: int
        index of the dataset
    fit: bool, default=True
        flag used to enable/disable the spectra fit once the template is loaded
    """
    buffer_session.load_data(0, x, y, []) #dataset n, x, y, sigma
    active = template["data"]["active"]
    model = template["model"]
    deactivate_points(buffer_session, active, 0)
    deactivate_points(session, active, dataset)
    buffer_session.execute("F="+model)
    if fit:
        try:
            buffer_session.execute(f"@0: fit")
        except:
            print("No fittable parameters.")
    funcs = read_functions(buffer_session, 0)
    session.execute(f"@{dataset}.F=0") #reset functions
    for func in funcs.values():
        session.execute(f"@{dataset}.F+={func}")

def fitMap(x, y_spectra, template, fileout="", verbosity=-1, split=0, fit=True, fitting_method="mpfit", max_wssr_evaluations=100):
    """
    Fit a batch of spectra. The initial conditions are obtained by matching
    the y_spectra to a template.

    Inputs
    ------
    x: array-like of float
        spectra x values
    y: pd.DataFrame
        data frame where each column is a spectrum
    template: string
        name of a .fit Fityk file used as template for the initial model used
        for fitting the spectra
    fileout: string, default=""
        if different to "", fileout is used as a file name to save the settions
    verbosity: int, default=-1
        value passed to Fityk to set the verbosity of the Fityk output.
        Possible values: -1 (silent), 0 (normal), 1 (verbose), 2 (very verbose)
    split: int, default=0
        if fileout is not empty and **split** is not 0, split the output in 
        subfiles. Each subfile will contain **split** number of datasets.
    fit: bool, default=True
        toggles the fitting of the spectra. If False, the template initial
        model is added but not fitted.
    fitting_method: str, default=mpfit
        sets the fitting method. 
        Accepted values: 
            levenberg_marquardt, mpfit, nelder_mead_simplex, genetic_algorithms,
            nlopt_nm, nlopt_lbfgs, nlopt_var2, nlopt_praxis, nlopt_bobyqa, 
            nlopt_sbplx.
    max_wssr_evaluations: int, default=100
        the maximum number of evaluations of the objective function (WSSR)
        0=unlimited    
    """
    def get_defines(template):
        f = Fityk()
        f.execute(f"exec '{template}'")
        defines = get_define_functions(f)
        return defines
    defines = get_defines(template)

    #TODO: once read_fityk is properly implemented merge it with the above part of defines 
    template = read_fityk_text(template)
    template_y = np.array([d["data"]["y"] for d in template])
    templ_ids = match_template(y_spectra.T, template_y)

    session = Fityk()
    buffer_session = Fityk()

    #initial general sets for 
    for f in [session, buffer_session]:
        set_define_functions(f, defines)
        f.execute(f"set max_wssr_evaluations={max_wssr_evaluations}")
        f.execute(f"set verbosity={verbosity}")
        f.execute(f"set fitting_method={fitting_method}")

    for i, (templ_id, (coord, y)) in enumerate(zip(templ_ids, y_spectra.items())):
        print(f"-----Fitting @{i}")
        match = template[templ_id]
        title = ";".join(coord) + f";K-{templ_id}"
        if i!=0: session.execute("@+ = 0")
        session.load_data(i, x, y, [], title)
        fitSpectrum(session, buffer_session, x, y, match, i, fit)
        if (fileout!="") and split and (i%split == 0):
            if "."in fileout:
                idx = fileout.rfind(".")
                fout = fileout[:idx] + "_" + str(i) + fileout[idx:]
            else:
                fout = fileout + "_" + str(i)
            print("-"*10, "Saving file","-"*10, sep="\n")
            session.execute(f"info state > '{fout}'")
    if fileout!="":
        if split:
            fout = fileout + "_" + str(i)
            session.execute(f"info state > '{fout}'")
        else:
            session.execute(f"info state > '{fileout}'")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser("")
    parser.add_argument("file", help="file .fit containing the data")
    parser.add_argument("--raman", action="store_true", help="fit raman files")
    parser.add_argument("--template", action="store", help="template file to get spectra kinds")
    
    parser.add_argument("--PL", action="store_true", help="fit PL files")

    args = parser.parse_args()

    file = args.file
    template = args.template

    f = Fityk()
    if(args.PL):
        fitMap(file, template, save=True)
    if(args.raman):
        fitMap(file, template, "Raman", save=True, const_functions ="")
