#!/usr/bin/env python3

"""
This module checks the PEP8 (pycodestyle) and pylint compliance of your code

pycodestyle is described here:
    https://pypi.org/project/pycodestyle/

pylint is described here:
    https://www.pylint.org/

$ python checkpy.py
Without arguments this runs a standard check on the code in the folders
starting with the current directory.

$ python checkpy.py [<path>]
Run it with folders or files as arguments to run the check on those paths.
These paths should be relative to the current working directory. Separate paths
with spaces
"""

from __future__ import print_function
import os
import sys
import subprocess
import argparse
from distutils import spawn

if sys.version_info.major == 3:
    PYLINT = 'pylint3'
else:
    PYLINT = 'pylint2'

IMPORT_ERROR_MSG = """

    pylint and/or pycodestyle not available
    Install these packages from:

    https://pypi.python.org/pypi/pylint


    Or, if you're on a Unix-like platform, try these commands:

        sudo apt install pylint
        sudo apt install pylint3
        sudo pip install autopep8
        sudo apt install pycodestyle

    And then try running the program: {} once again

""".format(sys.argv[0])


# PEP warnings to ignore
# we can tailor this to our needs but this may be a good start ...
IGNORE_PEP = {
    'E121': 'indentation is not a multiple of four',
    'E122': 'missing indentation or outdented',
    'E123': ('closing bracket does not match indentation of' +
             ' opening brackets line'),
    'E125': ('continuation line does not distinguish itself' +
             ' from next logical line'),
    'E126': 'over-indented for hanging indent',
    'E127': 'over-indented for visual indent',
    'E128': 'continuation line under-indented for visual indent',
    'E302': 'expected 2 blank lines, found %d',
    'E501': 'line too long (%d > %d characters)',
    'W391': 'blank line at end of file'}


USAGE_MSG = """

    Usage: {0} [-h|--help] [-l] [-r|--remove <pepkeylist>] [<path>]

    -h|--help      : displays this help message
    -l|--list      : list PEP warnings that are being ignored
            (and then exits the program without doing
            anything else)
    -r|--remove <pepkeylist>  : disable PEP check on this key or key list
    pepkeylist      : a string of comma-separated list of keys
            Examples of keylists:
            E127
            "E127"
            "E127,E501"
            "E127, E501"

    Run without arguments to run a standard check.
    python {0}

    Run with paths as arguments to check those paths,
    the paths must be relative to the current working directory
    python {0} [<path>]
    """.format(sys.argv[0])


def check(paths=None):
    """ function to do the pylint and pycodestyle check """

    folder = os.path.dirname(__file__)
    rcfile = os.path.join(folder, 'pylintrc')
    if os.path.isfile(rcfile):
        mypylint = '{} --rcfile="{}"'.format(PYLINT, rcfile)
    else:
        mypylint = '{} '.format(PYLINT)

    mypycodestyle = ('pycodestyle --ignore=%s --statistics ') % ','.join(IGNORE_PEP.keys())

    # If a normal check with no arguments, check the paths starting with the
    # current directory, else check the folders specified and treat them as
    # relative paths
    if paths is None:
        filelist = []
        for dpath, _, files in os.walk(os.getcwd()):
            for myfile in files:
                if myfile.endswith('.py'):
                    filelist.append(dpath + os.path.sep + myfile)
    else:
        filelist = []
        for thisfile in paths:
            if os.path.isfile(thisfile) and thisfile.endswith('.py'):
                filelist.append(thisfile)
            elif os.path.isdir(thisfile):
                for dpath, _, files in os.walk(thisfile):
                    for myfile in files:
                        if myfile.endswith('.py'):
                            filelist.append(dpath + os.path.sep + myfile)

    rescount = 0
    for myfile in filelist:
        rescount = 0
        sys.stdout.write('starting pylint, as %s %s\n' % (mypylint, myfile))
        sys.stdout.flush()
        res = subprocess.call(mypylint + " " + myfile, shell=True)
        if res == 0:
            result = 'SUCCESS'
        else:
            result = 'FAILED'
            rescount += 1
        sys.stdout.write('pylint: %s\n' % (result, ))
        sys.stdout.flush()

        sys.stdout.write('starting pycodestyle, as %s' % (mypycodestyle, ))
        sys.stdout.flush()
        res = subprocess.call(mypycodestyle + " " + myfile, shell=True)
        if res == 0:
            result = 'SUCCESS'
        else:
            result = 'FAILED'
            rescount += 1
        sys.stdout.write('pycodestyle: %s\n' % (result, ))
        sys.stdout.flush()

    return rescount


def list_pep_keys():
    """ function to list the pep keys """

    print("\n\tThese are the PEP Keys that are being ignored:\n")
    for k in IGNORE_PEP:
        print('\t%s: %s\n' % (k, IGNORE_PEP[k]))

    sys.exit(0)


def check_sanity():
    """ check to make sure that pylint and pycodestyle are installed """
    if spawn.find_executable(PYLINT) is None:
        print(IMPORT_ERROR_MSG)
        sys.exit(1)
    if spawn.find_executable('pycodestyle') is None:
        print(IMPORT_ERROR_MSG)
        sys.exit(1)


def main():
    """ main function """

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=USAGE_MSG)

    parser.add_argument('-l', '--list',
                        dest='listpep',
                        action='store_true')

    parser.add_argument('-r', '--remove',
                        dest='pepkeylist',
                        action='store_true')

    parser.add_argument('paths',
                        nargs='*', default=[])

    options = parser.parse_args()

    if options.listpep:
        list_pep_keys()

    if options.pepkeylist:
        keystr = options.pepkeylist
        keylist = [k.strip() for k in keystr.split(',')]
        for k in keylist:
            try:
                IGNORE_PEP.pop(k)
                print("Removing key:%s from PEP ignore list\n" % k)
            except KeyError:
                print("Error, key %s not found, these are the keys:\n" % k)
                list_pep_keys()
                sys.exit(1)

    check_sanity()

    if len(options.paths) == 0:
        myrc = check()
    else:
        myrc = check(paths=options.paths)

    sys.exit(myrc)


if __name__ == '__main__':
    main()
