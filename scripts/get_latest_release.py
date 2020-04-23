import getpass, subprocess, json, argparse
import threading, time, sys
from termcolor import colored

doneWorking = False

GITHUB_LINK = "@api.github.com/repos/tischfieldlab/moseq2-build/releases"

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("assetType", nargs="?", help="Specify either singularity or docker asset to download from the latest release.")

    username = input("Enter GitHub username: ")
    password = getpass.getpass(prompt="Enter password: ")

    args = parser.parse_args()
    assetsIndices = [0, 1]

    if (args.assetType == 'singularity'):
        assetsIndices = [1]

    elif (args.assetType == 'docker'):
        assetsIndices[0]

    if username == ' ':
        print("Please enter non-empty username.")
        exit(1)

    if password == ' ':
        print("Please enter non-empty password.")
        exit(1)

    downloadAssets(username, password, assetsIndices)

    print(colored('\n\nAll commands executed\t' + u'\u2705', 'green', attrs=['bold']))
#end main()

def downloadAssets(uname, pword, indices):
    url = "https://" + uname + ":" + pword + GITHUB_LINK
    getReleaseInfo = 'curl ' + url + "/latest"

    msg = "Received release info"

    print("\nGetting latest release info")

    result = executeCommand(getReleaseInfo)
    panicIfError(result, msg)

    info = result[0].decode('utf-8')
    info = info.replace('\n', '')
    info = info.replace(' ', '')
    jsonData = json.loads(info)

    for i in indices:
        asset = jsonData["assets"][i]
        releaseId = str(asset["id"])
        finalCom = "curl -O -J -L -H 'Accept: application/octet-stream' " + url + "/assets/" + releaseId
        msg = "Downloaded asset " + releaseId

        print("\n\nDownloading asset " + releaseId)

        result = executeCommand(finalCom)
        panicIfError(result, msg)
#end downloadAssets()

def executeCommand(com):
    global doneWorking
    doneWorking = False
    spinThread = threading.Thread(target=spinCursor)
    spinThread.start()

    proc = subprocess.Popen(com, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE,
            shell=True)
    contents = proc.communicate()

    doneWorking = True
    spinThread.join()

    return contents
#end executeCommand()

def panicIfError(output, msg):
    if len(output[0]) == 0:
        sys.stdout.write(colored('\n' + msg + '\t' + u'\u274c' + '\n', "red", attrs=['bold']))
        sys.stderr.write(output[1].decode('utf-8'))
        exit(1)

    else:
        sys.stdout.write(colored(msg + '\t' + u'\u2705', "green", attrs=['bold']))
#end panic()

def spinCursor():
    global doneWorking
    sys.stdout.flush()
    sys.stdout.write((colored("\nExecuting command", "red", attrs=['bold'])))
    while True:
        for cursor in '|/-\\':
            time.sleep(0.1)
            sys.stdout.write(colored('\rExecuting command' + cursor, "red", attrs=['bold']))
            sys.stdout.flush()
            if doneWorking:
                sys.stdout.write('\n')
                sys.stdout.write('\033[F')
                sys.stdout.write('\033[K')
                return
#end spinCursor()

if __name__ == '__main__':
    main()
