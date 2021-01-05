import os
import sys
import subprocess
import re
from stat import S_IEXEC

from moseq2_build.utils.mount import mount_dirs
from moseq2_build.utils.constants import Commands
from moseq2_build.utils.extract import place_classifier_in_yaml
from moseq2_build.utils.command import *

def batch(image, flip_path, batch_output, remainder, com_table, command_help=False):
    if 'aggregate-extract-results' in remainder:
        mount_com = mount_dirs(remainder, com_table['mount'], Commands.BATCH_TABLE['aggregate-extract-results'])
    else:
        mount_com = mount_dirs(remainder, com_table['mount'], Commands.BATCH_TABLE['batch'])

    if command_help == True:
        remainder.append('--help')
        bash_command = " bash -c 'source activate moseq2; moseq2-batch " + ' '.join(remainder) + ";'"
        final_command = com_table["exec"] + ' ' + image + bash_command

        process = subprocess.Popen(final_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        check_stderr(error)
        check_stdout(output)
        return

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
        sys.stderr.write('config.yaml has successfully been created at {}'.format(os.getcwd()))

    bash_command = " bash -c 'source activate moseq2; moseq2-batch " + ' '.join(remainder) + config_file + "'"
    final_command = com_table["exec"] + ' ' + mount_com + ' ' + image + bash_command

    process = subprocess.Popen(final_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    check_stderr(error)
    check_stdout(output)

    if 'extract-batch' in remainder and 'slurm' in remainder:
        out = output.decode('utf-8')
        final_command = ''
        with open('run_batch.sh', 'w') as f:
            for line in out.split('\n'):
                commandList = re.findall(r'"([^"]*)', line)

                if len(commandList) != 0:
                    com = commandList[0]
                    t = com_table["exec"] + ' ' + mount_com + ' ' + image + ' bash -c \'' + com
                    line = line.replace(com, t)
                    line = line[:-1] + "\'\";\n"
                    final_command += line
            f.write(final_command + '\n')
            outputPath = os.path.join(batch_output, 'run_batch.sh') # just in case we have been passed a location for batch script
            os.chmod(outputPath, S_IEXEC | os.stat(outputPath).st_mode)
#end batch()