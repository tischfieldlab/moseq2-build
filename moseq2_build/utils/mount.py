import os, ruamel.yaml as yaml

def mountDirectories(remainder, mountString, comTable):
    pathKeys=[]
    mountCommand = ''
    if (len(remainder) == 0):
        return ''

    for param in comTable:
        if param in remainder:
            idx = remainder.index(param) + 1
            if idx >= len(remainder):
                print('Please make sure each parameter has a valid value.')
                exit(1)

            pathKeys.append(os.path.abspath(remainder[idx]))

            if len(pathKeys) != 0:
                longestCommonPath = os.path.dirname(os.path.commonprefix(pathKeys))

                if longestCommonPath == '\\' or longestCommonPath == '/':
                    print('Common path is root, so it will not be mounted.')
                else:
                    mountCommand = mountString + ' ' + longestCommonPath
    return mountCommand
#end mountDirectories()

