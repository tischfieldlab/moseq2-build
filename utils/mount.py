import os

def mountDirectories(args, mountString, comTable):
    """ Correctly formats the command to mount directories
    in both singularity and docker. This is used before
    a command is executed using either docker or singularity
    and is resposnible for ensuring the files/directories passed
    in are mounted and accessible within the image.
    :type args: Python argparse arguments data structure.
    :param args: The list of arguments passed into the script.

    :type mountString: String
    :param mountString: String containing the correct prefix
    argument required for mounting by docker or singularity.

    :type comTable: Dictionary
    :param comTable: Dictionary containing the prefix arguments
    for various commands we expose from docker and singularity.

    :rtype: String containing the full mount command.
    """
    pathKeys = []
    mountCommand = ''
    if (len(args.remainder) == 0):
        return ''

    for param in comTable[args.remainder[0]]:
        if param in args.remainder:
            idx = args.remainder.index(param) + 1
            if idx >= len(args.remainder):
                print("Please make sure each paramater has a valid argument.")
                exit(1)

            pathKeys.append(os.path.abspath(args.remainder[idx]))

    # Get the longest pathname common for all paths passed in
    if (len(pathKeys) != 0):
        longestCommonPath = os.path.dirname(os.path.commonprefix(pathKeys))

        if (longestCommonPath == "\\" or longestCommonPath == "/"):
            print("Common path is the root directory, so it will not be mounted.")

        else:
            mountCommand = mountString + " " + longestCommonPath

    return mountCommand
#end mountDirectories()