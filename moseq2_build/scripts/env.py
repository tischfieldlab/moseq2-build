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
    add_custom_image_parser.add_argument('-e', '--env', required=True, default=None, help='Environment to add the image to.')
    add_custom_image_parser.add_argument('-a', '--activate', action='store_true', default=False, help='Activate the image passed in.')
    add_custom_image_parser.set_defaults(function=add_custom_image)

    delete_custom_image_parser = env_subparsers.add_parser('del-image', help='Delete an image from the environment file.')
    delete_custom_image_parser.add_argument('-i', '--image', type=str, default=None,
        choices=['singularity', 'docker'], required=True, help='The image to delete from.')
    delete_custom_image_parser.add_argument('-e', '--env', type=str, default=None, required=True,
        help='The name of the environment to delete the image from.')
    delete_custom_image_parser.set_defaults(function=delete_custom_image)

    # Get active image
    list_images_parser = env_subparsers.add_parser('list-image', help='List all of the images available for this environment.')
    list_images_parser.add_argument('-e', '--env', type=str, required=True, default=None, help='Environment to get the images for.')
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
    list_custom_binds_parser.add_argument('-e', '--env', type=str, default=None, required=True, help='List of bind paths added to environment file.')
    list_custom_binds_parser.set_defaults(function=list_custom_binds)

    args = parser.parse_args()
    try:
        args.function(args)
    except:
        pass
#end main()

def create_env_func(args):
    """Creates an environment and a manifest if one isn't already created.

    Args:
        args (ArgParse Arguments): A list of arguments from argparse.
    """
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
            # Here we default certain keys in the environment to None until they are overwritten by the user.
            cons = {"GITHUB_PAT": None, "IMAGE_PATHS": None, "ACTIVE_IMAGE": None, "CUSTOM_BIND_PATHS": []}
            yaml.dump(cons, f)
        sys.stderr.write('Environment config created at {}.\n'.format(f_path))

        # If the flag to download an image from releases is passed, we do that here.
        if args.download_image:
            download_args = Namespace(name=args.name, image=args.download_image,
                set_active=args.set_active_image, version=None)
            try:
                download_image_func(download_args)
            except:
                shutil.rmtree(get_environment_path(), args.name)
#end create_env_func()

def delete_env_func(args):
    """Deletes an environment from disk and the manifest.

    Args:
        args (ArgParse Arguments): A list of arguments from argparse.
    """
    assert (args.name is not None)

    # Make sure the manifest is created
    if is_manifest_created() is False:
        sys.stderr.write('Manifest file is not created, please make sure one is created before deleting.\n')
        exit(1)

    # Delete the entry from the manifest, returns True if it was successfully deleted.
    res = delete_from_manifest(args.name)

    # If we deleted successfully, remove the file from disk
    if res is True:
        shutil.rmtree(os.path.join(get_environment_path(), args.name))
        sys.stderr.write('The "{}" environment has successfully been removed.\n'.format(args.name))
#end delete_env_func()

def curr_env_func(args):
    """Prints the currently active function, if one is set.
    """
    print('Currently active image is: {}'.format(get_active_env()))
#end curr_env_func()

def list_env_func(args):
    """Lists all environments created on disk.

    Args:
        args (ArgParse Arguments): List of arguments from argparse.
    """
    assert (args.active_only is not None)

    # Ensure that the manifest exists, otherwise we crash and burn here.
    if is_manifest_created() is False:
        sys.stderr.write('No manifest is created, please create one first.\n')
        exit(1)

    man_path = get_environment_manifest()
    
    # Set up the output table headers here... TODO: maybe these shouldn't be hardcoded?
    contents = [['Name', 'Active']]
    with open(man_path, 'r') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')

        for row in reader:
            # If the row is active, we want to make sure that True is set on the active flag.
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
    """Activates the passed in environment.

    Args:
        args (ArgParse Arguments): List of arguments from argparse.
    """
    assert (args.name is not None)
    set_active_row(args.name, True)
#end activate_env_func()

def deactivate_env_func(args):
    """Deactivates the passed in environment.

    Args:
        args (ArgParse Arguments): List of arguments from argparse.
    """
    assert (args.name is not None)
    set_active_row(args.name, False)
#end deactivate_env_func()

def list_classifiers_func(args):
    """Lists the installed classifiers inside the containerized image.

    Args:
        args (ArgParse Arguments): List of arguments from argparse.
    """
    flips = get_all_classifiers()

    sys.stderr.write('Available flip files are: \n')
    for f in flips:
        sys.stderr.write('{}\n'.format(f))
#end list_classifiers_func()

