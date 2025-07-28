import pyfityk as pfk
from fityk import Fityk
import cProfile
from timeit import timeit

def main(filename):

    data, funcs = 0,0
    f = Fityk()
    f.execute(f"reset; exec '{filename}'")
    funcs = pfk.get_define_functions(f)

    f2 = Fityk()
    print("First: " + f2.get_info("types"), "\n-----------\n")
    pfk.set_define_functions(f2, funcs)
    print("After: " + f2.get_info("types"))

    # cProfile.run("pfk.read_fityk(filename)")
    # cProfile.run("pfk.read_fityk_text(filename)")
    # data, funcs = pfk.read_fityk(filename)
    # data, funcs = pfk.read_fityk_text(filename)
    # print(data[0])
    
    # cProfile.run("pfk.read_peaks(filename)")
    # t1 = timeit(lambda :pfk.read_peaks(filename), number=1000)
    # print(t1)
    # print(pfk.read_peaks(filename))
    # print(pfk.read_peaks_bis(filename))
    # print(*funcs, sep = "\n----------\n")
    # return data
    # fun = pfk.get_functions(f,1)
    # print(*funcs[:6], sep="\n---\n")

    # data = pfk.get_data(f,1)
    # print(data)

    # print(data)
    # dataset = pfk.read_dataset(f,0)
    # print(dataset[0])
    # return data, funcs


if __name__ == '__main__':
    # filename = "data/mapping_data/Map_PL_500.fit"
    filename = "data/mapping_data/Template_spectra.fit"
    # filename = "data/-3972.7:-5015.3.peaks"
    # filename = "data/Only_data.fit"
    # filename = "tests/fit_simple.fit"
    main(filename)
