# This file contains all the operations that are done to the manifest file
# The table is formatted as follows:
#            Name | Active
#            -------------
#            test | False
#            test1| True
#              .  |   .
#              .  |   .
#              .  |   .

import csv
import os
import sys

from moseq2_build.utils.constants import get_environment_manifest, get_environment_path

def create_manifest_file():
    man_path = get_environment_manifest()

    if os.path.isfile(man_path) is True:
        sys.stderr.write('Manifest file already exists, so one will not be created.\n')
        exit(0)

    # If the directory does not exist, then create it
    env_path = get_environment_path()
    if os.path.isdir(env_path) is False:
        os.mkdir(env_path)

    # Create the manifest file
    open(man_path, 'w').close()

    sys.stderr.write('Manifest file has been created at {}\n'.format(man_path))
#end create_manifest_file()

def delete_manifest_file():
    man_path = get_environment_manifest()

    if os.path.isfile(man_path) is False:
        sys.stderr.write('No manifest file exists so nothing will be deleted.\n')
        exit(0)

    # Delete the manifest file
    os.remove(man_path)

    sys.stderr.write('Manifest file {} has been deleted.\n'.format(man_path))
#end delete_manifest_file()

def is_manifest_created():
    return os.path.isfile(get_environment_manifest())
#end is_manifest_created()

def is_in_manifest(key):
    if is_manifest_created() is False:
        sys.stderr.write('No manifest file exists, please create one first.\n')
        return False

    man_path = get_environment_manifest()
    with open(man_path, 'r') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')

        for row in reader:
            if key == row[0]:
                return True

    return False
#end is_in_manifest()

def delete_from_manifest(key):
    if is_manifest_created() is False:
        sys.stderr.write('No manifest file exists, please create one first.\n')
        return False

    man_path = get_environment_manifest()
    contents = []
    with open(man_path, 'r') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')

        for row in reader:
            contents.append(row)

    # Delete the row with that key from the table
    new_contents = []
    target = []
    for row in contents:
        if len(row) == 0:
            continue
        if key != row[0]:
            new_contents.append(row)
        else:
            target = row

    if len(target) == 0:
        sys.stderr.write('\"{}\" does not exist in the manifest, so nothing was deleted.\n'.format(key))
        return False

    # Write out the new tsv file
    with open(man_path, 'w') as tsv_file:
        new_contents = [x for x in new_contents if x != []]
        writer = csv.writer(tsv_file, delimiter='\t')

        writer.writerows(new_contents)
        sys.stderr.write('"{}" was removed from the manifest file.\n'.format(target))

    return True
#end delete_from_manifest()

def put_in_manifest(key, active=False):
    if is_manifest_created() is False:
        sys.stderr.write('No manifest file exists, please create one first.\n')
        return False

    man_path = get_environment_manifest()
    if is_in_manifest(key) is False:
        entry = [key, active]
        with open(man_path, 'a') as tsv_file:
            if entry != []:
                writer = csv.writer(tsv_file, delimiter='\t')
                writer.writerow(entry)

            sys.stderr.write('{} has successfully been added to the manifest.\n'.format(entry))

        # Set the entry to active and remove active from all other entries
        if active is True:
            set_active_row(key, True)
            sys.stderr.write('Set {} as the active image.\n'.format(key))
        return True
    else:
        sys.stderr.write('"{}" is already in the manifest.\n'.format(key))

    return False
#end put_in_manifest()

def set_active_row(key, val):
    if is_manifest_created() is False:
        sys.stderr.write('No manifest file exists, please create one first.\n')
        return False

    man_path = get_environment_manifest()
    contents = []
    with open(man_path, 'r') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')

        for row in reader:
            contents.append(row)

    # Update the row if the key exists
    target = []
    for row in contents:
        if len(row) == 0:
            continue
        if key == row[0]:
            row[1] = val
            target = row
        else:
            row[1] = False

    if len(target) == 0:
        sys.stderr.write('"{}" does not exist in the manfiest. Nothing was updated.\n'.format(key))
        return False

    # Write out the file
    with open(man_path, 'w') as tsv_file:
        contents = [x for x in contents if x != []]
        writer = csv.writer(tsv_file, delimiter='\t')
        writer.writerows(contents)
        sys.stderr.write('"{}" has been updated in the manifest file.\n'.format(target))

    return True
#end set_active_row()

def is_active_row(key):
    if is_manifest_created() is False:
        sys.stderr.write('No manifest file exists, please create one first.\n')
        return False

    man_path = get_environment_manifest()
    with open(man_path, 'r') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')

        for row in reader:
            if key == row[0]:
                return row[1]

    return False
#end is_active_row()

def contains_active_row():
    if is_manifest_created() is False:
        sys.stderr.write('No manifest file exists, please create one first.\n')
        return False

    man_path = get_environment_manifest()
    with open(man_path, 'r') as tsv_file:
        reader = csv.reader(tsv_file, delimiter='\t')

        for row in reader:
            if row[1] == 'True':
                return True

    return False
#end contains_active_row()