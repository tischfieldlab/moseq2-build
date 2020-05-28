import click
import os
from termcolor import colored

from moseq2_build.utils.constants import getDefaultImage, DEFAULT_FLIP_PATH, SINGULARITY_COMS, EXTRACT_TABLE, BATCH_TABLE, ENVIRONMENT_CONFIG
from moseq2_build.auto.extract import doExtract
from moseq2_build.auto.batch import doBatch
from moseq2_build.env.env import updateEnvironment, updateDefaultImage, cleanEnvironmentFolder, determineTargetAssets
from moseq2_build.utils.commands import printSuccessMessage

orig_init = click.core.Option.__init__

def new_init(self, *args, **kwargs):
    orig_init(self, *args, **kwargs)
    self.show_default = True
#ned new_init()

click.core.Option.__init__ = new_init

@click.group()
def cli():
    pass

@cli.command(name='extract', context_settings=dict(ignore_unknown_options=True))
@click.option('--image', default=getDefaultImage(), type=click.Path(exists=True), help='Location of the image file to be used.')
@click.option('--flip-path', default=DEFAULT_FLIP_PATH, type=click.Path(), help='Location of the flip classifier file.')
@click.argument('remainder', nargs=-1, type=click.UNPROCESSED)
def extract(image, flip_path, remainder):
    fileCommands = None
    if (image is None):
        print(colored('No valid path was passed in.', 'red'))
        exit(1)

    if (image.endswith('.sif')):
        print(colored('\nDetected singularity image at {}\n'.format(os.path.abspath(image)),
            'white', attrs=['bold']))
        fileCommands = SINGULARITY_COMS

    else:
        print('Docker is not supported at the moment... sorry :)')
        exit(1)

    doExtract(image, flip_path, list(remainder), fileCommands)
#end test()

@cli.command(name='batch', context_settings=dict(ignore_unknown_options=True))
@click.option('--image', default=getDefaultImage(), type=click.Path(exists=True), help='Location of the image file to be used.')
@click.option('--flip-path', default=DEFAULT_FLIP_PATH, type=click.Path(), help='Location of the flip classifier file.')
@click.option('--batch-output', default=os.getcwd(), type=click.Path(exists=True), help='Location for which the batched command script will be output to.')
@click.argument('remainder', nargs=-1, type=click.UNPROCESSED)
def batch(image, flip_path, batch_output, remainder):
    fileCommands = None
    if (image is None):
        print(colored('No valid path was passed in.', 'red'))
        exit(1)

    if (image.endswith('.sif')):
        print(colored('\nDetected singularity image at {}\n'.format(os.path.abspath(image)),
            'white', attrs=['bold']))
        fileCommands = SINGULARITY_COMS

    else:
        print('Docker is not supported at the moment... sorry :)')
        exit(1)

    doBatch(image, flip_path, batch_output, list(remainder), fileCommands)
#end batch()

@cli.command(name='env')
@click.option('-c', '--clean', is_flag=True, type=bool, default=False, help='Deletes all data in the environment folder.')
@click.option('-u', '--update-image', type=click.Path(), default=None, help='Path to the image file that will become the new default image.')
@click.option('-d', '--download-image', is_flag=True, type=bool, default=False, help='Downloads new image to specified folder.')
@click.option('--no-default', is_flag=True, type=bool, default=True, help='Override the current default image.')
@click.option('-v', '--version', type=str, default=None, help='Specific version number to download. Format: v24')
def env(clean, update_image, download_image, no_default, version):
    if clean == True:
        print("DELETING ALL DATA IN THE ENVIRONMENT!")
        cleanEnvironmentFolder()

    if download_image == True:
        assetsIndices, imageType, paths = determineTargetAssets(version)
        if no_default == True:
            updateEnvironment(assetsIndices, imageType, paths)
        else:
            printSuccessMessage('Skipping envrionment file\n\n')

    if update_image is not None:
        updateDefaultImage(update_image)

    printSuccessMessage('Exiting now\n\n')
#end env()

if __name__ == '__main__':
    cli()
