import sys
import os
import tarfile
import tqdm
import requests
import yaml
import getpass

from moseq2_build.utils.constants import *

def add_images_to_environment(image_paths, env):
    env_path = os.path.join(get_environment_path(), env, env + '.yml')

    paths = []
    for image in image_paths:
        paths.append(image)

    with open(env_path, 'w+') as f:
        yaml.dump({'images': paths})
#end add_images_to_environment()

def download_images(images, env):
    assert (len(images) != 0)

    p = os.path.join(get_environment_path(), env, env + '.yml')
    with open(p, 'r') as f:
        data = yaml.load(f, Loader=yaml.SafeLoader)

        if data == None or data['GITHUB_PAT'] == None:
            pat = getpass.getpass("Enter GitHub Personal Access Token (PAT): ")
            data['GITHUB_PAT'] = pat
            with open(p, 'w+') as fi:
                yaml.dump(data, fi)
        else: 
            pat = data['GITHUB_PAT']

    url = "https://" + pat + ':' + GITHUB_LINK
    x = requests.get(url + '/latest')

    if x.status_code != 200:
        sys.stderr.write('Failed to get release info.\n')
        exit(1)

    jsonData = x.json()
    assets = jsonData['assets']
    result = []
    for image in images:
        for asset in assets:
            if image not in asset['name']:
                continue
            releaseID = str(asset['id'])
            assetName = asset['name']
            header = {'Accept': 'application/octet-stream'}
            finalURL = url + '/assets/' + releaseID

            x = requests.get(finalURL, headers=header, stream=True)
            if x.status_code != 200:
                sys.stderr.write('Error downloading the asset.\n')
                exit(1)

            totalSize = int(x.headers.get('content-length', 0))
            blockSize = 1024  # 1KB
            t = tqdm.tqdm(total=totalSize, unit='1B', unit_scale=True, desc='Downloading {}'.format(assetName))

            assetOutput = os.path.join(os.path.join(get_environment_path(), env, assetName))

            with open(assetOutput, 'wb') as f:
                for data in x.iter_content(blockSize):
                    t.update(len(data))
                    f.write(data)

            t.close()

            with tarfile.open(name=assetOutput) as tar:
                pa = os.path.splitext(assetOutput)[0]
                pa = os.path.splitext(pa)[0]
                for member in tqdm.tqdm(iterable=tar.getmembers(), total=len(tar.getmembers()), desc='Unzipping {}'.format(assetName)):
                    tar.extract(member=member, path=pa)

            os.remove(assetOutput)

            result.append(pa)

    return result
#end download_images()

def insert_image_in_environment(env, image):
    if is_image_in_environment(env, image):
        return

    env_path = os.path.join(get_environment_path(), env, env + '.yml')
    image_path = get_image_paths(env, image)

    # Now we need to add this to the environment file
    with open(env_path, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)

    if contents['IMAGE_PATHS'] is None:
        contents['IMAGE_PATHS'] = {image: image_path}
    else:
        contents['IMAGE_PATHS'][image] = image_path

    with open(env_path, 'w+') as f:
        yaml.dump(contents, f)
#end insert_image_in_environment()

def set_active_image(env, image):
    if not is_image_in_environment(env, image):
        sys.stderr.write('{} does not exist in the environment. Please download it first.\n'.format(image))
        exit(1)

    env_path = os.path.join(get_environment_path(), env, env + '.yml')
    with open(env_path, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)

    image_path = contents["IMAGE_PATHS"][image]
    sys.stderr.write('Setting {} as the active image.\n'.format(image_path))

    contents['ACTIVE_IMAGE'] = image_path
    with open(env_path, 'w+') as f:
        yaml.dump(contents, f)
#end set_active_image()

def is_image_in_environment(env, image):
    env_path = os.path.join(get_environment_path(), env, env + '.yml')

    with open(env_path, 'r') as f:
        contents = yaml.load(f, Loader=yaml.SafeLoader)

    if contents['IMAGE_PATHS'] == None:
        return False

    if image in contents['IMAGE_PATHS'].keys():
        return True

    return False
#end is_image_in_environment()