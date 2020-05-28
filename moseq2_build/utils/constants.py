from pathlib import Path
import os, ruamel.yaml as yaml

FIBER_FLIP_PATH = '/moseq2_data/flip_files/flip_classifier_k2_largemicewithfiber.pkl'
INSCOPIX_FLIP_PATH = '/moseq2_data/flip_files/flip_classifier_k2_inscopix.pkl'
C57_FLIP_PATH = '/moseq2_data/flip_files/flip_classifier_k2_c57_10to13weeks.pkl'
DEFAULT_FLIP_PATH = C57_FLIP_PATH

BATCH_TABLE = {'batch': ['--input-dir', '-i', '--config-file', '-c', '--filename']}
EXTRACT_TABLE = {'generate-config': ['-o', '--output-file'],
                'extract': ['--config-file', '--flip-classifier']}
SINGULARITY_COMS = {'exec': 'singularity exec', 'mount': '-B'}
ENVIRONMENT_CONFIG = os.path.join(str(Path.home()), ".config", "moseq2_environment", "moseq2_environment.yaml")
GITHUB_LINK = "@api.github.com/repos/tischfieldlab/moseq2-build/releases"

def getDefaultImage():
    if os.path.isfile(ENVIRONMENT_CONFIG):
        with open(ENVIRONMENT_CONFIG, "r") as f:
            contents = yaml.safe_load(f)
        defaultImage = contents['defaultImage']
    else:
        defaultImage = None
    return defaultImage
#end getDefaultImage()
