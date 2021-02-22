import yaml
import click
import os

from pathlib import Path

from moseq2_build.utils.constants import get_environment_path
from moseq2_extract import cli as extract_cli
from moseq2_batch import cli as batch_cli
from moseq2_pca import cli as pca_cli
from moseq2_viz import cli as viz_cli

def create_table(command_list):
    res = {}
    for f in command_list:
        p_list = []
        for param in command_list[f].params:
            if type(param.type) == type(click.Path()) or type(param.type) == type(click.File()) or 'dir' in param.name or param.name == 'flip_classifier':
                for opt in param.opts:
                    if param.param_type_name == 'option':
                        p_list.append(opt)
        if len(p_list) > 0:
            res[f] = p_list

    return res
#end create_table()

def create_config_table():
    p_list = []
    for param in extract_cli.cli.commands['extract'].params:
        if type(param.type) == type(click.Path()) or type(param.type) == type(click.File()) or 'dir' in param.name or param.name == 'flip_classifier':
            for opt in param.opts:
                if param.param_type_name == 'option':
                    p_list.append(param.name)

    return p_list
#end create_config_table()

def create_master_tables(path):
    command_tables = []
    command_tables.append(create_table(extract_cli.cli.commands))
    command_tables.append(create_table(batch_cli.cli.commands))
    command_tables.append(create_table(pca_cli.cli.commands))
    command_tables.append(create_table(viz_cli.cli.commands))
    command_tables.append({'config': create_config_table()})

    master_table = {}
    for table in command_tables:
        master_table.update(table)

    with open(path, 'w') as f:
        yaml.dump(master_table, f)

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--output-file', type=str, help='Path to file to create.', default=os.path.join(Path.home(), 'argtable.yaml'))
    args = parser.parse_args()

    create_master_tables(args.output_file)
#end main()

if __name__ == '__main__':
    main()