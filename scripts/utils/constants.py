DEFAULT_FLIP_PATH = '/moseq2_data/flip_files/flip_classifier_k2_c57_10to13weeks.pkl'
BATCH_TABLE = {'extract-batch': ['--input-dir', '-i', '--config-file', '-c', '--filename']}
EXTRACT_TABLE = {'generate-config': ['-o', '--output-file'],
                'extract': ['--config-file', '--flip-classifier']}
SINGULARITY_COMS = {'exec': 'singularity exec', 'mount': '-B'}