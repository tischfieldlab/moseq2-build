from distutils.core import setup
import setuptools
import os, sys, ruamel.yaml as yaml
from pathlib import Path
from get_latest_release import getUnamPword, downloadAssets

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

image_options = ['0', '1', '2']
image_type = ''
while (image_type not in image_options):
    image_type = input("\nSelect image type:\n[0] Docker\n[1] Singularity\n[2] Both\n")

outputPath = os.path.join(str(Path.home()), ".config", "moseq2_environment")
if not os.path.isdir(outputPath):
    os.makedirs(outputPath)

username, password = getUnamPword()

# Download singularity
if (image_type == '1'):
    assetsIndices = [1]

# Download docker
elif (image_type == '0'):
    assetsIndices = [0]

# Download both
else:
    assetsIndices = [0, 1]

downloadAssets(username, password, assetsIndices, outputPath)
configFile = os.path.join(str(Path.home()), ".config", "moseq2_environment", "moseq2_environment.yaml")

use_image = ''

# We need to determine which one to make default as the user asked for both
if len(assetsIndices) == 2:
    while (use_image is not '0' and use_image is not '1'):
        use_image = input("\nSelect which image you wish to use by default: (This can always be changed later)\n[0] Docker\n[1] Singularity\n")

# Otherwise just use what they requested (either 0 or 1)
else:
    use_image = image_type

with open(configFile, 'w') as f:
    # Set singularity as the default
    if use_image == '1':
        singPath = os.path.join(str(Path.home()), ".config", "moseq2_environment", "moseq2-singularity", "image")
    # Set docker as the default
    elif use_image == '0':
        singPath = os.path.join(str(Path.home()), ".config", "moseq2_environment", "moseq2-docker", "image")

    singFile = [fi for fi in os.listdir(singPath) if os.path.isfile(os.path.join(singPath, fi))][0]
    singPath = os.path.join(singPath, singFile)
    d = {'defaultImage': str(os.path.join(outputPath, singPath))}
    yaml.dump(d, f, Dumper=yaml.RoundTripDumper)