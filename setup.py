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
    version='0.1.0',
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
from moseq2_build.scripts.environment import determineTargetAssets, updateEnvironment

# This asks for user input for which image to download
# and then which image to make the default image for
# the environment itself
assetsIndices, imageType, paths = determineTargetAssets()
updateEnvironment(assetsIndices, imageType, paths)