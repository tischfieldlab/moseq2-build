import sys, subprocess, threading, time
from termcolor import colored

doneWorking = True

def executeCommand(commandString):
    global doneWorking
    """ Executes the passed in command string and captures the output
    from stderr and stdout in a tuple and returns it. It also spawns a
    thread that is responsible for displaying a load cursor until the
    command has been fully executed.
    :type commandString: String
    :param commandString: Command(s) to be executed by subprocess

    :rtype: Tuple of stdin and stdout byte strings generated from
    executing passed in command string.
    """
    doneWorking = False
    spinThread = threading.Thread(target=spinCursor)
    spinThread.start()

    proc = subprocess.Popen(commandString, stderr=subprocess.PIPE,
        stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
    contents = proc.communicate()

    doneWorking = True
    spinThread.join()
    return contents, proc.returncode
#end executeCommand()

def spinCursor():
    """ Thread function that spins a cursor while work
    is being done. Uses a global variable to track whether
    or not this thread should be joined.
    """
    global doneWorking
    sys.stdout.flush()
    sys.stdout.write(colored("Executing commands ", "red", attrs=['bold']))
    while True:
        for cursor in '|/-\\':
            time.sleep(0.1)
            sys.stdout.write(colored("\rExecuting commands " + cursor + "\t\t", "red", attrs=['bold']))
            sys.stdout.flush()
            if doneWorking:
                sys.stdout.write('\n')
                sys.stdout.write('\033[F')
                sys.stdout.write('\033[K')
                return
#end spinCursor()

def panicIfStderr(retCode, output, msg):
    """ Checks the return code from subprocess.communicate()
    to see if there was an error. If there was an error, then
    we print to stderr and exit the program.

    :type retCode: Integer
    :param retCode: Return code from subprocess.communicate()

    :type output: Tuple
    :param output: Tuple containing stdout and stderr output from
    subprocess.communicate().

    :type msg: String
    :param msg: Message to print to the screen.
    """
    if retCode != 0:
        printErrorMessage(msg)
        sys.stderr.write(output[1].decode('utf-8'))
        exit(1)
    else:
        printSuccessMessage(msg)
#end panicIfStderr()

def printSuccessMessage(msg):
    sys.stdout.write(colored('\n' + u'\u2705' + " " + msg, "green", attrs=['bold']))
#end printSuccessMessage()

def printErrorMessage(msg):
   sys.stderr.write(colored('\n' + u'\u2705' + " " + msg, "red", attrs=['bold']))
#end printErrorMessage()