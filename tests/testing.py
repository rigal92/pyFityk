import pyfityk as pfk
from pyfityk.mapping import match_template
import pandas as pd
from fityk import Fityk
import matplotlib.pyplot as plt
import cProfile
from timeit import timeit

def main(filename, file_template, file_template_data):

    # f = Fityk()
    # f.execute(f"reset; exec '{file_template}'")
    # funcs = pfk.get_define_functions(f)

    # f2 = Fityk()
    # print("First: " + f2.get_info("types"), "\n-----------\n")
    # pfk.set_define_functions(f2, funcs)
    # print("After: " + f2.get_info("types"))

    # cProfile.run("pfk.read_fityk(file_template)")
    # cProfile.run("pfk.read_fityk_text(filename)")
    # data  = pfk.read_fityk(filename)
    # data  = pfk.read_fityk_text(filename)
    # data  = pfk.read_fityk_text(file_template)
    # template = pd.DataFrame([x["data"].y for x in data]).T
    # print(template)
    # template.to_csv("data/mapping_data/Template.dat", sep = "\t", index=None, header=None)
    # print(*models, sep="\n")
    # print(data)
    
    # cProfile.run("pfk.read_peaks(filename)")
    # t1 = timeit(lambda :pfk.read_peaks(filename), number=1000)
    # print(t1)
    # print(pfk.read_peaks(filename))
    # print(pfk.read_peaks_bis(filename))
    # print(*funcs, sep = "\n----------\n")
    # return data
    # fun = pfk.get_functions(f,1)
    # print(*funcs[:6], sep="\n---\n")

    data = pd.read_table(filename, header=[13,14])
    data_template = pd.read_table(file_template_data, header = None)
    x = data.iloc[:,0]
    # y1 = data.iloc[:,20]
    # y2 = data_template.iloc[:,1]
    # t = match_template(data.iloc[:,1:].T.values, data_template.T.values, "pearsonr")
    # t2 = match_template(data.iloc[:,1:].T.values, data_template.T.values, "pearsonr", smooth=False)
    # plt.plot(t2-t1)
    # t = [match_template(data.iloc[:,1:].T.values, data_template.T.values, method) for method in ["euclidean", "cosine", "manhattan"]]
    # print(t)

    # plt.plot(y1, "-o", label="euclideanean")
    # plt.plot(y2, "-o", label="cosine")
    # plt.plot(t[2], "-o", label="manhattan")
    # plt.legend()
    # plt.show()

    pfk.fitMap(x, data.iloc[:,1:], file_template, match_preprocess=True, fileout="data/match_euclidean.fit", verbosity=-1, fit=False, match_method="euclidean")
    pfk.fitMap(x, data.iloc[:,1:], file_template, match_preprocess="norm smooth", fileout="data/match_cosine.fit", verbosity=-1, fit=False, match_method="cosine")
    pfk.fitMap(x, data.iloc[:,1:], file_template, match_preprocess="normbase", fileout="data/match_manhattan.fit", verbosity=-1, fit=False, match_method="manhattan")
    pfk.fitMap(x, data.iloc[:,1:], file_template, match_preprocess=False, fileout="data/match_pearsonr.fit", verbosity=-1, fit=False, match_method="pearsonr")


if __name__ == '__main__':
    # filename = "data/mapping_data/Map_PL_500.fit"
    # filename = "data/mapping_data/Map_PL_500.fit"
    # filedata = "data/mapping_data/Map_PL.txt"
    filedata = "data/mapping_data/Map_PL_small_eV.txt"
    file_template = "data/mapping_data/Template_spectra.fit"
    file_template_data = "data/mapping_data/Template.dat"
    
    # filename = "data/-3972.7:-5015.3.peaks"
    # filename = "data/Only_data.fit"
    # filename = "tests/fit_simple.fit"

    main(filedata, file_template, file_template_data)
