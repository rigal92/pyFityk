import pyfityk as pfk
from fityk import Fityk
import cProfile

def main(filename):

    # f = Fityk()
    # f.execute(f"reset; exec '{filename}'")

    # cProfile.run("pfk.read_fityk(filename)")
    # t = pfk.read_fityk_text(filename)
    # cProfile.run("pfk.read_fityk_text(filename)")
    # data, funcs = pfk.read_fityk(filename)
    data, funcs = pfk.read_fityk_text(filename)
    print(data[0])
    print(funcs)
    # return data
    # fun = pfk.get_functions(f,1)
    # print(*funcs[:6], sep="\n---\n")

    # data = pfk.get_data(f,1)
    # print(data)

    # print(data)
    # dataset = pfk.read_dataset(f,0)
    # print(dataset[0])


if __name__ == '__main__':
    # filename = "data/mapping_data/Map_PL_500.fit"
    filename = "data/mapping_data/Template_spectra.fit"
    # filename = "data/Only_data.fit"
    # filename = "data/Raman/map2x2.fit"
    data = main(filename)
