import setuptools
import os

from distutils.core import setup
from pathlib import Path

scripts = []
script_dir = Path(__file__).resolve().parent.joinpath(
    "moseq2_build", "scripts")
for s in script_dir.glob("*.py"):
    if s.name != "__init__.py":
        ep = s.name.replace(".py", "")
        epp = 'moseq2-' + ep
        scripts.append("{} = moseq2_build.scripts.{}:main".format(epp, ep))

setup(
    name='moseq2-build',
    author='Tischfield Lab',
    version='0.1.0',
    license='MIT License',
    install_requires=[
        'ruamel.yaml',
        'termcolor',
        'tqdm',
        'pytest',
        'setuptools',
        'tabulate',
        'python-dotenv',
        'pyyaml'
    ],
    python_requires='>=3.6',
    description='Location of environment images for use during the pipeline',
    packages=setuptools.find_packages(),
    include_package_data=True,
    entry_points={"console_scripts": scripts},
    zip_safe=False,
)

# # NOTE: Need to leave this here after we run the setup so that imports work correctly
# from moseq2_build.env.env import determineTargetAssets, updateEnvironment
#
# # This asks for user input for which image to download
# # and then which image to make the default image for
# # the environment itself
# assetsIndices, imageType, paths = determineTargetAssets(None) # Pass in None here because we want the latest release version
# updateEnvironment(assetsIndices, imageType, paths)
print("\nPlease make sure to setup your environment by running:\n moseq2-env create-env --help \n")
