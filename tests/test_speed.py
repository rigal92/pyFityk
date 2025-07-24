from fityk import Fityk
from time import time
import numpy as np

def test_large(x,y):

    # creating a large Fityk session
    f2 = Fityk()
    f2.execute("set verbosity = -1")
    for i in range(500):
        f2.execute("@+=0")
        f2.load_data(i, x.astype(float)[1:], y.astype(float), [])
        f2.execute(f"@{i}.F += Gaussian(~1000,~0,~1)")

    # fit the large session
    t2 = time()
    f2.execute("@0:fit")
    t2 = time() - t2
    print("Fitting the large file took", t2, "s")
    f2.execute("info state > 'generated_2.fit'")

def test_small(x,y):

    # creating a small Fityk session
    f1 = Fityk()
    f1.execute("set verbosity = -1")
    f1.load_data(0, x.astype(float)[1:], y.astype(float), [])
    f1.execute("@0.F += Gaussian(~1000,~0,~1)")

    # fit the small session
    t1 = time()
    f1.execute("@0:fit")
    t1 = time() - t1

    print("Fitting the small file took", t1, "s")
    # f1.execute("info state > 'generated_1.fit'")

def test_many_variables(x,y):


    # creating a small Fityk session
    f = Fityk()
    f.execute("set verbosity = -1")
    f.load_data(0, x.astype(float)[1:], y.astype(float), [])
    f.execute("@0.F += Gaussian(~1000,~0,~1)")


    # add parameters 
    # for i in range(10,1000):
    #     n = np.random.uniform()
    #     f.execute(f"$_{i} = ~{n}")

    # fit the small session
    t = time()
    f.execute("@0:fit")
    t = time() - t

    print("Fitting the file with a lot of variables", t, "s")
    f.execute("info state > 'generated_3.fit'")

if __name__ == "__main__":


    y, x = np.histogram(np.random.normal(size = 1000000), bins=1000)

    test_large(x,y)
    test_small(x,y)
    test_many_variables(x,y)
