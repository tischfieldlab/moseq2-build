import os

from pathlib import Path

GITHUB_LINK = "@api.github.com/repos/tischfieldlab/moseq2-build/releases"

def get_environment_path():
    return os.path.join(str(Path.home()), ".config", "moseq2_environment")

def get_environment_manifest():
    return os.path.join(str(Path.home()), ".config", "moseq2_environment", "environments.tsv")