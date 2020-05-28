import argparse, os, ruamel.yaml as yaml, shutil
from pathlib import Path

from moseq2_build.utils.constants import ENVIRONMENT_CONFIG, getDefaultImage, C57_FLIP_PATH, FIBER_FLIP_PATH, INSCOPIX_FLIP_PATH
from moseq2_build.utils.commands import printErrorMessage, printSuccessMessage
from moseq2_build.utils.release import getUnamPword, downloadAssets

def updateEnvironment(assetsIndices, image_type, paths):
    use_image = ''
    outputPath = os.path.join(str(Path.home()), ".config", "moseq2_environment")
    # We need to determine which one to make default as the user asked for both
    if len(assetsIndices) == 2:
        while (use_image is not '0' and use_image is not '1'):
            use_image = input("\nSelect which image you wish to use by default: (This can always be changed later)\n[0] Docker\n[1] Singularity\n")
    # Otherwise just use what they requested (either 0 or 1)
    else:
        use_image = image_type

    with open(ENVIRONMENT_CONFIG, 'w') as f:
        # Set singularity as the default
        if use_image == '1':
            p = ''
            for pt in paths:
                if 'singularity' in pt:
                    p = os.path.join(pt, "image")
            singPath = p
        # Set docker as the default
        elif use_image == '0':
            p = ''
            for pt in paths:
                if 'docker' in pt:
                    p = os.path.join(pt, "image")
            singPath = p

        singFile = [fi for fi in os.listdir(singPath) if os.path.isfile(os.path.join(singPath, fi))][0]
        singPath = os.path.join(singPath, singFile)
        d = {'defaultImage': str(os.path.join(outputPath, singPath))}
        flipPaths = {'flipPaths': [C57_FLIP_PATH, FIBER_FLIP_PATH, INSCOPIX_FLIP_PATH]}
        yaml.dump(d, f, Dumper=yaml.RoundTripDumper)
        yaml.dump(flipPaths, f, Dumper=yaml.RoundTripDumper)
    printSuccessMessage("Updated environment file\n\n")
#end updateEnvironment()

def updateDefaultImage(update_image):
    newPath = os.path.abspath(update_image)
    with open(ENVIRONMENT_CONFIG, 'r') as f:
        contents = yaml.safe_load(f)
    contents['defaultImage'] = newPath
    with open(ENVIRONMENT_CONFIG, 'w') as f:
        yaml.dump(contents, f, Dumper=yaml.RoundTripDumper)

    printSuccessMessage('Updated environment file\n\n')
#end updateDefaultImage()

def cleanEnvironmentFolder():
    folder = os.path.dirname(ENVIRONMENT_CONFIG)
    for filename in os.listdir(folder):
        fpath = os.path.join(folder, filename)
        try:
            if os.path.isfile(fpath) or os.path.islink(fpath):
                os.remove(fpath)
            elif os.path.isdir(fpath):
                shutil.rmtree(fpath)
        except Exception as e:
            printErrorMessage("Failed to delete %s. Reason %s" % (fpath, e))
            exit(1)

    printSuccessMessage("Successfully cleaned folder.\n\n")
#end cleanEnvironment()

def determineTargetAssets(version):
    """ Prompts for user input for which asset image
    to download.
    :type version: String
    :param version: String representing the specific version
    of the images to download.
    """
    image_options = ['0', '1', '2'] # 0 - Docker, 1 - Singularity, 2 - Both
    image_type = '' # Assume both at the start
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

    paths = downloadAssets(username, password, assetsIndices, outputPath, version)

    return assetsIndices, image_type, paths
#end determineTargetAssets()
