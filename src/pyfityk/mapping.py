from fityk import Fityk
from pyfityk.io import read_fityk_text
from pyfityk.support import get_define_functions, set_define_functions, deactivate_points, read_functions
from sklearn.metrics.pairwise import pairwise_distances_argmin
from scipy.stats import pearsonr
from scipy.signal import savgol_filter
import pandas as pd
import numpy as np


# -----------------------------------------------------------------
# Help functions
# -----------------------------------------------------------------

def match_template(data_y, template_data, metric="pearsonr", normalize=True, smooth=True, baseline=True):
    """
    Finds the spectrum in template_data that is most similar to each one in 
    data_y. Metric is the method used for the matching.

    Input
    ------
    data_y: np.array (n_spectra, spectrum_y)
        the spectra to be matched
    template_data: np.array (n_spectra, spectrum_y)
        the template spectra used for matching
    metric: str, default="euclidean"
        the metric used to calculate the distances.
        Possible values:
        - from manual implementation:
            ['pearsonr']

        - from scikit-learn: ['cityblock', 'cosine', 'euclidean', 'l1', 'l2',
         'manhattan', 'nan_euclidean']

        - from :mod:`scipy.spatial.distance`: ['braycurtis', 'canberra', 'chebyshev',
          'correlation', 'dice', 'hamming', 'jaccard', 'kulsinski',
          'mahalanobis', 'minkowski', 'rogerstanimoto', 'russellrao',
          'seuclidean', 'sokalmichener', 'sokalsneath', 'sqeuclidean',
          'yule']
    baseline: bool, default=True
        remove a costant baseline before computing the distance
    smooth: bool, default=True
        smooth data before computing the distance
    normalize: bool, default=True
        normalize the data before computing the distance
    Return
    ------
    numpy.array
        array of closest matches of template_data for each data_y
    """
    if baseline:
        template_data = np.array([s-s.min()for s in template_data])
        data_y = np.array([s-s.min()for s in data_y])
    if smooth:
        win = 50
        template_data = savgol_filter(template_data, window_length=win, polyorder=2, mode='interp')
        data_y = savgol_filter(data_y, window_length=win, polyorder=2, mode='interp')
    if normalize:
        template_data = np.array([s/s.max()for s in template_data])
        data_y = np.array([s/s.max()for s in data_y])

    #compute distance
    if metric == "pearsonr":
        return np.array([np.argmin([1 - pearsonr(y, ref)[0] for ref in template_data]) for y in data_y]) 
    else:
        return pairwise_distances_argmin(data_y, template_data, metric=metric)


def edit_filename(filename, obj, replace=False):
    """Edits filename. If replace==True **obj** will replace the extension.
    Else **ojb** is inserted before the extension"""
    if "." in filename:
        idx = filename.rfind(".")
        if replace:
            return filename[:idx] + obj
        else:
            return filename[:idx] + "_" + str(obj) + filename[idx:]
    else:
        if replace:
            return filename + "_" + str(obj)
        else:
            return filename + "_" + str(obj)
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

def fitMap(x, y_spectra, template, fileout="", verbosity=-1, split=0, fit=True, match_method="pearsonr", match_preprocess=False, fitting_method="mpfit", max_wssr_evaluations=100):
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
        model is added but not fitted. Usefull to check the template matching
    match_method: str, default="pearsonr"
        defines the method used for matching the spectra with the template
        Possible values:
        - from manual implementation:
            ['pearsonr']

        - from scikit-learn: ['cityblock', 'cosine', 'euclidean', 'l1', 'l2',
         'manhattan', 'nan_euclidean']

        - from :mod:`scipy.spatial.distance`: ['braycurtis', 'canberra', 'chebyshev',
          'correlation', 'dice', 'hamming', 'jaccard', 'kulsinski',
          'mahalanobis', 'minkowski', 'rogerstanimoto', 'russellrao',
          'seuclidean', 'sokalmichener', 'sokalsneath', 'sqeuclidean',
          'yule']
    match_preprocess: str|bool, default=False
        enable preprocessing of the data for matching
        Possible values:
        - False: No preprocessing
        - True: performs costant baseline subtraction, smoothing and normalization
        - str: the 'base', 'smooth' and 'norm' keywords can be used to toggle 
        the corresponging preprocess. For example: 'base norm' will perform
        baseline correction and normalization before performing the matching
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
    if match_preprocess:
        if match_preprocess == True:
            normalize=smooth=baseline=True
        else:
            normalize = "norm" in match_preprocess
            smooth = "smooth" in match_preprocess
            baseline = "base" in match_preprocess
    else:
        normalize=smooth=baseline=False
    template = read_fityk_text(template)
    template_y = np.array([d["data"]["y"] for d in template])

    templ_ids = match_template(y_spectra.T.values, template_y, metric=match_method, normalize=normalize, smooth=smooth, baseline=baseline)

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
        if (fileout!="") and split and ((i+1)%split == 0):
            fout = edit_filename(fileout, i+1)
            print("-"*10, "Saving file","-"*10, sep="\n")
            session.execute(f"info state > '{fout}'")
    if fileout!="":
        if split:
            fout = edit_filename(fileout, i)
            session.execute(f"info state > '{fout}'")
        else:
            session.execute(f"info state > '{fileout}'")

