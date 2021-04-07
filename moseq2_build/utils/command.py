import sys

def check_stderr(error):
    """Exits if stderr is not empty.

    Args:
        error (byte string): Byte string output from subprocess.communicate().
    """
    if len(error) != 0:
        sys.stderr.write(error.decode('utf-8'))
        exit(1)
#end check_stderr()

def check_stdout(out):
    """Prints the stdout if it is not empty.

    Args:
        out (byte string): Byte string output from subprocess.communicate().
    """
    if len(out) != 0:
        sys.stdout.write(out.decode('utf-8'))
#end check_stdout()