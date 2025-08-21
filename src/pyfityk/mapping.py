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

# def to_ev(x):
#     return 1.239842e3/532.1 - 1.23984198e-04*x


# def get_y(fityk, dataset):
#     return np.array([x.y for x in fityk.get_data(dataset)])

# def get_coordinates(fityk, dataset):
#     return np.array([(x.x, x.y, x.is_active) for x in fityk.get_data(dataset)]).T

# def read_function_info(func):
#     def list_params(f):
#         l=[]
#         i=0
#         while x:=f.get_param(i):
#             l.append(f.get_param_value(x))
#             i+=1
#         return l

#     return func.get_template_name(),list_params(func)

# def read_functions(session, dataset):
#     """
#     Read all the fuctions of a dataset in the session
    
#     Input
#     ------
#     session: Fityk
#         Fityk session
#     dataset: int
#         dataset index
#     Return
#     ------
#     dict:
#         dictionary with the function name as a key and
#         the parameters as the value
#     """
#     return dict(read_function_info(func) for func in session.get_components(dataset))

# -----------------------------------------------------------------
# Template reading and matching
# -----------------------------------------------------------------
# def read_fityk(filename):
#     """
#     Read file from Fityk to use as a template to initialize functions.
#     Input
#     ------
#     filename: str
#         name of the template file
#     Return
#     ------
#     tuple (dict, dict):
#         return functions and y for each dataset
#     """
#     f = Fityk()
#     f.execute(f"reset; exec '{filename}'")
#     funcs = np.array([read_functions(f,i) for i in range(f.get_dataset_count())])
#     data = np.array([get_coordinates(f,i) for i in range(f.get_dataset_count())])
#     return funcs, data

def match_template(data_y, template_data):
    dist = euclidean_distances(template_data, data_y)
    return dist.argmin(axis=0)

# -----------------------------------------------------------------
# Fitting
# -----------------------------------------------------------------

def fitSpectrum(session, buffer_session, x, y, template, dataset):
    buffer_session.load_data(0, x, y, []) #dataset n, x, y, sigma
    active = template["data"]["active"]
    model = template["model"]
    deactivate_points(buffer_session, active, 0)
    deactivate_points(session, active, dataset)
    buffer_session.execute("F="+model)
    try:
        buffer_session.execute(f"@0: fit")
    except:
        print("No fittable parameters.")
    funcs = read_functions(buffer_session, 0)
    session.execute(f"@{dataset}.F=0") #reset functions
    for func in funcs.values():
        session.execute(f"@{dataset}.F+={func}")

def fitMap(x, y_spectra, template, fileout="", verbosity=-1, split=0):
    def get_defines(template):
        f = Fityk()
        f.execute(f"exec '{template}'")
        defines = get_define_functions(f)
        return defines
    defines = get_defines(template)

    #TODO: once read_fityk is properly implemented merge it with the above parti of defines 
    template = read_fityk_text(template)
    template_y = np.array([d["data"]["y"] for d in template])
    templ_ids = match_template(y_spectra.T, template_y)

    session = Fityk()
    buffer_session = Fityk()

    for f in [session, buffer_session]:
        set_define_functions(f, defines)
        f.execute(f"set max_wssr_evaluations=100")
        f.execute(f"set verbosity={verbosity}")
        # f.execute("set fitting_method=mpfit")

    for i, (templ_id, (coord, y)) in enumerate(zip(templ_ids, y_spectra.items())):
        print(f"-----Fitting @{i}")
        match = template[templ_id]
        title = ";".join(coord)
        session.execute("@+ = 0")
        session.load_data(i, x, y, [], title)
        fitSpectrum(session, buffer_session, x, y, match, i)

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
