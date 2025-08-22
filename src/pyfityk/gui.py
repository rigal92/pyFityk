def exporter():
    parser = argparse.ArgumentParser("")
    parser.add_argument("file")
    parser.add_argument("-o", dest="output", nargs="?", default="", help="output folder. If nothing is passed the *file* containing folder is used")
    parser.add_argument("--errors", dest="errors", action="store_true", help="flag to enable the export of the peaks' parameters errors")
    parser.add_argument("--data-only", dest="do", action="store_true", help="export only data")
    parser.add_argument("--peaks-only", dest="po", action="store_true", help="export peaks data")
    args = parser.parse_args()
    file = args.file

    output = args.output
    if output == "":
        output = os.path.dirname(file)

    f = Fityk()
    f.execute(f"exec '{file}'")
    if not args.po:
        io.export_data(f, output)
    if not args.do:
        io.export_peaks(f, output, args.errors)
