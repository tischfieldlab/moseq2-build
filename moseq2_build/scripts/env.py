import argparse
import tabulate
import shutil
import yaml

from argparse import Namespace
from moseq2_build.utils.manifest import *
from moseq2_build.utils.image import *
from moseq2_build.utils.constants import get_image_paths
from moseq2_build.scripts.image import download_image_func

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    env_parser = subparsers.add_parser('env', help='Contains all of the environment operations for the moseq2'
                                                   ' environment')
    env_subparsers = env_parser.add_subparsers()

    # Create environment parser
    create_env_parser = env_subparsers.add_parser('create')
    create_env_parser.add_argument('-n', '--name', type=str, help='The name of the environment that is to be created.',
                                   default=None, required=True)
    create_env_parser.add_argument('--set-active-env', action='store_true', help='Set the new environment to be the active one.')
    create_env_parser.add_argument('--set-active-image', action='store_true', help='Set the new image to be the active one.')
    create_env_parser.add_argument('-d', '--download-image', choices=['singularity', 'docker', 'all'], required=False, help='Specify an image to download.')
    create_env_parser.set_defaults(function=create_env_func)

    # Delete environment parser
    delete_env_parser = env_subparsers.add_parser('delete')
    delete_env_parser.add_argument('-n', '--name', type=str, default=None, required=True, help='Name of the environment to delete.')
    delete_env_parser.set_defaults(function=delete_env_func)

    # List environment parser
    list_env_parser = env_subparsers.add_parser('list')
    list_env_parser.add_argument('-a', '--active-only', action='store_true', help='Return back the active environment only.')
    list_env_parser.set_defaults(function=list_env_func)

    # Activate environment parser
    activate_env_parser = env_subparsers.add_parser('activate')
    activate_env_parser.add_argument('-n', '--name', type=str, default=None, required=True, help='Name of the environment to be active.')
    activate_env_parser.set_defaults(function=activate_env_func)

    # Deactivate environment parser
    deactivate_env_parser = env_subparsers.add_parser('deactivate')
    deactivate_env_parser.add_argument('-n', '--name', type=str, default=None, required=True, help='Name of the environment to be active.')
    deactivate_env_parser.set_defaults(function=deactivate_env_func)

    args = parser.parse_args()
    args.function(args)
#end main()

def create_env_func(args):
    assert (args.name is not None)

    # Make sure the manifest file exists
    if is_manifest_created() is False:
        sys.stderr.write('Manifest file is not created, so creating one now.\n')
        create_manifest_file()

    # Insert into the manifest
    res = put_in_manifest(args.name, args.set_active_env)

    # Create the environment file if we successfully put in the entry
    if res is True:
        os.mkdir(os.path.join(get_environment_path(), args.name))
        f_path = os.path.join(get_environment_path(), args.name, args.name + '.yml')
        with open(f_path, 'w') as f:
            cons = {"GITHUB_PAT": None, "IMAGE_PATHS": None, "ACTIVE_IMAGE": None}
            yaml.dump(cons, f)
        sys.stderr.write('Environment config created at {}.\n'.format(f_path))

        if args.download_image:
            download_args = Namespace(name=args.name, image=args.download_image,
                set_active=args.set_active_image)
            download_image_func(download_args)
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
    set_active_row(args.name, True)
#end activate_env_func()

def deactivate_env_func(args):
    assert (args.name is not None)
    set_active_row(args.name, False)
#end deactivate_env_func()

if __name__ == '__main__':
    main()