import os
import sys
import csv
import yaml

from pathlib import Path

GITHUB_LINK = "@api.github.com/repos/tischfieldlab/moseq2-build/releases"
DEFAULT_FLIP_FILE = 'flip_classifier_k2_c57_10to13weeks.pkl'
IMAGE_FLIP_PATH = '/moseq2_data/flip_files'

class Commands:
    BATCH_TABLE = {'batch': ['--input-dir', '-i', '--config-file', '-c', '--filename']}
    EXTRACT_TABLE = {'generate-config': ['-o', '--output-file'],
                'extract': ['--config-file', '--flip-classifier']}
    SINGULARITY_COMS = {'exec': 'singularity exec', 'mount': '-B'}
    #  TODO: SUPPORT DOCKER
    DOCKER_COMS = None
#end Commands

def get_environment_path():
    return os.path.join(str(Path.home()), ".config", "moseq2_environment")
#end get_environment_path()

def get_environment_manifest():
    return os.path.join(str(Path.home()), ".config", "moseq2_environment", "environments.tsv")
#end get_environment_manifest()

def get_active_env():
    with open(get_environment_manifest(), 'r') as f:
        contents = csv.reader(f, delimiter='\t')

        env_name = ''
        for row in contents:
            if row[1] == 'True':
                env_name = row[0]

    if len(env_name) == 0:
        sys.stderr.write('There is no active environment, please activate one.\n')
        exit(1)

    return env_name
#end get_active_env()

def get_active_image():
    env = get_active_env()

    env_path = os.path.join(get_environment_path(), env, env + '.yml')
    with open(env_path, 'r') as f:
        contents = yaml.load(f, Loader=yaml.FullLoader)

    img = contents['ACTIVE_IMAGE']

    if img == None:
        sys.stderr.write('There is no active image. Please activate one before proceeding.\n')
        exit(1)

    return img
#end get_active_image()

def get_classifier_path():
    return IMAGE_FLIP_PATH
#end get_classifier_path()

def get_all_classifiers():
    mod_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    flip_dir = os.path.join(mod_dir, 'flip_classifiers')

    flips = []
    # NOTE: Keep this as a forward slash because the singularity file only works with /
    for f in os.listdir(flip_dir):
        flips.append(IMAGE_FLIP_PATH + '/' + f)

    return flips
#end get_all_classifiers()

class Found(Exception): pass
def get_image_paths(env, image):
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

if __name__ == "__main__":
    print(get_all_classifiers())