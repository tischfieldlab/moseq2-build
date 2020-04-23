import argparse
import ruamel.yaml as yaml
from termcolor import colored
import os, sys, re, time, subprocess, threading
from stat import S_IEXEC

doneWorking = False

DEFAULT_FLIP_PATH = '/moseq2_data/flip_files/flip_classifier/flip_classifier_k2_c57_10to13weeks.pkl'
BATCH_TABLE = {'extract-batch': ['--input-dir', '-i', '--config-file', '-c', '--filename']}
EXTRACT_TABLE = {'generate-config': ['-o', '--output-file'],
                'extract': ['--config-file', '--flip-classifier']}
SINGULARITY_COMS = {'exec': 'singularity exec', 'mount': '-B'}

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title="moseq2 cli entrypoints.", dest="command")
    subparserList = []
    
    parser_extract = subparsers.add_parser('moseq2-extract')
    parser_batch = subparsers.add_parser('moseq2-batch')

    subparserList.append(parser_extract)
    subparserList.append(parser_batch)

    arguments = [
            (('--path', '-p'), {'default':None, 'nargs':'?','help':'Location of the image file to be used.',
                'dest':'imagePath'}),
            (('remainder',), {'nargs':argparse.REMAINDER})
            ]

    for p in subparserList:
        for pos, keyword in arguments:
            p.add_argument(*pos, **keyword)
            p.set_defaults(func=entrypoint)

    args = parser.parse_args()
    args.func(args)
#end main()

def entrypoint(args):

    fileCommands = None

    if (args.imagePath is None):
        print(colored("Path not passed in...", 'red'))
        exit(1)

    if (args.imagePath.endswith('.sif')):
        print(colored("\nDetected singularity image at {}\n".format(os.path.dirname(os.path.abspath(args.imagePath))),
            'white', attrs=['bold']))
        fileCommands = SINGULARITY_COMS

    # Since Docker doesn't have an extension, we need to figure
    # out if this is a docker file...
    else:
        print("urggg.")

    if (args.command == 'moseq2-batch'):
        handle_batch(args, fileCommands)

    elif (args.command == 'moseq2-extract'):
        handle_extract(args, fileCommands)

    print(colored("\nExiting now\t\t" + u'\u2705', 'green', attrs=['bold']))
#end extract_entrypoint()

def handle_batch(args, command):
    mountCommand = mountDirectories(args, command["mount"], BATCH_TABLE)

    configFile = ''
    if ('-c' not in args.remainder and '--config-file' not in args.remainder):
        print(colored("No config file was passed in... generating one now.\n", 'yellow'))
        bashCommand = " bash -c 'source activate moseq2; moseq2-extract generate-config;'"
        configCommand = command["exec"] + ' ' + mountCommand + ' ' + args.imagePath + bashCommand
        result = executeCommand(configCommand)

        if (len(result[1]) != 0):
            print(colored("\nConfig file generated\t" + u'\u274C', 'red', attrs=['bold']))
            exit(1)
        else:
            place_classifier_in_yaml("config.yaml", DEFAULT_FLIP_PATH)
            configFile = " -c config.yaml"
            print(colored("\nConfig file generated\t" + u'\u2705', 'green', attrs=['bold']))

    bashCommand = " bash -c 'source activate moseq2; moseq2-batch " + ' '.join(args.remainder) + configFile + "'"
    finalCommand = command["exec"] + ' ' + mountCommand + ' ' + args.imagePath + bashCommand
    result = executeCommand(finalCommand)

    if (len(result[1]) != 0):
        print(colored('Executed batch command\t' + u'\u274C', 'red', attrs=['bold']))
        print(result[1].decode('utf-8'))
        exit(1)

    if ('extract-batch' in args.remainder and 'slurm' in args.remainder):
        output = result[0].decode('utf-8')
        finalCommand = ''
        with open('run_batch.sh', 'w') as f:
            for line in output.split('\n'):
                commandList = re.findall(r'"([^"]*)', line)

                if len(commandList) != 0:
                    com = commandList[0]
                    t = command["exec"] + ' ' + mountCommand + ' ' + args.imagePath + ' bash -c \'' + com
                    line = line.replace(com, t)
                    line = line[:-1] + "\'\";\n"
                    finalCommand += line
            f.write(finalCommand + '\n')
            os.chmod('run_batch.sh', S_IEXEC | os.stat('run_batch.sh').st_mode)

    print(colored('Executed batch command\t' + u'\u2705', 'green', attrs=['bold']))
