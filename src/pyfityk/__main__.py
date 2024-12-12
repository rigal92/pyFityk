from fityk import Fityk 
import argparse
import pyfityk.io as io

if __name__ == '__main__':
    parser = argparse.ArgumentParser("")
    parser.add_argument("file")
    parser.add_argument("-o", dest="output", help="output folder")
    args = parser.parse_args()
    file = args.file
    
    f = Fityk()
    f.execute(f"exec '{file}'")
    io.export_data(f, args.output)
    io.export_peaks(f, args.output)