import argparse

from moseq2_build.utils.image import *
from moseq2_build.utils.constants import *

def main():
    parser = argparse.ArgumentParser(description='Contains all of the image options for the moseq2 environment.')
    image_subparsers = parser.add_subparsers()

    # Activate image
    activate_image_parser = image_subparsers.add_parser('activate')
    activate_image_parser.add_argument('-n', '--name', type=str, default=None, required=True,
        help='The name of the environment to activate the image of.')
    activate_image_parser.add_argument('-i', '--image', type=str, default=None,
        choices=['singularity', 'docker'], required=True, help='The image to be set to active.')
    activate_image_parser.set_defaults(function=activate_image_func)

    # Download image
    download_image_parser = image_subparsers.add_parser('download')
    download_image_parser.add_argument('-n', '--name', type=str, default=None, required=True,
        help='The name of the environment to activate the image of.')
    download_image_parser.add_argument('-i', '--image', type=str, default=None,
        choices=['singularity', 'docker', 'all'], required=True, help='The image to be downloaded.')
    download_image_parser.add_argument('--set-active', action='store_true', help='Sets the image to active.')
    download_image_parser.set_defaults(function=download_image_func)

    # Update image
    update_image_parser = image_subparsers.add_parser('update')
    update_image_parser.add_argument('-n', '--name', type=str, default=None, required=True,
        help='The name of the environment to activate the image of.')
    update_image_parser.add_argument('-i', '--image', type=str, default=None,
        choices=['singularity', 'docker'], required=True, help='The image to be set as active.')
    update_image_parser.set_defaults(function=update_active_image_func)

    # Get active image
    list_images_parser = image_subparsers.add_parser('list')
    list_images_parser.set_defaults(function=list_images_parser_func)

    args = parser.parse_args()
    args.function(args)
#end main()

def activate_image_func(args):
    assert (args.name is not None)
    assert (args.image is not None)

    insert_image_in_environment(args.name, args.image)
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

    image_paths = download_images(images, args.name)
    assert (len(image_paths) == len(images))

    for image in images:
        insert_image_in_environment(args.name, image)

    if args.image == 'all' and args.set_active is True:
        return

    if args.set_active is True:
        set_active_image(args.name, args.image)
#end download_image_func()

def list_images_parser_func(args):
    sys.stderr.write('Active image: \n')
    sys.stderr.write(get_active_image() + '\n')
#end list_images_parser_func()

def update_active_image_func(args):
    assert (args.name is not None)
    assert (args.image is not None)

    set_active_image(args.name, args.image)
#end update_active_image_func()

if __name__ == "__main__":
    main()