import subprocess

from moseq2_build.utils.command import *
from moseq2_build.utils.constants import *
from moseq2_build.utils.mount import mount_dirs

def extract(image, flip_path, remainder, command_table):
    assert (len(command_table) != 0)

    if 'generate-config' in remainder:
        tab = Commands.EXTRACT_TABLE['generate-config']
    else:
        tab = Commands.EXTRACT_TABLE['extract']

    mount_com = mount_dirs(remainder, command_table['mount'], tab)

    bash_com = " bash -c 'source activate moseq2; moseq2-extract " + ' '.join(remainder) + "'"
    final_com = command_table['exec'] + ' ' + mount_com + ' ' + image + bash_com

    process = subprocess.Popen(final_com, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output, error = process.communicate()

    check_stderr(error)
    check_stdout(output)

    if ('generate-config' in remainder and inner_help is False):
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
#end extract()

def place_classifier_in_yaml(config, flip):
    with open(config, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)
    
    contents['flip_classifier'] = flip

    with open(config, 'w+') as f:
        yaml.dump(contents, f)
#end place_classifier_in_yaml()