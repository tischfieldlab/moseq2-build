import yaml
import click
import os

from pathlib import Path

from moseq2_extract import cli as extract_cli
from moseq2_batch import cli as batch_cli
from moseq2_pca import cli as pca_cli
from moseq2_viz import cli as viz_cli
from moseq2_model import cli as model_cli

def create_table(command_list):
    """Creates the argtable file that is used to determine which arguments 
    to which moseq2 scripts have values that need to be mounted.

    Args:
        command_list (Dictionary <string, string>): List of commands as defined in the `constants.py` file.

    Returns:
        Dictionary <string, string>: A dictionary of each entry point name and the list of commands that are candidates for mounting.
    """
    res = {}
    for f in command_list:
        p_list = []
        for param in command_list[f].params:
            # If the passed in parameter is a path or a file as defined by click, we store it in the resulting table we return.
            if type(param.type) == type(click.Path()) or type(param.type) == type(click.File()) or 'dir' in param.name or param.name == 'flip_classifier':
                for opt in param.opts:
                    if param.param_type_name == 'option':
                        p_list.append(opt)
        if len(p_list) > 0:
            res[f] = p_list

    return res
#end create_table()

def create_config_table():
    """Creates the table of important arguments from the moseq2-extract generate-config entry point.

    We need to differentaite here because some of the important arguments for this function are not defined to be
    "path" or "file" by click. We need to hardcode some of them here.

    Returns:
        Dictionary <string, string>: A dictionary of the config command arguments that we care about.
    """
    p_list = []
    for param in extract_cli.cli.commands['extract'].params:
        if type(param.type) == type(click.Path()) or type(param.type) == type(click.File()) or 'dir' in param.name or param.name == 'flip_classifier':
            for opt in param.opts:
                if param.param_type_name == 'option':
                    p_list.append(param.name)

    return p_list
#end create_config_table()

def create_master_tables(path):
    """Wrapper function that creates the master argtable for all of the moseq2 pipeline scripts.

    Args:
        path (string): Path to the resulting argtable yaml file that will be generated.
    """
    command_tables = []
    command_tables.append(create_table(extract_cli.cli.commands))
    command_tables.append(create_table(batch_cli.cli.commands))
    command_tables.append(create_table(pca_cli.cli.commands))
    command_tables.append(create_table(viz_cli.cli.commands))
    command_tables.append(create_table(model_cli.cli.commands))
    command_tables.append({'config': create_config_table()})

    master_table = {}
    # Put all the tables in the master table
    for table in command_tables:
        master_table.update(table)

    # Write the master table to disk. NOTE: Formatted in a yaml file.
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