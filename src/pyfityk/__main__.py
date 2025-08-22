from fityk import Fityk 
import argparse
import pyfityk.io as io
import os 
import sys

def main():
    argv = list(sys.argv[1:] if argv is None else argv)

    if not argv:
        print("Usage: python -m pyfityk <command> [options]")
        print("Available submodules: export, mapping")
        return 1

    subcommand = argv.pop(0)

    try:
        mod = import_module(f"mypackage.{subcommand}")
    except ModuleNotFoundError:
        print(f"Unknown submodule: {subcommand}")
        return 1

    if not hasattr(mod, "main"):
        print(f"Submodule {subcommand} has no main()")
        return 1

    return mod.main(argv)
if __name__ == '__main__':
    sys.exit(main())
