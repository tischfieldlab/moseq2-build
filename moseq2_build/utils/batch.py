import os
import sys
import subprocess
import re

from moseq2_build.utils.mount import *
from moseq2_build.utils.constants import get_classifier_path
from moseq2_build.utils.extract import place_classifier_in_yaml
from moseq2_build.utils.command import *

def batch(image, flip_path, batch_output, mount_dirs_list, remainder, com_table, argtable):
    """Wrapper function that calls into moseq2-batch.

    Args:
        image (string): Path to the image to do work in.
        flip_path (string): Path to the flip file to use, if needed.
        batch_output (string): Mount directory, if passed in.
        mount_dirs_list (string[]): List of directories to mount. This pulls from CUSTOM_BIND_PATHS in the environment file.
        remainder (ArgParse UnkownArguments): List of unkown arguments to be passed to the image file as arguments to the script.
        com_table (Dictionary <string, string>): Table of commands that are determined by the passed image file.
        argtable (Dictionary <string, string>: List of arguments we care about that can result in mounting inside the image.
    """
    # Field the help commands first.
    if '-h' in remainder or '--help' in remainder:
        bash_command = " bash -c 'source activate moseq2; moseq2-batch " + ' '.join(remainder) + ";'"
        final_command = com_table["exec"] + ' ' + image + bash_command

        process = subprocess.Popen(final_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        check_stderr(error)
        check_stdout(output)
        return

    # Generate the mount command based on the mount directories passed in and the mount command bound based on the image.
    mount_com = mount_additional_dirs(mount_dirs_list, com_table['mount']) + ' '

    # Figure out if we are running a command that needs to be mounted
    for v in remainder:
        if v in argtable.keys():
            # Add mount directories if we find that passed in arguments are to be mounted.
            mount_com += mount_dirs(remainder, com_table['mount'], argtable[v])

    # Call into specific functions for each entry point to free up this funciton
    bash_command = ''
    if 'extract-batch' in remainder:
        # Specific call for extract-batch due to quality of life additions.
        bash_command = handle_extract_batch(image, flip_path, mount_com, remainder, com_table)
    else:
        # Any other moseq2-batch entry point gets fielded here.
        bash_command = handle_entry_points(remainder)

    # Format the final command to be passed to subprocess
    final_command = com_table["exec"] + ' ' + mount_com + ' ' + image + bash_command

    # Call the subprocess executing the command and invoking the image.
    process = subprocess.Popen(final_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    check_stderr(error)
    check_stdout(output)

    # If we run extract-batch, we want that output to print on the screen so it can be redirected to a file,
    # thereby mimicing the original functionality.
    if 'extract-batch' in remainder and 'slurm' in remainder:
        format_stdout_from_extract_batch(remainder, output, com_table, mount_com, image)
#end batch()

def handle_entry_points(remainder):
    bash_command = " bash -c 'source activate moseq2; moseq2-batch " + ' '.join(remainder) + "'"
    return bash_command
#end handle_aggregate_extract()

def handle_extract_batch(image, flip_path, mount_com, remainder, com_table):
    """Formats the extract batch command, and creates a config file on the fly if one is not passed in directly.

    Args:
        image (string): Path to the image to do work in.
        flip_path (string): Path to the flip file to use, if needed.
        mount_com (Dictionary <string, string>): Command to mount for the given image passed in.
        remainder (ArgParse UnkownArguments): List of unkown arguments to be passed to the image file as arguments to the script.
        com_table (Dictionary <string, string>): Table of commands that are determined by the passed image file.

    Returns:
        string: Formatted command to run extract-batch.
    """
    # Because sometimes, we don't want to neecessarily pass in the config file, we can generate one automatically.
    # If the user passed in the --flip-file and the --config flags, tell them the config will not be overwritten
    if '-c' in remainder or '--config-file' in remainder:
        test = get_classifier_path() + '/' + os.path.basename(flip_path)
        if flip_path != test:
            sys.stderr.write('WARNING: Flip file and config file have been passed in. Ignoring the flip file so config file will NOT be overwitten.\n')

    config_file = ''
    if '-c' not in remainder and '--config-file' not in remainder and 'extract-batch' in remainder:
        sys.stderr.write('No config file was passed in, so one will be generated at {}\n'.format(os.getcwd()))
        bash_command = " bash -c 'source activate moseq2; moseq2-extract generate-config;'"
        config_command = com_table["exec"] + ' ' + mount_com + ' ' + image + bash_command

        process = subprocess.Popen(config_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        check_stderr(error)
        check_stdout(output)

        place_classifier_in_yaml('config.yaml', flip_path)
        config_file = " -c config.yaml"
        sys.stderr.write('config.yaml has successfully been created at {}\n'.format(os.getcwd()))

    bash_command = " bash -c 'source activate moseq2; moseq2-batch " + ' '.join(remainder) + config_file + "'"
    return bash_command
#end handle_extract_batch()

def format_stdout_from_extract_batch(remainder, output, com_table, mount_com, image):
    """Writes the extract batch output to stdout so that it can be redirected to a file.

    Args:
        remainder (ArgParse UnkownArguments): List of unkown arguments to be passed to the image file as arguments to the script.
        output (byte string): Output from the extract batch command.
        com_table (Dictionary <string, string>): Table of commands that are determined by the passed image file.
        mount_com (Dictionary <string, string>): Command to mount for the given image passed in.
        image (string): Path to the image used to invoke the commands in.
    """
    out = output.decode('utf-8')
    final_command = ''
    for line in out.split('\n'):
        commandList = re.findall(r'"([^"]*)', line)

        if len(commandList) != 0:
            com = commandList[0]
            t = com_table["exec"] + ' ' + mount_com + ' ' + image + ' bash -c \'' + com
            line = line.replace(com, t)
            line = line[:-1] + "\'\";\n"
            final_command += line
        sys.stdout.write(final_command + '\n')
#end format_stdout_from_extract_batch()