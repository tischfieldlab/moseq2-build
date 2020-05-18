from pathlib import Path
import os, ruamel.yaml as yaml

DEFAULT_FLIP_PATH = '/moseq2_data/flip_files/flip_classifier_k2_c57_10to13weeks.pkl'
BATCH_TABLE = {'extract-batch': ['--input-dir', '-i', '--config-file', '-c', '--filename']}
EXTRACT_TABLE = {'generate-config': ['-o', '--output-file'],
                'extract': ['--config-file', '--flip-classifier']}
SINGULARITY_COMS = {'exec': 'singularity exec', 'mount': '-B'}
ENVIRONMENT_CONFIG = os.path.join(str(Path.home()), ".config", "moseq2_environment", "moseq2_environment.yaml")
GITHUB_LINK = "@api.github.com/repos/tischfieldlab/moseq2-build/releases"

def getDefaultImage():
    with open(ENVIRONMENT_CONFIG, "r") as f:
        contents = yaml.safe_load(f)
    defaultImage = contents['defaultImage']
    return defaultImage
#end getDefaultImage()