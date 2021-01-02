import argparse
import tabulate
import shutil

from moseq2_build.utils.manifest import *
from moseq2_build.utils.image import *
from moseq2_build.utils.constants import get_image_paths

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    env_parser = subparsers.add_parser('env', help='Contains all of the environment operations for the moseq2'
                                                   ' environment')
    env_subparsers = env_parser.add_subparsers()

    # Create environment parser
    create_env_parser = env_subparsers.add_parser('create-env')
    create_env_parser.add_argument('-n', '--name', type=str, help='The name of the environment that is to be created.',
                                   default=None, required=True)
    create_env_parser.add_argument('--set-active', action='store_true', help='Set the new environment to be the active one.')
    create_env_parser.set_defaults(function=create_env_func)

    # Delete environment parser
    delete_env_parser = env_subparsers.add_parser('delete-env')
    delete_env_parser.add_argument('-n', '--name', type=str, default=None, required=True, help='Name of the environment to delete.')
    delete_env_parser.set_defaults(function=delete_env_func)

    # List environment parser
    list_env_parser = env_subparsers.add_parser('list')
    list_env_parser.add_argument('-a', '--active-only', action='store_true', help='Return back the active environment only.')
    list_env_parser.set_defaults(function=list_env_func)

    # Activate environment parser
    activate_env_parser = env_subparsers.add_parser('activate-env')
    activate_env_parser.add_argument('-n', '--name', type=str, default=None, required=True, help='Name of the environment to be active.')
    activate_env_parser.set_defaults(function=activate_env_func)

    # Activate image parser
    activate_image_parser = env_subparsers.add_parser('activate-image')
    activate_image_parser.add_argument('-n', '--name', type=str, default=None, required=True,
        help='The name of the environment to activate the image of.')
    activate_image_parser.add_argument('-i', '--image', type=str, default=None,
        choices=['singularity', 'docker', 'all'], required=True, help='The image to be set to active.')
    activate_image_parser.set_defaults(function=activate_image_func)

    args = parser.parse_args()
    args.function(args)

def create_env_func(args):
    assert (args.name is not None)
    assert (args.set_active is not None)

    # Make sure the manifest file exists
    if is_manifest_created() is False:
        sys.stderr.write('Manifest file is not created, so creating one now.\n')
        create_manifest_file()

    # Insert into the manifest
    res = put_in_manifest(args.name, args.set_active)

    # Create the environment file if we successfully put in the entry
    if res is True:
        os.mkdir(os.path.join(get_environment_path(), args.name))
        f_path = os.path.join(get_environment_path(), args.name, args.name + '.yml')
        open(f_path, 'w').close()
        sys.stderr.write('Environment config created at {}.\n'.format(f_path))

    env_path = os.path.join(get_environment_path(), args.name)
    image_paths = [get_image_paths('singularity'), get_image_paths('docker')]

    # Copy over the images
    unpack_image(env_path, image_paths)

    # Write out the image locations
    
#end create_env_func()

def delete_env_func(args):
    assert (args.name is not None)

    # Make sure the manifest is created
    if is_manifest_created() is False:
        sys.stderr.write('Manifest file is not created, please make sure one is created before deleting.\n')
        exit(1)

    # Delete the entry from the manifest
    res = delete_from_manifest(args.name)

    # If we deleted successfully, remove the file from disk
    if res is True:
        shutil.rmtree(os.path.join(get_environment_path(), args.name))
        sys.stderr.write('The "{}" environment has successfully been removed.\n'.format(args.name))
#end delete_env_func()

def list_env_func(args):
    assert (args.active_only is not None)

    if is_manifest_created() is False:
        sys.stderr.write('No manifest is created, please create one first.\n')
        exit(1)

    man_path = get_environment_manifest()
    contents = [['Name', 'Active']]
    with open(man_path, 'r') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')

        for row in reader:
            if args.active_only is True:
                if row[1] == 'True':
                    contents.append(row)
            else:
                contents.append(row)

    table = tabulate.tabulate(contents, headers='firstrow')
    sys.stdout.write(table)
    sys.stderr.write('\n')
#end list_env_func()

def activate_env_func(args):
    assert (args.name is not None)
    set_active_row(args.name)
#end activate_env_func()

def activate_image_func(args):
    pass
#end activate_image_func()

def setup_images_func(args):
    assert (args.name is not None)
    assert (args.image is not None)

    env_path = os.path.join(get_environment_path(), args.name)

    image_paths = []
    if args.image == 'all':
        image_paths.append(get_image_paths('singularity'))
        image_paths.append(get_image_paths('docker'))
    
    else:
        image_paths.append(get_image_paths(args.image))
    
    unpack_image(env_path, image_paths)


if __name__ == '__main__':
    main()