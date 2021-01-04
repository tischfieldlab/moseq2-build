import sys

def check_stderr(error):
    if len(error) != 0:
        sys.stderr.write(error.decode('utf-8'))
        exit(1)
#end check_stderr()

def check_stdout(out):
    if len(out) != 0:
        sys.stdout.write(out.decode('utf-8'))
#end check_stdout()