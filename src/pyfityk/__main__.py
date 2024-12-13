from fityk import Fityk 
import argparse
import pyfityk.io as io
import os 
import sys 

if __name__ == '__main__':
    parser = argparse.ArgumentParser("")
    parser.add_argument("file")
    parser.add_argument("-o", dest="output", nargs="?", default="", help="output folder. If nothing is passed the *file* containing folder is used")
    args = parser.parse_args()
    file = args.file

    output = args.output
    if output == "":
        output = os.path.dirname(file)


    f = Fityk()
    f.execute(f"exec '{file}'")
    io.export_data(f, output)
    io.export_peaks(f, output)
