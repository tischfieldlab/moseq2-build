from setuptools import setup, find_packages
import subprocess, sys

def install(package):
    subprocess.call([sys.executable, "-m", "pip", "install", package])
#end install()

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
        'importlib',
        'click',
    ],
    python_requires='>=3.6',
    description='Location of environment images for use during the pipeline',
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': ['moseq2-env = moseq2_build.cli:cli'],
    },
)

# NOTE: Need to leave this here after we run the setup so that imports work correctly
from moseq2_build.env.env import determineTargetAssets, updateEnvironment

# This asks for user input for which image to download
# and then which image to make the default image for
# the environment itself
assetsIndices, imageType, paths = determineTargetAssets(None) # Pass in None here because we want the latest release version
updateEnvironment(assetsIndices, imageType, paths)
