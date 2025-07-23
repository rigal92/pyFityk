import pyfityk.io as ftk
from pyfityk.support import points_to_arrays, get_func_y
from fityk import Fityk
import time

f = Fityk()
def main(filename):

    f.execute(f"reset; exec {filename}")

    import timeit
    # t1 = timeit.timeit(lambda :ftk.get_functions(f,1), number =100)
    # print("get_functions\n", ftk.get_functions(f,1))
    # print("Time:", t1)
    t1 = timeit.timeit(lambda :ftk.read_functions(f,1), number =100)
    print("get_functions\n", ftk.read_functions(f,1))
    print("Time:", t1)
    # t1 = timeit.timeit(lambda :ftk.get_data(f,1), number =1)
    # print(t1)

    # print(funcs)
    # print(funcs.iloc[1,-1])
    
    # data = ftk.get_data(f,2)
    # print(data)
    # x = data[:,0]
    # print("test = :", timeit.timeit(lambda:ftk.get_functions(f, 0), number = 1000))
    # print("test intern = :", timeit.timeit(lambda:f.execute(f"@0: print all:x ,y, F[0](x), F(x)")))




if __name__ == '__main__':

    filename = "data/Map_PL_500spectra.fit"
    # filename = "data/Raman/map2x2.fit"
    main(filename)