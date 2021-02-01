import os
from os import path
import sys
import yaml

from moseq2_build.utils.constants import get_classifier_path

def mount_dirs(remainder, mount_string, com_table):
    pathKeys = []
    mount_com = ''
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
                        if contents['flip_classifier'] and os.path.isfile(contents['flip_classifier']):
                            pathKeys.append(os.path.abspath(contents['flip_classifier']))
                        if contents['output_dir'] and os.path.isfile(contents['output_dir']):
                            pathKeys.append(os.path.abspath(contents['output_dir']))
                    except:
                        pass

            # Check if file exists on OS, if it does, add it to the mount command
            if os.path.isfile(remainder[idx]) or os.path.isdir(remainder[idx]):
                pathKeys.append(os.path.abspath(remainder[idx]))

    for i in range(len(pathKeys)):
        if pathKeys[i] == os.path.abspath(os.sep):
            sys.stderr.write('Mount string passed in is the root directory, so we are skipping mounting it.\n')
            continue
        if i == 0:
            mount_com = mount_string + ' ' + pathKeys[i]
        else:
            mount_com += ',' + pathKeys[i]

    return mount_com
#end mount_dirs()
