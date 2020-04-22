import argparse
import ruamel.yaml as yaml
import os, sys, re
from stat import S_IEXEC

DEFAULT_FLIP_PATH = '/moseq2_data/flip_files/flip_classifier/flip_classifier_k2_c57_10to13weeks.pkl'
BATCH_TABLE = {'extract-batch': ['--input-dir', '-i', '--config-file', '-c', '--filename']}
EXTRACT_TABLE = {'generate-config': ['-o', '--output-file'],
                 'extract': ['--config-file', '--flip-classifier']}

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Extract related arguments
    parser_extract = subparsers.add_parser('moseq2-extract')
    
    # Singularity specific arguments
    parser_extract.add_argument('--singularity-image', nargs='?', help='Location for the singularity image file.', dest='singularity_image_path', default='', type=str, const=True)

    # Docker specific arguments
    parser_extract.add_argument('--docker-image', nargs='?', help='Location for the docker image file.', dest='docker_image_path', default='', type=str, const=True)

    parser_extract.add_argument('remainder', nargs=argparse.REMAINDER)
    parser_extract.set_defaults(func=extract_entrypoint)

    
    # Batch related arguments
    parser_batch = subparsers.add_parser('moseq2-batch')
    
    # Singularity specific arguments
    parser_batch.add_argument('--singularity-image', nargs='?', help='Location for the singularity image file.', dest='singularity_image_path', default='', type=str, const=True)

    # Docker specific arguments
    parser_batch.add_argument('--docker-image', nargs='?', help='Location for the docker image file.', dest='docker_image_path', default='', type=str, const=True)

    parser_batch.add_argument('remainder', nargs=argparse.REMAINDER)
    parser_batch.set_defaults(func=batch_entrypoint)

    args = parser.parse_args()
    args.func(args)
    return 0
#end main()

def batch_entrypoint(args):
    if args.singularity_image_path is not '':
        singularity_batch(args)
    elif args.docker_image_path is not '':
        docker_batch(args)
    else:
        print("Please pass in the path to either the docker image or singularity image.")
        exit(0)
#end batch_entrypoint()

def singularity_batch(args):
    # Loop thru the remaining args
    pathKeys = []
    mountCommand = ''
    for param in BATCH_TABLE[args.remainder[0]]:
        if param in args.remainder:
            idx = args.remainder.index(param) + 1
            pathKeys.append(os.path.abspath(args.remainder[idx]))

    # Get the longest pathname that is common between all of the paths
    if len(pathKeys) != 0:
        longestCommonPath = os.path.dirname(os.path.commonprefix(pathKeys))

        if longestCommonPath == "\\" or longestCommonPath == "/":
            print("Common path is root directory, so it will not be mounted.")
        else:
            mountCommand = "-B" + " " + longestCommonPath

    # See if there was not a config file that was passed in
    if '-c' not in args.remainder and '--config-file' not in args.remainder:
        print("Please pass in a config file to be used during extraction. To generate one, type moseq2-extract --help.")
        exit(0)

    # Write out the command
    with open('temp.sh', 'w') as f:
        f.write('source activate moseq2\n')
        command = "moseq2-batch " + ' '.join(args.remainder)
        f.write(command + '\n')

    finalCommand = "singularity exec " + mountCommand + " " + args.singularity_image_path + " bash temp.sh"
    stream = os.popen(finalCommand)
    output = stream.read()

    # We need to alter how this output looks so that it will call a singularity command.
    if 'extract-batch' in args.remainder and 'slurm' in args.remainder:
        
        if not os.path.isdir('slurmTempFiles'):
            os.mkdir('slurmTempFiles')
        tempFileNumber = 1
        with open('run_batch.sh', 'w') as com:
            for line in output.split('\n'):
                # Extract command part from the wrap command so it can be dumped in a temp file
                commandList = re.findall(r'"([^"]*)"', line)

                if len(commandList) != 0:
                    command = commandList[0]
                    fname = 'slurmTempFiles/temp' + str(tempFileNumber) + '.sh'
                    tempFileNumber += 1
                    with open(fname, 'w') as f:
                        f.write(command)
                    t = "singularity exec " + mountCommand + " " + args.singularity_image_path + " bash " + fname
                    line = line.replace(command, t)
                    com.write(line + '\n')
                os.chmod('run_batch.sh', S_IEXEC | os.stat('run_batch.sh').st_mode)

    else:
        print(output)

    print("Command was completed successfully.")
    
    os.remove('temp.sh')
#end singularity_batch()

def docker_batch(args):
    pass
#end docker_batch()

def extract_entrypoint(args):
    print(args.singularity_image_path)
    if args.singularity_image_path is not '':
        singularity_extract(args)
    elif args.docker_image_path is not '':
        docker_extract(args)
    else:
        print("Please pass in the path to either the docker image or the singularity image.")
        exit(0)
#end singularity_extract()

def docker_extract(args):
    print('docker')
#end docker_extract()

def singularity_extract(args):
    # Loop thru remaining args to see what was called
    pathKeys = []
    mountCommand = ''
    for param in EXTRACT_TABLE[args.remainder[0]]:
        if param in args.remainder:
            idx = args.remainder.index(param) + 1
            if idx >= len(args.remainder):
                print("Please make sure each param has a valid argument.")
                exit(0)
            pathKeys.append(os.path.abspath(args.remainder[idx]))

    # Get the longest pathname that is common between all of the paths pased in.
    if len(pathKeys) != 0:
        longestCommonPath = os.path.dirname(os.path.commonprefix(pathKeys))

        if longestCommonPath == "\\" or longestCommonPath == "/":
            print("Common path is root directory, so it will not be mounted.")

        else:
            mountCommand = "-B" + " " + longestCommonPath

    # Write out the command and execute it in singularity
    with open('temp.sh', 'w') as f:
        f.write('source activate moseq2\n')
        command = "moseq2-extract " + ' '.join(args.remainder)
        f.write(command + '\n')

    finalCommand = "singularity exec " + mountCommand + " " + args.singularity_image_path + " bash temp.sh"
    stream = os.popen(finalCommand)
    output = stream.read()
    print(output)

    # Update the flip classifier path
    if 'generate-config' in args.remainder:
        configPath = "config.yaml"
        if '-o' in args.remainder:
            idx = args.remainder.index('-o') + 1
            configPath = args.remainder[idx]
        elif '--output-file' in args.remainder:
            idx = args.remainder.index('--output-file') + 1
            configPath = args.remainder[idx]

        place_classifier_in_yaml(configPath, DEFAULT_FLIP_PATH)

    print("Command finished successfully.")

    os.remove('temp.sh')
#end singularity_entrypoint()

def place_classifier_in_yaml(configPath, flipPath):
    with open(configPath, 'r') as f:
        contents = yaml.safe_load(f)
        contents['flip_classifier'] = flipPath

    with open(configPath, 'w') as f:
        yaml.dump(contents, f, Dumper=yaml.RoundTripDumper)
#end place_classifier_in_yaml()

if __name__ == '__main__':
    main()

