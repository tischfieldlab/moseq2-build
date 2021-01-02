import os

from pathlib import Path

GITHUB_LINK = "@api.github.com/repos/tischfieldlab/moseq2-build/releases"

def get_environment_path():
    return os.path.join(str(Path.home()), ".config", "moseq2_environment")

def get_environment_manifest():
    return os.path.join(str(Path.home()), ".config", "moseq2_environment", "environments.tsv")

def get_image_paths(image):
    contents = os.listdir(get_environment_path())
    envs = []
    for f in contents:
        if os.path.isdir(f):
            continue

        if f.endswith('.tar.gz') and image in f:
            envs.append(os.path.join(get_environment_path(), f))

    if len(envs) == 0:
        return None

    return envs[0]