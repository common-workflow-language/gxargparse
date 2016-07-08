# /usr/bin/python3
import imp
import os
import shutil
import string
import subprocess
import sys

import setuptools as old_setuptools

import argparse as ap

params = None
package_dir = None
base_dir = os.getcwd()


def setup(*args, **kwargs):
    global params
    params = kwargs


def normalize(s):
    return s.lower().replace('-', '_')


def install_package(repo_name, install_globally):
    global package_dir
    exit_status = subprocess.call([os.path.dirname(__file__) + '/./download_install_package.sh {0} {1} {2}'.
                    format(base_dir, repo_name, install_globally)], shell=True)
    if exit_status == 1:
        sys.exit("Package couldn't install, try installing manually")
    # p2c-dir is created inside `download_install_package.sh` script
    p2cdir = os.path.abspath(os.path.join(base_dir, 'p2c-dir'))
    # importing setup from the target repo and parsing scripts
    for directory in os.listdir(p2cdir):
        if normalize(directory).startswith(normalize(repo_name)):
            package_dir = os.path.join(p2cdir, directory)
            break
    sys.path.insert(0, package_dir)
    os.chdir(package_dir)
    import setup as s


def generate_tools(args):
    if params is None:
        sys.exit('Check setup.py of the downloaded package at {0}; could not import setup function'.format(package_dir))
    if params.get('entry_points', ''):
        console_scripts = params['entry_points'].get('console_scripts', '')
        if console_scripts:
            if not params.get('scripts', ''):
                params['scripts'] = []
            for script in console_scripts:
                params['scripts'].append(script.split('=')[0].strip())
    if params.get('scripts', ''):
        for script in list(map(lambda script: script.split('/')[-1], params['scripts'])):
            command = [script, '--generate_cwl_tool', '-d', args.directory or base_dir]
            if args.generate_outputs:
                command.extend(['-go'])
            subprocess.call(command)
        print('CWL tool descriptions are successfully generated into {0}'.format(args.directory or base_dir))
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
    parser.add_argument('--no-clean', action='store_true',
                        help="Don't delete a directory with the source code")
    args = parser.parse_args()
    repo_name = args.repo
    install_globally = True and args.venv

    if not all(map(lambda x: x in string.ascii_letters + string.digits + '-_', repo_name)):
        sys.exit("Package with name `{0}` doesn't exist".format(repo_name))
    else:
        setuptools = imp.new_module('setuptools')
        sys.modules['setuptools'] = setuptools
        # making copies of `setuptools` attributes and capturing `setup()`
        k = list(map(lambda x: setattr(setuptools, x, getattr(old_setuptools, x)), dir(old_setuptools)))
        setuptools.setup = setup

        install_package(repo_name, install_globally)
        try:
            generate_tools(args)
        except KeyError:
            sys.exit('Tools cannot be generated: no scripts provided in the setup.py of the package, '
                     'check {0}/setup.py'.format(package_dir))
        finally:
            if not args.no_clean:
                shutil.rmtree(os.path.join(base_dir, 'p2c-dir'))


if __name__ == "__main__":
    main()