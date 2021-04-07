import os
from os import path
import sys
import yaml
import re

from moseq2_build.utils.constants import get_custom_bind_paths

def mount_dirs(remainder, mount_string, argtable):
    """Generates a string to be used to mount properly during image invocation.

    Args:
        remainder (ArgParse UnkownArguments): List of unkown arguments to be passed to the image file as arguments to the script.
        mount_string (string): Command prefix or suffix used to mount for a given image.
        argtable (Dictionary <string, string>: List of arguments we care about that can result in mounting inside the image.

    Returns:
        string: Flattened list of mount directories correctly formatted for the image in use.
    """
    pathKeys = []
    if (len(remainder) == 0):
        return ''

    for param in argtable:
        if param in remainder:
            idx = remainder.index(param) + 1
            if idx >= len(remainder):
                sys.stderr.write('Please make sure each parameter has a valid value.\n')
                exit(1)

            # Check if file exists on OS, if it does, add it to the mount command
            if os.path.isdir(remainder[idx]) and remainder[idx] not in pathKeys:
                pathKeys.append(os.path.abspath(remainder[idx]))
            elif os.path.isfile(remainder[idx]):
                pathKeys.append(os.path.dirname(os.path.abspath(remainder[idx])))

    return compute_mount_com(pathKeys, mount_string)
#end mount_dirs()

def mount_additional_dirs(other_dirs, mount_string):
    """Generates mount command for custom bind paths.

    Args:
        other_dirs (list (string)): List of paths gathered from the CUSTOM_BIND_PATHS key in the environment.
        mount_string (string): Command prefix or suffix used to mount for a given image.

    Returns:
        string: Flattened list of mount directories correctly formatted for the image in use.
    """
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
    """Computes the flattened string containing the mount commands for the paths passed in.

    Args:
        pathKeys (list (string)): List of paths to be mounted.
        mount_string (string): Command prefix or suffix used to mount for a given image.

    Returns:
        string: Flattened list of mount directories correctly formatted for the image in use.
    """
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