from distutils.core import setup
import setuptools
import os, sys
from pathlib import Path

scripts = []
script_dir = Path(__file__).resolve().parent.joinpath('moseq2_build', 'scripts')
for s in script_dir.glob('*.py'):
    if s.name != '__init__.py':
        ep = s.name.replace('.py', '')
        scripts.append('{} = scripts.{}:main'.format(ep,ep))

setup(
    name='moseq2-build',
    version='0.0.1',
    license='MIT License',
    install_requires=[
        'ruamel.yaml',
        'termcolor',
        'tqdm',
    ],
    description='Location of environment images for use during the pipeline',
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': scripts,
    },
    zip_safe=False
)

# NOTE: Need to leave this here after we run the setup so that imports work correctly
from moseq2_build.utils.setup_utils import determineTargetAssetsAndUpdateEnvironment

# This will ask the user for which image(s) to download and
# update the global configuration file
determineTargetAssetsAndUpdateEnvironment()