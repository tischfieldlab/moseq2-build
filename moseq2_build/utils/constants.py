from pathlib import Path
import os, ruamel.yaml as yaml

DEFAULT_FLIP_PATH = '/moseq2_data/flip_files/flip_classifier_k2_c57_10to13weeks.pkl'
BATCH_TABLE = {'extract-batch': ['--input-dir', '-i', '--config-file', '-c', '--filename']}
EXTRACT_TABLE = {'generate-config': ['-o', '--output-file'],
                'extract': ['--config-file', '--flip-classifier']}
SINGULARITY_COMS = {'exec': 'singularity exec', 'mount': '-B'}
ENVIRONMENT_CONFIG = os.path.join(str(Path.home()), ".config", "moseq2_environment", "moseq2_environment.yaml")

# Get the default image path from the config file and use it here
with open(ENVIRONMENT_CONFIG, 'r') as f:
    contents = yaml.safe_load(f)
if contents is not None:
    DEFAULT_IMAGE = contents["defaultImage"]
else:
    DEFAULT_IMAGE = None