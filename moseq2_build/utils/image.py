import sys
import os
import tarfile

from moseq2_build.utils.constants import get_environment_manifest, get_environment_path

def unpack_image(env_path, image_paths):
    assert (len(image_paths) != 0)

    for p in image_paths:
        if not p.endswith('.tar.gz'):
            continue
        target_dir = os.path.join(env_path, p.split('/')[-1].replace('.tar.gz', ''))
        tar = tarfile.open(p)
        tar.extractall(target_dir)
        tar.close()