#end handle_batch()

def handle_extract(args, command):
    mountCommand = mountDirectories(args, command["mount"], EXTRACT_TABLE)

    bashCommand = " bash -c 'source activate moseq2; moseq2-extract " + ' '.join(args.remainder) + "'"
    finalCommand = command["exec"] + ' ' + mountCommand + ' ' + args.imagePath + bashCommand
    result = executeCommand(finalCommand)

    if (len(result[1]) != 0):
        print(colored('Executed extract command\t' + u'\u274C', 'red', attrs=['bold']))
        exit(1)

    # If this is a config file command, we need to place in the path
    # in the docker/singularity environment
    if ('generate-config' in args.remainder):
        configPath = 'config.path'
        if '-o' in args.remainder:
            idx = args.remainder.index('-o') + 1
            assert(idx < len(args.remainder))
            configPath = args.remainder[idx]
        elif '--output-file' in args.remainder:
            idx = args.remainder.index('--output-file') + 1
            assert(idx < len(args.remainder))
            configPath = args.remainder[idx]

        place_classifier_in_yaml(configPath, DEFAULT_FLIP_PATH)
    print(colored('Executed extract command\t' + u'\u2705', 'green', attrs=['bold']))
#end handle_extract()

def executeCommand(command):
    done = False
    spin_thread = threading.Thread(target=spinCursor)
    spin_thread.start()

    proc = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE,
            stdin=subprocess.PIPE, shell=True)
    contents = proc.communicate()

    global doneWorking
    doneWorking = True
    spin_thread.join()
    doneWorking = False

    return contents
#end executeCommand()

def mountDirectories(args, mountString, table):
    pathKeys = []
    mountCommand = ''
    if (len(args.remainder) == 0):
        return ''

    for param in table[args.remainder[0]]:
        if param in args.remainder:
            idx = args.remainder.index(param) + 1
            if idx >= len(args.remainder):
                print("Please make sure each paramater has a valid argument.")
                exit(1)

            pathKeys.append(os.path.abspath(args.remainder[idx]))

    # Get the longest pathname common for all paths passed in
    if (len(pathKeys) != 0):
        longestCommonPath = os.path.dirname(os.path.commonprefix(pathKeys))

        if (longestCommonPath == "\\" or longestCommonPath == "/"):
            print("Common path is the root directory, so it will not be mounted.")

        else:
            mountCommand = mountString + " " + longestCommonPath

    return mountCommand
#end mountDirectories()

def spinCursor():
    global doneWorking
    sys.stdout.flush()
    sys.stdout.write(colored("Executing commands ", "red", attrs=['bold']))
    while True:
        for cursor in '|/-\\':
            time.sleep(0.1)
            sys.stdout.write(colored("\rExecuting commands " + cursor, "red", attrs=['bold']))
            sys.stdout.flush()
            if doneWorking:
                sys.stdout.write('\n')
                sys.stdout.write('\033[F')
                sys.stdout.write('\033[K')
                return
#end spinCursor()

def place_classifier_in_yaml(configPath, flipPath):
    with open(configPath, 'r') as f:
        contents = yaml.safe_load(f)
        contents['flip_classifier'] = flipPath

    with open(configPath, 'w') as f:
        yaml.dump(contents, f, Dumper=yaml.RoundTripDumper)
#end place_classifier_in_yaml()

if __name__ == '__main__':
    main()
