import sys
from importlib import import_module
import pyfityk.cli as cli

def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)

    if not argv:
        print("Usage: python -m pyfityk <command> [options]")
        print("Available submodules: exporter, mapping")
        return 1

    subcommand = argv.pop(0)

    # try:
    #     mod = import_module(f"pyfityk.cli.{subcommand}")
    # except ModuleNotFoundError:
    #     return 1

    try:
        cmd = getattr(cli, subcommand)
    except AttributeError:
        print(f"Unknown submodule: {command}")
        # print(f"Submodule {subcommand} has no main()")
        return 1

    return cmd(argv)

if __name__ == '__main__':
    sys.exit(main())
