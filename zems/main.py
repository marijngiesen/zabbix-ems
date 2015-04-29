try:
    from commandr import Run
except ImportError:
    Run = None
    import sys
    print "Error: Commandr module cannot be loaded, please install using 'pip install commandr'"
    sys.exit(1)

from zems import commands


def main():
    Run()


if __name__ == "__main__":
    main()
