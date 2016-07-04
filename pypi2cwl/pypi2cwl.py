# /usr/bin/python3
import imp
import os
import string
import subprocess
import sys

import setuptools as old_setuptools

import argparse as ap

params = None

def setup(*args, **kwargs):
    global params
    params = kwargs


def install_package(repo_name, pip_version, install_globally):
    subprocess.call(['./download_install_package.sh {0} {1} {2}'.
                    format(repo_name, pip_version, install_globally)], shell=True)
    # p2c-dir is created inside `download_install_package.sh` script
    base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'p2c-dir'))
    # importing setup from the target repo and parsing scripts
    for directory in os.listdir(base_path):
        if directory.lower().startswith(repo_name.lower()):
            DIR = os.path.join(base_path, directory)
            break
    sys.path.insert(0, DIR)
    os.chdir(DIR)
    import setup as s


def generate_tools(args):
    if params.get('entry_points', ''):
        console_scripts = params['entry_points'].get('console_scripts', '')
        if console_scripts:
            for script in console_scripts:
                params['scripts'].append(script.split('=')[0].strip())
    if params.get('scripts', ''):
        for script in list(map(lambda script: script.split('/')[-1], params['scripts'])):
            command = [script, '--generate_cwl_tool']
            if args.directory:
                command.extend(['-d', args.directory])
            if args.generate_outputs:
                command.extend(['-go'])
            subprocess.call(command)
    else:
        raise KeyError


def main():
    help_text = """
    pypi2cwl generates a bunch of  CWL command line tools out of scripts from a given PyPi package or GitHub repo
    Example: $ pypi2cwl PYPI_PACKAGE <options>
    """
    parser = ap.ArgumentParser(description=help_text,
                               formatter_class=ap.RawDescriptionHelpFormatter)
    parser.add_argument('repo',
                        help='PyPi repository or direct Github link')
    parser.add_argument('-d', '--directory',
                        help='Directory to store CWL tool descriptions')
    parser.add_argument('-go', '--generate_outputs', action='store_true',
                        help='Form output section from args than contain `output` keyword in their names')
    parser.add_argument('-v', '--venv', action='store_false',
                        help="Choose this option if you run pypi2cwl in a virtual environment so the package is "
                             "not installed globally")
    args = parser.parse_args()
    repo_name = args.repo
    install_globally = True and args.venv

    if not all(map(lambda x: x in string.ascii_letters + string.digits + '-_', repo_name)):
        raise ValueError('Incorrect repository name')
    else:
        setuptools = imp.new_module('setuptools')
        sys.modules['setuptools'] = setuptools
        # making copies of `setuptools` attributes and capturing `setup()`
        k = list(map(lambda x: setattr(setuptools, x, getattr(old_setuptools, x)), dir(old_setuptools)))
        setuptools.setup = setup

        install_package(repo_name, 'pip2', install_globally)
        try:
            generate_tools(args)
        except KeyError:
            raise KeyError('No scripts provided in setup.py of the package')
        except:
            install_package(repo_name, 'pip3', install_globally)
            try:
                generate_tools(args)
            except:
                raise ValueError('Something went wrong')


if __name__ == "__main__":
    main()