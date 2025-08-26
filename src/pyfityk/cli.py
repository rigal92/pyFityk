import argparse
doc_methods = """
Possible values:
    default="pearsonr"
    - from manual implementation:
        ['pearsonr']

    - from scikit-learn: ['cityblock', 'cosine', 'euclidean', 'l1', 'l2',
     'manhattan', 'nan_euclidean']

    - from :mod:`scipy.spatial.distance`: ['braycurtis', 'canberra', 'chebyshev',
      'correlation', 'dice', 'hamming', 'jaccard', 'kulsinski',
      'mahalanobis', 'minkowski', 'rogerstanimoto', 'russellrao',
      'seuclidean', 'sokalmichener', 'sokalsneath', 'sqeuclidean',
      'yule']
"""

def exporter(argv=None):
    from pyfityk import io
    from fityk import Fityk
    import os
    parser = argparse.ArgumentParser("")
    parser.add_argument("file")
    parser.add_argument("-o", dest="output", nargs="?", default="", help="output folder. If nothing is passed the *file* containing folder is used")
    parser.add_argument("--errors", dest="errors", action="store_true", help="flag to enable the export of the peaks' parameters errors")
    parser.add_argument("--data-only", dest="do", action="store_true", help="export only data")
    parser.add_argument("--peaks-only", dest="po", action="store_true", help="export peaks data")
    args = parser.parse_args(argv)
    file = args.file

    output = args.output
    if output == "":
        output = os.path.dirname(file)

    f = Fityk()
    f.execute(f"exec '{file}'")
    if not args.po:
        io.export_data(f, output)
    if not args.do:
        io.export_peaks(f, output, args.errors)
    return 0

def mapping(argv=None):
    import pandas as pd
    from pyfityk.mapping import edit_filename, fitMap
    parser = argparse.ArgumentParser("")
    parser.add_argument("file", help="file containing the data")
    parser.add_argument("template", help="template file to get spectra kinds")
    parser.add_argument("--out", default="", help="template file to get spectra kinds")
    parser.add_argument("--style", default="jasko", help="Style of the input file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output from Fityk")
    parser.add_argument("--match_preprocess", default="", help="Add data preprocessing for the spectra template matching. Possible inputs are b=baseline subtracrtion, n=normalize, s=smooth, a=all.")
    parser.add_argument("--match_method", default="pearsonr", help="Method used for matching the template.\n"+doc_methods)
    parser.add_argument("--split", type=int, default=0, help="Splits the output file")
    parser.add_argument("--nofit", action="store_false", help="Set up but does not perform fit")

    args = parser.parse_args(argv)
    
    out = args.out
    style = args.style
    preprocess = args.match_preprocess
    verbose = "0" if args.verbose else "-1"

    accepted_styles = ["jasko"]
    if style not in accepted_styles:
        parser.error("Unknown style.")        
    elif args.style=="jasko":
        data = pd.read_table(args.file, header=[13,14], dtype=float)
        x = data.iloc[:,0]
        ys = data.iloc[:,1:]

        # x = data.iloc[:,0].astype(float)
        # ys = data.iloc[:,1:].astype(float)

    if out == "":
        out = edit_filename(args.file, ".fit", replace=True)

    if preprocess == "":
        preprocess = False
    else:
        try:
            subdict = dict(b="base", s="smooth", n="norm", a="base norm smooth")
            preprocess = "".join([subdict[s] for s in preprocess])
        except KeyError:
            print("Unknown preprocess option. Accepted keys are b, n, s, a.")
            return 1

    fitMap(x, ys,  args.template, fileout=out, split=args.split, fit=args.nofit, match_preprocess=preprocess, match_method=args.match_method, verbosity = verbose)
    return 0
