import argparse

from moseq2_build.utils.constants import *
from moseq2_build.utils.batch import batch

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    # Batch parser
    batch_parser = subparsers.add_parser('batch', help='Run batch commands through the image file.')
    batch_parser.add_argument('--image', default=get_active_image(), type=str, help='Path to the image to execute commands in.')
    batch_parser.add_argument('--flip-path', default=DEFAULT_FLIP_FILE, type=str, help='Path to the flip file to use.')
    batch_parser.add_argument('--batch-output', default=os.getcwd(), type=str, help='Location for which the batched command script will be output to.')
    batch_parser.add_argument('--command-help', action='store_true', help='Print the help out from the passed in commands.')
    batch_parser.set_defaults(function=batch_parser_func)

    args, unknown = parser.parse_known_args()
    args.function(args, unknown)
#end main()

def batch_parser_func(args, unknown):
    assert (args.image is not None)
    assert (args.flip_path is not None)
    assert (args.batch_output is not None)

    file_coms = None
    if args.image.endswith('.sif'):
        sys.stderr.write('Detected Singularity image {}\n'.format(os.path.basename(args.image)))
        file_commands = Commands.SINGULARITY_COMS

    batch(args.image, args.flip_path, args.batch_output, unknown, file_commands, args.command_help)
#end batch_parser_func()

if __name__ == "__main__":
    main()