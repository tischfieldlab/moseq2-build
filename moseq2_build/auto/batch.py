import os
from termcolor import colored

from moseq2_build.utils.constants import BATCH_TABLE
from moseq2_build.utils.mount import mountDirectories
from moseq2_build.utils.commands import executeCommand, printSuccessMessage, panicIfStderr

from moseq2_build.auto.extract import placeClassifierInYaml

def doBatch(image, flip_path, batch_output, remainder, command):
    mountCommand = mountDirectories(remainder, command['mount'], BATCH_TABLE['batch'])
    print(mountCommand)

    configFile = ''
    if ('-c' not in remainder and '--config-file' not in remainder):
        print(colored("No config file was passed in... generating one now.\n", 'yellow'))
        bashCommand = " bash -c 'source activate moseq2; moseq2-extract generate-config;'"
        configCommand = command["exec"] + ' ' + mountCommand + ' ' + image + bashCommand
        result, retCode = executeCommand(configCommand)

        panicIfStderr(retCode, result, "Config file generated\n")
        placeClassifierInYaml("config.yaml", flip_path)
        configFile = " -c config.yaml"
        printSuccessMessage("Config file generated\n")

    bashCommand = " bash -c 'source activate moseq2; moseq2-batch " + ' '.join(remainder) + configFile + "'"
    finalCommand = command["exec"] + ' ' + mountCommand + ' ' + image + bashCommand
    result, retCode = executeCommand(finalCommand)

    panicIfStderr(retCode, result, "Executed batch command\n")

    if ('extract-batch' in remainder and 'slurm' in remainder):
        output = result[0].decode('utf-8')
        finalCommand = ''
        with open('run_batch.sh', 'w') as f:
            for line in output.split('\n'):
                commandList = re.findall(r'"([^"]*)', line)

                if len(commandList) != 0:
                    com = commandList[0]
                    t = command["exec"] + ' ' + mountCommand + ' ' + image + ' bash -c \'' + com
                    line = line.replace(com, t)
                    line = line[:-1] + "\'\";\n"
                    finalCommand += line
            f.write(finalCommand + '\n')
            outputPath = os.path.join(batch_output, 'run_batch.sh') # just in case we have been passed a location for batch script
            os.chmod(outputPath, S_IEXEC | os.stat(outputPath).st_mode)

    if len(result[0]) != 0:
        print(result[0].decode('utf-8'))
#end doBatch()

