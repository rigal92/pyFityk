from fityk import Fityk
from time import time
import numpy as np


if __name__ == "__main__":


    y, x = np.histogram(np.random.normal(size = 1000000), bins=1000)

    # creating a small Fityk session
    f1 = Fityk()
    f1.load_data(0, x.astype(float)[1:], y.astype(float), [])
    f1.execute("@0.F += Gaussian(~1000,~0,~1)")


    # creating a large Fityk session
    f2 = Fityk()
    for i in range(500):
        f2.execute("@+=0")
        f2.load_data(i, x.astype(float)[1:], y.astype(float), [])
        f2.execute(f"@{i}.F += Gaussian(~1000,~0,~1)")

    # fit the small session
    t1 = time()
    f1.execute("@0:fit")
    t1 = time() - t1

    # fit the large session
    t2 = time()
    f2.execute("@0:fit")
    t2 = time() - t2

    print("Fitting the small file took", t1, "s")
    print("Fitting the large file took", t2, "s")

    f1.execute("info state > 'generated_1.fit'")
    f2.execute("info state > 'generated_2.fit'")
