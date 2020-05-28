import os, ruamel.yaml as yaml
from termcolor import colored

from moseq2_build.utils.constants import getDefaultImage, DEFAULT_FLIP_PATH, SINGULARITY_COMS, EXTRACT_TABLE
from moseq2_build.utils.commands import executeCommand, panicIfStderr
from moseq2_build.utils.mount import mountDirectories

def doExtract(image, flip_path, remainder, command):
    if 'generate-config' in remainder:
        tab = EXTRACT_TABLE['generate-config']
    else:
        tab = EXTRACT_TABLE['extract']
    mountCommand = mountDirectories(remainder, command['mount'], tab)
    print(mountCommand)

    bashCommand = " bash -c 'source activate moseq2; moseq2-extract " + ' '.join(remainder) + "'"
    print(bashCommand)
    finalCommand = command['exec'] + ' ' + mountCommand + ' ' + image + bashCommand
    print(finalCommand)

    result, retCode = executeCommand(finalCommand)
    panicIfStderr(retCode, result, 'Executed extract command\n')

    if ('generate-config' in remainder):
        configPath = 'config.yaml'
        if '-o' in remainder:
            idx = remainder.index('-o') + 1
            assert(idx < len(remainder))
            configPath = remainder[idx]
        elif '--output-file' in remainder:
            idx = remainder.index('--output-file') + 1
            assert(idx < len(remainder))
            configPath = remainder[idx]
        placeClassifierInYaml(os.path.abspath(configPath), flip_path)

    if len(result[0]) != 0:
        print(result[0].decode('utf-8'))
#end do_extract()

def placeClassifierInYaml(configPath, flipPath):
    with open(configPath, 'r') as f:
        contents = yaml.safe_load(f)
        contents['flip_classifier'] = flipPath
    with open(configPath, 'w') as f:
        yaml.dump(contents, f, Dumper=yaml.RoundTripDumper)
#end placeClassifierInYaml()
