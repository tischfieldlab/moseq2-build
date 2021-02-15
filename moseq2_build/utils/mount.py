import os
from os import path
import sys
import yaml
import re

from moseq2_build.utils.constants import get_classifier_path, get_custom_bind_paths

def mount_dirs(remainder, mount_string, com_table):
    pathKeys = []
    if (len(remainder) == 0):
        return ''

    for param in com_table:
        if param in remainder:
            idx = remainder.index(param) + 1
            if idx >= len(remainder):
                sys.stderr.write('Please make sure each parameter has a valid value.\n')
                exit(1)

            # If we get a config path, we need to make sure that the flip file is mounted as well
            if '-c' == param or '--config-file' == param:
                if os.path.isfile(remainder[idx]):
                    with open(remainder[idx], 'r') as f:
                        contents = yaml.load(f, yaml.FullLoader)
                    # If the config classifier is on the host machine, we need to mount it
                    try:
                        if contents['flip_classifier'] and os.path.isfile(contents['flip_classifier']) and contents['flip_classifier'] not in pathKeys:
                            pathKeys.append(os.path.abspath(contents['flip_classifier']))
                        if contents['output_dir'] and os.path.isdir(contents['output_dir']) and contents['output_dir'] not in pathKeys:
                            pathKeys.append(os.path.abspath(contents['output_dir']))
                    except:
                        pass

            # Check if file exists on OS, if it does, add it to the mount command
            if os.path.isdir(remainder[idx]) and remainder[idx] not in pathKeys:
                pathKeys.append(os.path.abspath(remainder[idx]))
            elif os.path.isfile(remainder[idx]):
                pathKeys.append(os.path.dirname(os.path.abspath(remainder[idx])))

    return compute_mount_com(pathKeys, mount_string)
#end mount_dirs()

def mount_additional_dirs(other_dirs, mount_string):
    if other_dirs is None:
        other_dirs = []

    for p in get_custom_bind_paths():
        other_dirs.append(p)

    if len(other_dirs) == 0:
        return ''

    pathKeys = []
    for p in other_dirs:
        # Check if file exists on OS, if it does, add it to the mount command
        if os.path.isdir(p) and p not in pathKeys:
            pathKeys.append(os.path.abspath(p))
        elif os.path.isfile(p) and p not in pathKeys:
            pathKeys.append(os.path.dirname(os.path.abspath(p)))

    return compute_mount_com(pathKeys, mount_string)
#end mount_additional_dirs()

def compute_mount_com(pathKeys, mount_string):
    mount_com = ''
    # Pattern for matching windows root folder
    pattern = re.compile(r'^[a-zA-Z]:\\')
    for i in range(len(pathKeys)):
        if pathKeys[i] == os.path.abspath(os.sep) or pattern.fullmatch(pathKeys[i]) == True:
            sys.stderr.write('Mount string passed in is the root directory, so we are skipping mounting it.\n')
            continue
        if i == 0:
            mount_com = mount_string + ' ' + pathKeys[i]
        else:
            mount_com += ',' + pathKeys[i]

    return mount_com
#end compute_mount_com()