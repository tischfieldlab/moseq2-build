import os
import sys
import csv
import yaml

from pathlib import Path

GITHUB_LINK = "@api.github.com/repos/tischfieldlab/moseq2-build/releases"
DEFAULT_FLIP_FILE = 'flip_classifier_k2_c57_10to13weeks.pkl'
IMAGE_FLIP_PATH = '/moseq2_data/flip_files'

class Commands:
    BATCH_TABLE = {
        'extract-batch':                ['--input-dir', '-i', '--config-file', '-c', '--filename'],
        'aggregate-extract-results':    ['-i', '--input-dir', '-o', '--output-dir'],
        'aggregate-modeling-results':   ['-i', '--input-dir', '-d', '--dest-file'],
        'convert-raw-to-avi':           ['-i', '--input-dir'],
        'gen-grid-search-config':       ['-o', '--output-dir', '-n', '--name'],
        'learn-model-parameter-scan':   ['--output-dir', '--input-file', '--log-path']
    }

    EXTRACT_TABLE = {
        'generate-config':              ['-o', '--output-file'],
        'extract':                      ['--config-file', '--flip-classifier', '--output-dir'],
        'convert-raw-to-avi':           ['-o', '--output-file'],
        'copy-slice':                   ['-o', '--output-file'],
        'download-flip-file':           ['--output-dir'],
        'find-roi':                     ['--output-dir', '--config-file']
    }

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

def get_environment_path():
    return os.path.join(str(Path.home()), ".config", "moseq2_environment")
#end get_environment_path()

def get_environment_manifest():
    return os.path.join(str(Path.home()), ".config", "moseq2_environment", "environments.tsv")
#end get_environment_manifest()

def get_active_env():
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
    env = get_active_env()

    env_path = os.path.join(get_environment_path(), env, env + '.yml')
    with open(env_path, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)

    img = contents['ACTIVE_IMAGE']

    if img == None:
        sys.stderr.write('There is no active image. Please activate one before proceeding by typing moseq2-env use-env --help.\n')
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

def get_custom_bind_paths():
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