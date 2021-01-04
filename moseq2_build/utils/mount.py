import os
import sys
import yaml

def mount_dirs(remainder, mount_string, com_table):
    pathKeys = []
    mount_com = ''
    if (len(remainder) == 0):
        return ''

    for param in com_table:
        if param in remainder:
            idx = remainder.index(param) + 1
            if idx >= len(remainder):
                sys.stderr.write('Please make sure each parameter has a valid value.\n')
                exit(1)

            pathKeys.append(os.path.abspath(remainder[idx]))

            if len(pathKeys) != 0:
                longest_path = os.path.dirname(os.path.commonpath(pathKeys))

                if longest_path == '\\' or longest_path == ' / ':
                    sys.stderr.write('Common path is the root, so it will not be mounted.\n')
                else:
                    mount_com = mount_string + ' ' + longest_path

    return mount_com
#end mount_dirs()