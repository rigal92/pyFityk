from fityk import Fityk
# from pyfityk.support import to_eV
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

def initialize_function(name, parameters, dataset_id, const_functions=""):
    if const_functions:
        constant = True if re.match(const_functions, name) else False
    else:
        constant = False
    const = "" if constant else "~"
    pars = ",".join([const+str(i) for i in parameters]).rstrip(",")
    return f"@{dataset_id}.F += {name}({pars})"

# -----------------------------------------------------------------
# Fitting
# -----------------------------------------------------------------

def fitSpectrum(buffer_session, x, y, active, templ_function, const_functions="Constant|Linear|Bg"):
    buffer_session.execute("reset")
    buffer_session.execute(f"set max_wssr_evaluations=100")
    define_fitting_functions(buffer_session)    
    buffer_session.load_data(0, x, y, []) #dataset n, x, y, sigma
    deactivate_points(buffer_session, active, 0)

    for key, pars in read_functions(session, dataset).items():
        buffer_session.execute(initialize_function(key, pars, 0, const_functions))
    try:
        buffer_session.execute(f"@0: fit")
    except:
        print("Unparametrized functions. Skipping")
    session.execute(f"@{dataset}.F=0") #reset functions
    for key, pars in read_functions(buffer_session, 0).items():
        session.execute(initialize_function(key, pars, dataset, const_functions))


def fitMap(file, template, save=False, const_functions="Constant|Linear|Bg"):
# def fitMap(file, template, session, measurement, save=False, const_functions="Constant|Linear|Bg"):

    df = pd.read_table(file, skiprows=13, header=[0,1])
    templ_function, templ_data = read_fityk(template)
    fout = file.replace(".fit", "_fitted.fit")
    # define_fitting_functions(session)
    templ_ids = match_template(df.values.T[1:], templ_data[:,1,:])
    # print(templ_function)

    session = Fityk()
    buffer_session = Fityk()
    x = templ_data[:,0,:]

    # plt.imshow(templ_ids.reshape(50,50))
    # plt.show()


    for i, (templ_id, (coord, y)) in enumerate(zip(templ_ids, df.items())):
        # pass
        print(f"-----Fitting @{i}")
        # if measurement == "PL":
            # session.execute(to_eV(i))
        initials = templ_function[templ_id]
        active = templ_data[templ_id,2,:]
        fitSpectrum(session, buffer_session, x,y,  const_functions)

        # template
    #     session.execute(f"@{i}: title = '" + session.get_info("title",i) + f"_{template_id:02}'")
        deactivate_points(session, templ_data[template_id][2], i)

    #     # set initials
    #     for name, pars in initials.items():
    #         session.execute(initialize_function(name, pars, i, const_functions))


    #     if i%200==0:
    #         print("-"*10, "Saving temp file","-"*10, sep="\n")
    #         session.execute(f"info state > '{fout}temp'")

    # if save:
    #     session.execute(f"info state > '{fout}'")

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
