import argparse
from os import path
import sys
import tabulate
import shutil
import yaml

from argparse import Namespace
from moseq2_build.utils.manifest import *
from moseq2_build.utils.image import *
from moseq2_build.utils.constants import *

def main():
    parser = argparse.ArgumentParser(description='Contains all of the environment operations for the moseq2'
                                                   ' environment.')
    env_subparsers = parser.add_subparsers()

    # Create environment parser
    create_env_parser = env_subparsers.add_parser('create-env', help='Create a new environment and entry in the global manifest table.')
    create_env_parser.add_argument('-n', '--name', type=str, help='The name of the environment that is to be created.',
                                   default=None, required=True)
    create_env_parser.add_argument('--set-active-env', action='store_true', help='Set the new environment to be the active one.')
    create_env_parser.add_argument('--set-active-image', action='store_true', help='Set the new image to be the active one.')
    create_env_parser.add_argument('-d', '--download-image', choices=['singularity', 'docker', 'all'], required=False, help='Specify an image to download.')
    create_env_parser.set_defaults(function=create_env_func)

    # Delete environment parser
    delete_env_parser = env_subparsers.add_parser('delete-env', help='Delete the environment from the global manifest table.')
    delete_env_parser.add_argument('-n', '--name', type=str, default=None, required=True, help='Name of the environment to delete.')
    delete_env_parser.set_defaults(function=delete_env_func)

    # Current env parser
    curr_env_parser = env_subparsers.add_parser('cur-env', help='Lists the currently active environment.')
    curr_env_parser.set_defaults(function=curr_env_func)

    # List environment parser
    list_env_parser = env_subparsers.add_parser('list-env', help='List all of the environments on this computer.')
    list_env_parser.add_argument('-a', '--active-only', action='store_true', help='Return back the active environment only.')
    list_env_parser.set_defaults(function=list_env_func)

    # Activate environment parser
    activate_env_parser = env_subparsers.add_parser('use-env', help='Activate an environment and load all of its configured values.')
    activate_env_parser.add_argument('-n', '--name', type=str, default=None, required=True, help='Name of the environment to be active.')
    activate_env_parser.set_defaults(function=activate_env_func)

    # Deactivate environment parser
    deactivate_env_parser = env_subparsers.add_parser('deactivate-env', help='Deactivates the current image.')
    deactivate_env_parser.add_argument('-n', '--name', type=str, default=None, required=True, help='Name of the environment to be active.')
    deactivate_env_parser.set_defaults(function=deactivate_env_func)

    # Activate image
    activate_image_parser = env_subparsers.add_parser('use-image', help='Activate an image downloaded for the environment.')
    activate_image_parser.add_argument('-n', '--name', type=str, default=None, required=True,
        help='The name of the environment to activate the image of.')
    activate_image_parser.add_argument('-i', '--image', type=str, default=None,
        choices=['singularity', 'docker'], required=True, help='The image to be set to active.')
    activate_image_parser.set_defaults(function=activate_image_func)

    # Download image
    download_image_parser = env_subparsers.add_parser('download-image', help='Download a new image for the current environment.')
    download_image_parser.add_argument('-n', '--name', type=str, default=None, required=True,
        help='The name of the environment to activate the image of.')
    download_image_parser.add_argument('-i', '--image', type=str, default=None,
        choices=['singularity', 'docker', 'all'], required=True, help='The image to be downloaded.')
    download_image_parser.add_argument('-v', '--version', type=str, required=False, default=None, help='Specify the tag number for the version to get.')
    download_image_parser.add_argument('--set-active', action='store_true', help='Sets the image to active.')
    download_image_parser.set_defaults(function=download_image_func)

    # Add image manually
    add_custom_image_parser = env_subparsers.add_parser('add-image', help='Add an image to use to the environment. THIS WILL COPY TO THE DIRECTORY STRUCTURE OF THE ENVIRONMENT.')
    add_custom_image_parser.add_argument('image', type=str, help='Path to the image file.')
    add_custom_image_parser.add_argument('-e', '--env', default=get_active_env(), help='Environment to add the image to.')
    add_custom_image_parser.add_argument('-a', '--activate', action='store_true', default=False, help='Activate the image passed in.')
    add_custom_image_parser.set_defaults(function=add_custom_image)

    # Get active image
    list_images_parser = env_subparsers.add_parser('list-image', help='List all of the images available for this environment.')
    list_images_parser.add_argument('-e', '--env', type=str, default=get_active_env(), help='Environment to get the images for.')
    list_images_parser.set_defaults(function=list_images_parser_func)

     # List available flip files
    flip_file_parser = env_subparsers.add_parser('list-classifiers', help='List all of the classifiers available within the images.')
    flip_file_parser.set_defaults(function=list_classifiers_func)

    # Add custom binds to env file
    add_custom_binds_parser = env_subparsers.add_parser('add-bind-path', help='Use this to add common bind paths to your environment file so that you no longer need to type them.')
    add_custom_binds_parser.add_argument('paths', nargs='+', help='List of directories to add to the env file.', type=str)
    add_custom_binds_parser.set_defaults(function=add_custom_binds_func)

    # Add custom binds to env file
    del_custom_binds_parser = env_subparsers.add_parser('del-bind-path', help='Use this to delete common bind paths to your environment file.')
    del_custom_binds_parser.add_argument('paths', nargs='+', help='List of directories to add to the env file.', type=str)
    del_custom_binds_parser.set_defaults(function=del_custom_binds_func)

    list_custom_binds_parser = env_subparsers.add_parser('list-binds', help='Use this to list all of the custom bind paths added to your environment file.')
    list_custom_binds_parser.add_argument('-e', '--env', type=str, default=get_active_env(), help='List of bind paths added to environment file.')
    list_custom_binds_parser.set_defaults(function=list_custom_binds)

    args = parser.parse_args()
    try:
        args.function(args)
    except:
        pass
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
            cons = {"GITHUB_PAT": None, "IMAGE_PATHS": None, "ACTIVE_IMAGE": None, "CUSTOM_BIND_PATHS": []}
            yaml.dump(cons, f)
        sys.stderr.write('Environment config created at {}.\n'.format(f_path))

        if args.download_image:
            download_args = Namespace(name=args.name, image=args.download_image,
                set_active=args.set_active_image, version=None)
            try:
                download_image_func(download_args)
            except:
                shutil.rmtree(get_environment_path(), args.name)
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