def add_custom_image(args):
    """Add a custom image to an environment. NOTE: This will copy the image to the environment folder structure.

    Args:
        args (ArgParse Arguments): List of arguments from argparse.
    """
    image = os.path.abspath(args.image)
    env = args.env
    env_path = os.path.join(get_environment_path(), env)

    # If we are passing in a singularity image
    if str.endswith(image, 'sif'):
        # Grab the root directory of the passed in image
        root_dir = os.path.splitext(os.path.split(image)[-1])[0]

        # Format the destination directory to remove the sif extension
        final_dir = os.path.join(env_path, root_dir, root_dir + '.sif')
        try:
            os.mkdir(os.path.join(env_path, root_dir))
        except:
            sys.stderr.write('Error: Image already exists in the environment. Operation aborted.\n')
            return

        sys.stderr.write('Copying {} to {}.\n'.format(image, env_path))
        shutil.copy(image, final_dir)

        # Add the image to the environment
        add_custom_image_in_environment(env, final_dir, 'singularity')

        # If we are told to activate the image by the user, activate it in the manifest.
        if args.activate:
            set_custom_active_image(env, final_dir)

    # This is the case where the image is a docker image
    else:
        add_custom_image_in_environment(env, env_path, 'docker')
#end add_custom_image()

def delete_custom_image(args):
    """Deletes a custom image from the environment.

    Args:
        args (ArgParse Arguments): List of arguments from argparse.
    """
    assert (args.env)
    env_path = os.path.join(get_environment_path(), args.env, args.env + '.yml')

    with open(env_path, 'r') as f:
        contents = yaml.load(f, yaml.FullLoader)

    # Because custom images may be a pain to deal with, we list all of the images in the 
    # environment directory structure and ask the user which to delete on the command line.
    image_path = contents['IMAGE_PATHS'][args.image]
    sys.stderr.write('Choose to delete one of the following images: \n')
    count = 0
    for p in image_path:
        sys.stderr.write('{}: {}\n'.format(count, p))
        count += 1
    selection = input('Enter selection [{}-{}]: '.format(0, len(image_path) - 1))
    image_path = image_path[int(selection)]

    containing_dir = os.path.dirname(image_path)

    try:
        shutil.rmtree(containing_dir)
    except:
        sys.stderr.write('Could not delete {}\n'.format(containing_dir))
        exit(-1)
    sys.stderr.write('Deleted {}.\n'.format(image_path))

    # If we deleted the active image, we need to let the user know that there is no current active image.
    if contents['ACTIVE_IMAGE'] == image_path:
        sys.stderr.write('\nWARNING: YOU HAVE DELETED THE ACTIVE IMAGE. PLEASE SET A NEW ONE BEFORE DOING ANY OTHER OPERATIONS.\n')
        contents['ACTIVE_IMAGE'] = None

    with open(env_path, 'w+') as f:
        yaml.dump(contents, f)
#end delete_custom_image()

def activate_image_func(args):
    """Sets the passed in image to be the active image. There can only be one at a time.

    Args:
        args (ArgParse Arguments): List of arguments from argparse.
    """
    assert (args.name is not None)
    assert (args.image is not None)

    set_active_image(args.name, args.image)
#end activate_image_func()

def download_image_func(args):
    """Downloads an image based on the passed in container information and GitHub tag.

    Args:
        args (ArgParse Arguments): List of arguments from argparse.
    """
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
    """Lists all the images installed in an environment.

    Args:
        args (ArgParse Arguments): List of arguments from argparse.
    """
    active_image = get_active_image()

    env_path = os.path.join(get_environment_path(), args.env, args.env + '.yml')

    with open(env_path, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)

    image_paths = contents["IMAGE_PATHS"]

    # Here is where we loop through the image paths and print them out, formatting them and denoting which is active.
    for k in image_paths:
        sys.stderr.write('{}: \n'.format(k))
        for p in image_paths[k]:
            # Show the image is active here
            if p == active_image:
                sys.stderr.write('[ACTIVE] - {}\n'.format(p))
            else:
                sys.stderr.write('\t - {}\n'.format(p))
#end list_images_parser_func()

def add_custom_binds_func(args):
    """Adds custom bind paths to the environment that are shadow bound on all calls into an image.

    Args:
        args (ArgParse Arguments): List of arguments from argparse.
    """
    paths = []
    for p in args.paths:
        p = os.path.abspath(p)
        paths.append(p)

    add_custom_bind_paths(paths)
#end custom_binds_func()

def del_custom_binds_func(args):
    """Delete custom binds from the environment.

    Args:
        args (ArgParse Arguments): List of arguments from argparse.
    """
    paths = []
    for p in args.paths:
        p = os.path.abspath(p)
        paths.append(p)

    remove_custom_bind_paths(paths)
#end del_binds_func()

def list_custom_binds(args):
    """Lists all of the custom bind paths configured for an environment.

    Args:
        args (ArgParse Arguments): List of arguments from argparse.
    """
    env_path = os.path.join(get_environment_path(), args.env, args.env + '.yml')

    with open(env_path, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)

    # Pull the value for this key in the environment metadata yaml file.
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