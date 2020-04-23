from distutils.core import setup
import setuptools
import os
from pathlib import Path


scripts = []
script_dir = Path(__file__).resolve().parent.joinpath('scripts')
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
    ],
    description='Location of environment images for use during the pipeline',
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': scripts,
    },
    zip_safe=False
)