def curr_env_func(args):
    print('Currently active image is: {}'.format(get_active_env()))
#end curr_env_func()

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

def list_classifiers_func(args):
    flips = get_all_classifiers()

    sys.stderr.write('Available flip files are: \n')
    for f in flips:
        sys.stderr.write('{}\n'.format(f))
#end list_classifiers_func()

def add_custom_image(args):
    image = os.path.abspath(args.image)
    env = args.env
    env_path = os.path.join(get_environment_path(), env)

    # If we are passing in a singularity image
    if str.endswith(image, 'sif'):
        root_dir = os.path.splitext(os.path.split(image)[-1])[0]
        final_dir = os.path.join(env_path, root_dir)
        try:
            os.mkdir(final_dir)
        except:
            sys.stderr.write('Error: Image already exists in the environment. Operation aborted.\n')
            return
        sys.stderr.write('Copying {} to {}.\n'.format(image, env_path))
        shutil.copy(image, final_dir)
        add_custom_image_in_environment(env, final_dir + '.sif', 'singularity')
        if args.activate:
            set_custom_active_image(env, final_dir + '.sif')

    else:
        add_custom_image_in_environment(env, env_path, 'docker')
#end add_custom_image()

def activate_image_func(args):
    assert (args.name is not None)
    assert (args.image is not None)

    set_active_image(args.name, args.image)
#end activate_image_func()

def download_image_func(args):
    assert (args.name is not None)
    assert (args.image is not None)

    if args.image == 'all' and args.set_active is True:
        sys.stderr.write('WARNING: Cannot activate more than one image at once, so none will be activated.\n')

    if args.image == 'all':
        images = ['docker', 'singularity']

    else:
        images = [args.image]

    image_paths = download_images(images, args.name, args.version)
    assert (len(image_paths) == len(images))

    for image in images:
        insert_image_in_environment(args.name, image)

    if args.image == 'all' and args.set_active is True:
        return

    if args.set_active is True:
        set_active_image(args.name, args.image)
#end download_image_func()

def list_images_parser_func(args):
    active_image = get_active_image()

    env_path = os.path.join(get_environment_path(), args.env, args.env + '.yml')

    with open(env_path, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)

    image_paths = contents["IMAGE_PATHS"]

    for k in image_paths:
        sys.stderr.write('{}: \n'.format(k))
        for p in image_paths[k]:
            if p == active_image:
                sys.stderr.write('[ACTIVE] - {}\n'.format(p))
            else:
                sys.stderr.write('\t - {}\n'.format(p))
#end list_images_parser_func()

def add_custom_binds_func(args):
    paths = []
    for p in args.paths:
        p = os.path.abspath(p)
        paths.append(p)

    add_custom_bind_paths(paths)
#end custom_binds_func()

def del_custom_binds_func(args):
    paths = []
    for p in args.paths:
        p = os.path.abspath(p)
        paths.append(p)

    remove_custom_bind_paths(paths)
#end del_binds_func()

def list_custom_binds(args):
    env_path = os.path.join(get_environment_path(), args.env, args.env + '.yml')

    with open(env_path, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)

    bind_paths = contents['CUSTOM_BIND_PATHS']

    if len(bind_paths) == 0:
        sys.stderr.write('There are no bind paths set on this environment.\n')
        return

    sys.stderr.write('Custom bind paths are for {} are: \n'.format(args.env))
    for p in bind_paths:
        sys.stderr.write('\t- {}\n'.format(p))
#end list_custom_binds()

if __name__ == '__main__':
    main()