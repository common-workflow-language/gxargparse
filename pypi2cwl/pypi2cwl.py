# /usr/bin/python3
import imp
import os
import subprocess
import sys

import argparse as ap


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
parser.add_argument('--no-install', action='store_true',
                            help="Uninstall package after tool generation ")

args = parser.parse_args()

repo = args.repo
if len(repo.split('/')) > 1:
    # GitHub repo
    pass
else:
    setuptools = imp.new_module('setuptools')
    sys.modules['setuptools'] = setuptools
    params = None

    # TODO: cover all setuptools functions

    def setup(*args, **kwargs):
        global params
        params = kwargs

    def find_packages(*args, **kwargs):
        return

    setuptools.setup = setup
    setuptools.find_packages = find_packages
    subprocess.call(['sudo','pip2', 'install', repo])  # TODO: check pip version
    """
    TODO: Downloading repo from GitHub via API and unzipping
    """
    DIR = "/home/anton/phylotoast-master"  # has nothing to do with production version, just for the sake of quicker prototyping!
    sys.path.insert(0, DIR)
    os.chdir(DIR)
    # importing setup from the target repo and parsing scripts
    import setup
    if params['scripts']:
        for script in list(map(lambda script: script.split('/')[-1], params['scripts'])):
            command = [script, '--generate_cwl_tool']
            if args.directory:
                command.extend(['-d', args.directory])
            subprocess.call(command)
