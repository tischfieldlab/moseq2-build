import os
import sys
import subprocess
import re
from stat import S_IEXEC

from moseq2_build.utils.mount import *
from moseq2_build.utils.constants import Commands, get_classifier_path
from moseq2_build.utils.extract import place_classifier_in_yaml
from moseq2_build.utils.command import *

def batch(image, flip_path, batch_output, mount_dirs_list, remainder, com_table):
    # Field the help commands first.
    if '-h' in remainder or '--help' in remainder:
        bash_command = " bash -c 'source activate moseq2; moseq2-batch " + ' '.join(remainder) + ";'"
        final_command = com_table["exec"] + ' ' + image + bash_command

        process = subprocess.Popen(final_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        check_stderr(error)
        check_stdout(output)
        return

    mount_com = mount_additional_dirs(mount_dirs_list, com_table['mount']) + ' '

    # Figure out if we are running a command that needs to be mounted
    for v in remainder:
        if v in Commands.BATCH_TABLE.keys():
            mount_com += mount_dirs(remainder, com_table['mount'], Commands.BATCH_TABLE[v])

    # Call into specific functions for each entry point to free up this funciton
    bash_command = ''
    if 'extract-batch' in remainder:
        bash_command = handle_extract_batch(image, flip_path, mount_com, remainder, com_table)
    else:
        bash_command = handle_entry_points(remainder)

    final_command = com_table["exec"] + ' ' + mount_com + ' ' + image + bash_command

    process = subprocess.Popen(final_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    check_stderr(error)
    check_stdout(output)

    if 'extract-batch' in remainder and 'slurm' in remainder:
        format_stdout_from_extract_batch(remainder, output, com_table, mount_com, image)
#end batch()

def handle_entry_points(remainder):
    bash_command = " bash -c 'source activate moseq2; moseq2-batch " + ' '.join(remainder) + "'"
    return bash_command
#end handle_aggregate_extract()

def handle_extract_batch(image, flip_path, mount_com, remainder, com_table):
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