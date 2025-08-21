import pyfityk as pfk
import pandas as pd
from fityk import Fityk
import cProfile
from timeit import timeit

def main(filename, file_template):

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
    # names, data, funcs, models  = pfk.read_fityk_text(filename)
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
    x = data.iloc[:,0]
    # x = 1.239842e3/532.1 - 1.23984198e-04*data.iloc[:,0]
    pfk.fitMap(x, data.iloc[:,1:], file_template, fileout="data/temp.fit", verbosity=-1, fit=True)
    # lambda:pfk.read_functions_bis(f,0)
    # print(timeit(lambda:pfk.read_functions(f,0), number=1000))
    # print(pfk.read_functions(f,0))
    # print(pfk.read_functions(f,0, as_text=True))
    return

    # pfk.read_map(filename, save = False)
    # print(data)

    # print(data)
    # dataset = pfk.read_dataset(f,0)
    # print(dataset[0])
    # return data, funcs


if __name__ == '__main__':
    # filename = "data/mapping_data/Map_PL_500.fit"
    # filename = "data/mapping_data/Map_PL_500.fit"
    # filedata = "data/mapping_data/Map_PL.txt"
    filedata = "data/mapping_data/Map_PL_small_eV.txt"
    file_template = "data/mapping_data/Template_spectra.fit"
    
    # filename = "data/-3972.7:-5015.3.peaks"
    # filename = "data/Only_data.fit"
    # filename = "tests/fit_simple.fit"

    main(filedata, file_template)
