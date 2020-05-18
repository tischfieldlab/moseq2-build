import argparse, os, ruamel.yaml as yaml, shutil
from pathlib import Path

from moseq2_build.utils.constants import ENVIRONMENT_CONFIG, getDefaultImage
from moseq2_build.utils.commands import printErrorMessage, printSuccessMessage
from moseq2_build.scripts.get_latest_release import getUnamPword, downloadAssets

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--update-image', help='Path to the image file that will become the new default image.',
        default=None, type=str, dest="updatePath")
    parser.add_argument('-c', '--clean-env', help='Deletes all data in the environment folder.',
        dest='cleanFlag', const=True, default=False, type=bool, nargs='?')
    parser.add_argument('-d', '--download-image', help='Updates the environment image and config file.',
        dest='downloadImage', type=bool, default=False, nargs='?', const=True)
    parser.add_argument('--no-default', help='Do not override the current default image path.',
        dest="noDefaultChange", type=bool, const=True, default=False, nargs='?')

    args = parser.parse_args()

    # This needs to be first as it clears all the stuff in the folder
    if (args.cleanFlag == True):
        print("WARNING: About to delete all data in the environment folder!")
        cleanEnvironmentFolder()

    if (args.downloadImage == True):
        assetsIndices, imageType, paths = determineTargetAssets()
        if (args.noDefaultChange == False):
            updateEnvironment(assetsIndices, imageType, paths)
        else:
            printSuccessMessage("Skipping environment file\n\n")

    if (args.updatePath is not None):
        updateDefaultImage(args)

    printSuccessMessage("Exiting now\n\n")
#end main()

def determineTargetAssets():
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

    paths = downloadAssets(username, password, assetsIndices, outputPath)

    return assetsIndices, image_type, paths
#end determineTargetAssets()

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
        yaml.dump(d, f, Dumper=yaml.RoundTripDumper)
    printSuccessMessage("Updated environment file\n\n")
#end updateEnvironment()

def updateDefaultImage(args):
    newPath = os.path.abspath(args.updatePath)
    with open(ENVIRONMENT_CONFIG, 'r') as f:
        contents = yaml.safe_load(f)
    contents['defaultImage'] = newPath
    with open(ENVIRONMENT_CONFIG, 'w') as f:
        yaml.dump(contents, f, Dumper=yaml.RoundTripDumper)

    printSuccessMessage("Updated environment file\n\n")
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

if __name__ == '__main__':
    main()