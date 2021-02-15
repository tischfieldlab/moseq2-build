import subprocess
import re

from moseq2_build.utils.command import *
from moseq2_build.utils.constants import *
from moseq2_build.utils.mount import mount_additional_dirs, mount_dirs

def extract(image, flip_path, mount_dirs_list, remainder, command_table):

    # Field the help commands first.
    if '-h' in remainder or '--help' in remainder:
        extract_command = " bash -c 'source activate moseq2; moseq2-extract " + ' '.join(remainder) + ";'"
        final_command = command_table["exec"] + ' ' + image + extract_command

        process = subprocess.Popen(final_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        output, error = process.communicate()

        check_stderr(error)
        check_stdout(output)
        return

    mount_com = mount_additional_dirs(mount_dirs_list, command_table['mount']) + ' '

    # Figure out if we are running a command that needs to be mounted
    for v in remainder:
        if v in Commands.EXTRACT_TABLE.keys():
            mount_com += mount_dirs(remainder, command_table['mount'], Commands.EXTRACT_TABLE[v])

    temp_list = []
    result = re.split(r'[,\s]+', mount_com)
    [temp_list.append(x) for x in result if x not in temp_list]
    if len(temp_list) > 2:
        mount_com = command_table['mount'] + " " + ",".join(temp_list[1:])
    else:
        mount_com = command_table['mount'] + " " + "".join(temp_list[1:])

    bash_com = handle_entry_points(remainder)

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
    with open(config, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)
    
    contents['flip_classifier'] = flip

    with open(config, 'w+') as f:
        yaml.dump(contents, f)
#end place_classifier_in_yaml()