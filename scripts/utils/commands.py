import sys, subprocess, threading
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
    return contents
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
            sys.stdout.write(colored("\rExecuting commands " + cursor, "red", attrs=['bold']))
            sys.stdout.flush()
            if doneWorking:
                sys.stdout.write('\n')
                sys.stdout.write('\033[F')
                sys.stdout.write('\033[K')
                return
#end spinCursor()