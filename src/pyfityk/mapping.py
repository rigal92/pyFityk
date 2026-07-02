from fityk import Fityk
from sklearn.metrics.pairwise import pairwise_distances_argmin
from scipy.stats import pearsonr
from scipy.signal import savgol_filter
import pandas as pd
import numpy as np
from pyfityk.io import get_functions, read_fityk_text
from pyfityk.support import *

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

def fitSpectrum(buffer_session, x, y, template, dataset=0, session=None, fit=True, to_array=False):
    """
    Fit a spectrum using a buffer session and adds is to another session.
    
    Inputs
    ------
    buffer_session: Fityk
    x,y: array like of floats
    template: dict
        a template element returned from pyfityk.io.read_fityk_text
    dataset: int
        index of the dataset. Ignored if to_array==True
    session: Fityk or None
        session on which to save the fit. If to_array this is ignored
    fit: bool, default=True
        flag used to enable/disable the spectra fit once the template is loaded
    to_array: bool, default=False
        returns an array with the parameters
    Returns
    -------
    pd.DataFrame:
        return the parameters of the functions fitted if to_array==True 
    """
    active = template["data"]["active"]
    model = template["model"]
    buffer_session.load_data(0, x, y, []) #dataset n, x, y, sigma
    deactivate_points(buffer_session, active, 0)
    if model != 0:
        buffer_session.execute("F="+model)
        if fit:
            is_fittable = "~" in model
            if is_fittable:
                buffer_session.execute(f"@0: fit")
            else:
                print("No fittable parameters.")
    if not to_array:
        funcs = read_functions(buffer_session, 0)
        deactivate_points(session, active, dataset)
        session.execute(f"@{dataset}.F=0") #reset functions
        for func in funcs.values():
            session.execute(f"@{dataset}.F+={func}")
    else:
        funcs = get_functions(buffer_session, 0)
        return funcs


def fitMap(x, y_spectra, template_file, fileout="", verbosity=-1, split=0, fit=True, match_method="sqeuclidean", match_preprocess=False, to_array=False):
    """
    Fit a batch of spectra. The initial conditions are obtained by matching
    the y_spectra to a template.

    Inputs
    ------
    x: array-like of float
        spectra x values
    y: pd.DataFrame
        data frame where each column is a spectrum
    template_file: str
        name of a Fityk file used as template for the initial model used
        for fitting the spectra
    fileout: string, default=""
        if different to "", fileout is used as a file name to save the results
        - a fityk file if to_array == False
        - a table with the parameters if to_array == True
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
    to_array: bool, default=False
        returns an array of all the parameters
    """

    if match_preprocess:
        if match_preprocess == True:
            normalize=smooth=baseline=True
        else:
            normalize = "norm" in match_preprocess
            smooth = "smooth" in match_preprocess
            baseline = "base" in match_preprocess
    else:
        normalize=smooth=baseline=False

    template = Fityk()
    template.execute(f"exec '{template_file}'")
    initials = get_session_initials(template)
    initials["sets"] = re.sub(r"set verbosity = (.*?);", f"set verbosity = {verbosity};", initials["sets"])

    #TODO: once read_fityk is properly implemented to read limits and constants merge it with the above part of defines 
    template = read_fityk_text(template_file)
    template_y = np.array([d["data"]["y"] for d in template])

    templ_ids = match_template(y_spectra.T.values, template_y, metric=match_method, normalize=normalize, smooth=smooth, baseline=baseline)
    session = Fityk()
    buffer_session = Fityk()

    #initial general sets for sessions 
    for f in [session, buffer_session]:
        set_define_functions(f, initials["defines"])
        f.execute(initials["sets"])

    if not pd.api.types.is_float_dtype(x):
        # fityk accepts only float arrays    
        x = x.astype(float)

    l = []

    for i, (templ_id, (coord, y)) in enumerate(zip(templ_ids, y_spectra.items())):
        if verbosity == -1:
            if i%500==0:
                print(f"-----Fitting @{i}")
        else:
            print(f"-----Fitting @{i}")

        if not pd.api.types.is_float_dtype(y):
        # fityk accepts only float arrays    
            y = y.astype(float)
        match = template[templ_id]
        title = ";".join(coord) + f";ID-{templ_id}"
        #Fityk creates an empty dataset at position 0. Do not create a new one for dataset 0
        if not to_array:
            dataset_idx = i%split if split else i
            if dataset_idx!=0: session.execute("@+ = 0")
            session.load_data(dataset_idx, x, y, [], title)
            fitSpectrum(buffer_session, x, y, match, session=session, dataset=dataset_idx, fit=fit)
            if (fileout!="") and split and ((i+1)%split == 0):
                fout = edit_filename(fileout, i+1)
                print("-"*10, "Saving file","-"*10, sep="\n")
                session.execute(f"info state > '{fout}'")
                session.execute("reset")
                set_define_functions(session, initials["defines"])
                session.execute(initials["sets"])
        else:
            funcs = fitSpectrum(buffer_session, x, y, match, fit=fit, to_array=True)
            idx = pd.MultiIndex.from_tuples([(coord[0], coord[1], templ_id) for _ in range(len(funcs))], names=("x","y","templateIDX"))
            funcs = funcs.set_index(idx)
            l.append(funcs)


    if not to_array:
        if fileout!="":
            if split:
                if len(templ_ids)%split!=0:
                    fout = edit_filename(fileout, i+1)
                    session.execute(f"info state > '{fout}'")
            else:
                session.execute(f"info state > '{fileout}'")
    else:
        return pd.concat(l)

