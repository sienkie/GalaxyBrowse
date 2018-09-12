from models import *
import sys


def run(argv):
    try:
        choice = argv[1].strip()
    except IndexError as err:
        print('Please specify, which GalaxyBrowse method you want to run.')
        # this should not happen if correct methods are specified in wrappers
        raise err

    args = argv[2:]
    if choice == 'prepare':
        script = JBrowsePrepare(args)
    elif choice == "add":
        script = JBrowseAdd(args)
    elif choice == "remove":
        script = JBrowseRemove(args)
    else:
        raise ValueError('Invalid name of GalaxyBrowse method!')
        # this should not happen if correct methods are specified in wrappers
    script.run()


if __name__ == '__main__':
    run(sys.argv)
