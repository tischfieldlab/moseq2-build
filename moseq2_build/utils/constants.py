import os
import sys
import csv
import subprocess
import yaml
from io import StringIO

from pathlib import Path

# Used to download images from the releases page.
GITHUB_LINK = "@api.github.com/repos/tischfieldlab/moseq2-build/releases"

# Used as the default flip file in certain scripts, if one is not passed in explicitly.
DEFAULT_FLIP_FILE = 'flip_classifier_k2_c57_10to13weeks.pkl'

# Used to list and add images to the container.
IMAGE_FLIP_PATH = '/moseq2_data/flip_files'

# Path to the argtable file within the image generated during build time.
ARG_TABLE = '/moseq2_data/argtable.yaml'

# This class houses the commands we support for each image. We abstract them out to this class so that we
# can use the appropriate command syntax when needed.
class Commands:
    SINGULARITY_COMS = {
        'exec':                         'singularity exec',
        'mount':                        '-B'
    }

    # TODO: SUPPORT DOCKER
    DOCKER_COMS = {
        'exec':                         None,
        'mount':                        None
    }
#end Commands

def get_argtable(com_table, image):
    """Returns the contents of the argtable if it exists within the image.

    Args:
        com_table (Dictionary <string, string>): A list of commands compatible with the active image.
        image (string): Path to the image file.

    Returns:
        Dictionary <string, string>: The contents of the argtable yaml file.
    """

    # We cat the contents of the argtable file in the image, redirect it from stdout to a StringIO object
    # where we then load it as a yaml file object.
    final_command = com_table['exec'] + ' ' + image + ' ' + 'cat ' + ARG_TABLE
    process = subprocess.Popen(final_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    if len(error) != 0:
        sys.stderr.write('Could not open argtable. Got the following error: {}\n'.format(error.decode('utf-8')))
        sys.stderr.write('Please be sure that you have downloaded the latest image.\n')
        exit(-1)

    # Load the string io object into a yaml file object and return it.
    with StringIO(output.decode('utf-8')) as f:
        conts = yaml.load(f, yaml.FullLoader)

    return conts
#end get_argtable()

def get_environment_path():
    """Gets the location where all environments are to be installed.

    Returns:
        string: Path to the environment directory.
    """
    return os.path.join(str(Path.home()), ".config", "moseq2_environment")
#end get_environment_path()

def get_environment_manifest():
    """Gets the global manifest file where all environments are listed.

    Returns:
        string: Path to the manifest file.
    """
    return os.path.join(str(Path.home()), ".config", "moseq2_environment", "environments.tsv")
#end get_environment_manifest()

def get_active_env():
    """Gets the active environment name.

    Returns:
        string: The name of the active environment.
    """
    if not os.path.isfile(get_environment_manifest()):
        sys.stderr.write('No environment has been created. Please create one and rerun.\n')
        exit(1)

    with open(get_environment_manifest(), 'r') as f:
        contents = csv.reader(f, delimiter='\t')

        env_name = ''
        for row in contents:
            if row == []:
                continue
            if row[1] == 'True':
                env_name = row[0]

    if len(env_name) == 0:
        sys.stderr.write('There is no active environment, please activate one by typing moseq2-env use-env --help.\n')
        exit(1)

    return env_name
#end get_active_env()

def get_active_image():
    """Gets the active image for the current active environment.

    Returns:
        string: Path to the active image.
    """
    env = get_active_env()

    env_path = os.path.join(get_environment_path(), env, env + '.yml')
    with open(env_path, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)

    img = contents['ACTIVE_IMAGE']

    if img == None:
        sys.stderr.write('There is no active image. Please activate one before proceeding by typing moseq2-env use-env --help.\n')

    return img
#end get_active_image()

def get_classifier_path():
    """Returns the path to where the classifiers are stored inside the image.

    Returns:
        string: Path to the folder where flip classifiers are stored in the image.
    """
    return IMAGE_FLIP_PATH
#end get_classifier_path()

def get_all_classifiers():
    """Returns a list of all classifiers available inside the container.

    Returns:
        list (string): List of all available classifiers inside an image.
    """
    mod_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    flip_dir = os.path.join(mod_dir, 'flip_classifiers')

    flips = []
    # IMPORTANT: Keep this as a forward slash because the singularity file only works with /
    for f in os.listdir(flip_dir):
        flips.append(IMAGE_FLIP_PATH + '/' + f)

    return flips
#end get_all_classifiers()

def get_custom_bind_paths():
    """Gets the list of custom bind paths if they exist in the active environment.

    Returns:
        list (string): List of custom bind paths for the active environment.
    """
    env = get_active_env()
    env_path = os.path.join(get_environment_path(), env, env + '.yml')
    with open(env_path, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)

    paths = contents['CUSTOM_BIND_PATHS']

    if paths == None or len(paths) == 0:
        return []

    return paths
#end get_custom_bind_paths()

def add_custom_bind_paths(paths):
    """Adds a custom bind path to the active envrionment yaml file.

    Args:
        paths (list (string)): List of absolute bind paths to add to the environment.
    """
    env = get_active_env()
    env_path = os.path.join(get_environment_path(), env, env + '.yml')
    with open(env_path, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)

    old_paths = contents['CUSTOM_BIND_PATHS']
    if old_paths == None:
        old_paths = paths

    else:
        for p in paths:
            if p in old_paths:
                sys.stderr.write('Skipping adding {} as it already exists in the env file.\n'.format(p))
                continue
            else:
                old_paths.append(p)
                sys.stderr.write('Successfully added {} into the env file.\n'.format(p))

    contents['CUSTOM_BIND_PATHS'] = old_paths

    with open(env_path, 'w') as f:
        yaml.dump(contents, f)
#end add_custom_bind_paths()

def remove_custom_bind_paths(paths):
    """Removes custom bind paths from the active environment file.

    Args:
        paths (list (string)): List of absolute bind paths to remove from the environment.
    """
    env = get_active_env()
    env_path = os.path.join(get_environment_path(), env, env + '.yml')
    with open(env_path, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)

    old_paths = contents['CUSTOM_BIND_PATHS']
    for p in paths:
        if p in old_paths:
            old_paths.remove(p)
            sys.stderr.write('Successfully deleted {} from the env file.\n'.format(p))
        else:
            sys.stderr.write('{} is not in the env file, so it was not deleted.\n'.format(p))

    contents['CUSTOM_BIND_PATHS'] = old_paths

    with open(env_path, 'w') as f:
        yaml.dump(contents, f)
#end remove_custom_bind_paths()

# Set up a dummy exception so we can break from searching.
class Found(Exception): pass
def get_image_paths(env, image):
    """Gets the list of images available in a given environment.

    Args:
        env (string): Name of the environment.
        image (string): Name of the environment. [singularity|docker]

    Raises:
        Found: Dummy exception raised when the image is found so we stop searching.

    Returns:
        string: Path to the image path searched for.
    """
    contents = os.path.join(get_environment_path(), env)
    res = None

    try:
        for root, subdirs, files in os.walk(contents):
            for f in files:
                if image == 'singularity' and f.endswith('.sif'):
                    res = os.path.join(root, f)
                    raise Found

                # TODO: DOCKER
                if image == 'docker':
                    for sub in subdirs:
                        if image in sub:
                            res = os.path.join(root, sub)
                            raise Found
    except Found:
        return res

    sys.stderr.write('Could not find any images. Please make sure you have them downloaded first.\n')
    exit(1)
#end get_image_paths()