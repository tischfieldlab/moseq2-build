import subprocess
import re

from moseq2_build.utils.command import *
from moseq2_build.utils.constants import *
from moseq2_build.utils.mount import mount_additional_dirs, mount_dirs

def extract(image, flip_path, mount_dirs_list, remainder, command_table, argtable):
    """Wrapper function for all moseq2-extract operations.

    Args:
        image (string): Path to the image to do work in.
        flip_path (string): Path to the flip file to use, if needed.
        mount_dirs_list (string[]): List of directories to mount. This pulls from CUSTOM_BIND_PATHS in the environment file.
        remainder (ArgParse UnkownArguments): List of unkown arguments to be passed to the image file as arguments to the script.
        command_table (Dictionary <string, string>): Table of commands that are determined by the passed image file.
        argtable (Dictionary <string, string>: List of arguments we care about that can result in mounting inside the image.
    """

    # Field the help commands first.
    if '-h' in remainder or '--help' in remainder:
        extract_command = " bash -c 'source activate moseq2; moseq2-extract " + ' '.join(remainder) + ";'"
        final_command = command_table["exec"] + ' ' + image + extract_command

        process = subprocess.Popen(final_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        check_stderr(error)
        check_stdout(output)
        return

    # Generate the mount command based on the mount directories passed in and the mount command bound based on the image.
    mount_com = mount_additional_dirs(mount_dirs_list, command_table['mount']) + ' '

    # Figure out if we are running a command that needs to be mounted
    for v in remainder:
        if v in argtable.keys():
            # Add mount directories if we find that passed in arguments are to be mounted.
            mount_com += mount_dirs(remainder, command_table['mount'], argtable[v])

    # Get the bash command to execute using subprocess that is based on the passed in arguments.
    bash_com = handle_entry_points(remainder)

    # Format the final command with the appropriate mounts, image, and subsequent image exec command.
    final_com = command_table['exec'] + ' ' + mount_com + ' ' + image + bash_com

    process = subprocess.Popen(final_com, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    check_stderr(error)
    check_stdout(output)

    if 'generate-config' in remainder:
        handle_generate_config(remainder, flip_path)
#end extract()

def handle_entry_points(remainder):
    bash_command = " bash -c 'source activate moseq2; moseq2-extract " + ' '.join(remainder) + "'"
    return bash_command
#end handle_entry_points()

def handle_generate_config(remainder, flip_path):
    """Places the passed in flip path into the generated config automatically.

    Args:
        remainder (ArgParse UnkownArguments): List of unkown arguments to be passed to the image file as arguments to the script.
        flip_path (string): Path to the flip file to use, if needed.
    """
    configPath = 'config.yaml'
    if '-o' in remainder:
        idx = remainder.index('-o') + 1
        assert(idx < len(remainder))
        configPath = remainder[idx]
    elif '--output-file' in remainder:
        idx = remainder.index('--output-file') + 1
        assert(idx < len(remainder))
        configPath = remainder[idx]

    place_classifier_in_yaml(os.path.abspath(configPath), flip_path)
#end handle_generate_config()

def place_classifier_in_yaml(config, flip):
    """Places the passed in flip path into the generated config automatically.

    Args:
        config (string): Path to the config file to be altered.
        flip (string): Path to the flip file to be added to the config file.
    """
    with open(config, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)
    
    contents['flip_classifier'] = flip

    with open(config, 'w+') as f:
        yaml.dump(contents, f)
#end place_classifier_in_yaml()