import pyfityk as pfk
from fityk import Fityk
import cProfile

def main(filename):

    # f = Fityk()
    # f.execute(f"reset; exec '{filename}'")

    # cProfile.run("pfk.read_fityk(filename)")
    # cProfile.run("pfk.read_fityk_bis(filename)")
    # t = pfk.read_fityk_text(filename)
    cProfile.run("pfk.read_fityk_text(filename)")



    # print(data)
    # dataset = pfk.read_dataset(f,0)
    # print(dataset[0])


if __name__ == '__main__':
    filename = "data/mapping_data/Map_PL_500.fit"
    main(filename)