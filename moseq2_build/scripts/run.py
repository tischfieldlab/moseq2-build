import argparse

from moseq2_build.utils.constants import *
from moseq2_build.utils.batch import batch
from moseq2_build.utils.extract import extract
import sys

def main():
    parser = argparse.ArgumentParser(add_help=False)
    subparsers = parser.add_subparsers()

    # Batch parser
    batch_parser = subparsers.add_parser('batch', help='Run batch commands through the image file.', add_help=False)
    batch_parser.add_argument('--image', default=get_active_image(), type=str, help='Path to the image to execute commands in.')
    batch_parser.add_argument('--flip-path', default=DEFAULT_FLIP_FILE, type=str, help='Path to the flip file to use.')
    batch_parser.add_argument('--batch-output', default=os.getcwd(), type=str, help='Location for which the batched command script will be output to.')
    batch_parser.add_argument('--mount-dir', action='append', help='Directory paths to be mounted inside the image being used to execute commands.', type=str)
    batch_parser.set_defaults(function=batch_parser_func)

    # Extract parser
    extract_parser = subparsers.add_parser('extract', help='Run extract commands through the image file.', add_help=False)
    extract_parser.add_argument('--image', default=get_active_image(), type=str, help='Path to the image to execute commands in.')
    extract_parser.add_argument('--flip-path', default=DEFAULT_FLIP_FILE, type=str, help='Path to the flip file to be used during extraction.')
    extract_parser.add_argument('--mount-dir', action='append', help='Directory paths to be mounted inside the image being used to execute commands.' +
        '-m must be prefixed before each mounted directory.', type=str)
    extract_parser.set_defaults(function=extract_parser_func)

    args, unknown = parser.parse_known_args()
    # Check if the help flag is passed in by itself, we need to intercept this here, before it gets to the actual argument functions.
    # Reason being, moseq2-run --help needs to print the help functions for all the underlying scripts as the --help flag passed for
    # each script will trigger the help call inside the image, not for the wrapper method that exists in this file.
    if len(sys.argv) > 1:
        if sys.argv[1] == '-h' or sys.argv[1] == '--help':
            parser.print_help()
            sys.stdout.write('\n---------------------------- COMMANDS FOR BATCH ----------------------------\n\n')
            batch_parser.print_help()
            sys.stdout.write('----------------------------------------------------------------------------\n\n')
            sys.stdout.write('---------------------------- COMMANDS FOR EXTRACT --------------------------\n\n')
            extract_parser.print_help()
            sys.stdout.write('----------------------------------------------------------------------------\n')
            return

    try:
        args.function(args, unknown)
    except:
        pass
#end main()

def batch_parser_func(args, unknown):
    """Wrapper function for all moseq2-batch entry points.

    Args:
        args (ArgParse Arguments): List of arguments from argparse.
        unknown (ArgParse UnknownArguments): List of miscellaneous arguments from argparse.
    """
    assert (args.image is not None)
    assert (args.flip_path is not None)
    assert (args.batch_output is not None)

    # We need to make sure the flip path passed in is mounted.
    args.flip_path = mount_flip_path(args.flip_path)

    file_commands = None
    # The case of Singularity
    if args.image.endswith('.sif'):
        sys.stderr.write('Detected Singularity image {} using environment {}\n'.format(os.path.basename(args.image), get_active_env()))
        # Bind the file commands to be the list of Singularity Commands
        file_commands = Commands.SINGULARITY_COMS

        # Get the list of commands we care about in terms of path binding and mounting of directories in files.
        table = get_argtable(Commands.SINGULARITY_COMS, args.image)
    # The case of Docker
    else:
        sys.stderr.write('Docker not supported at the moment...')
        exit(1)

    # Call into the wrapper function that handles all execution of commands for moseq2-batch to be invoked in the image.
    batch(args.image, args.flip_path, args.batch_output, args.mount_dir, unknown, file_commands, table)
#end batch_parser_func()

def extract_parser_func(args, remainder):
    """Wrapper function for all moseq2-extract entry points.

    Args:
        args (ArgParse Arguments): List of arguments from argparse.
        unknown (ArgParse UnknownArguments): List of miscellaneous arguments from argparse.
    """
    assert (args.image is not None)
    assert (args.flip_path is not None)

    # We need to make sure the flip path passed in is mounted.
    args.flip_path = mount_flip_path(args.flip_path)

    file_commands = None
    # Singularity Cacse
    if (args.image.endswith('.sif')):
        sys.stderr.write('Detected Singularity image {} using environment {}\n'.format(os.path.basename(args.image), get_active_env()))
        file_commands = Commands.SINGULARITY_COMS
        table = get_argtable(Commands.SINGULARITY_COMS, args.image)
    # Docker case
    else:
        sys.stderr.write('Docker not supported at the moment...')
        exit(1)

    # Call into the extract wrapper function that handles all processes for moseq2-extract invoked inside the image.
    extract(args.image, args.flip_path, args.mount_dir, remainder, file_commands, table)
#end extract_parser_func()

def mount_flip_path(flip_path):
    """Helper function used to mount file paths.

    Args:
        flip_path (string): Path to the flip file to be used in various entry points in the moseq2 pipeline.

    Returns:
        string: Mounted filepath to either be inside the image, or to be outside the image.
    """
    if os.path.isfile(flip_path):
        return flip_path
    else:
        # The / is hardcoded since all paths relative to the image use /
        return get_classifier_path() + '/' + flip_path
#end mount_flip_path()

if __name__ == "__main__":
    main()
