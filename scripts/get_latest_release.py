import getpass, argparse, requests, os

# local imports
from utils.commands import executeCommand, panicIfStderr, printSuccessMessage, printErrorMessage

GITHUB_LINK = "@api.github.com/repos/tischfieldlab/moseq2-build/releases"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("assetType", nargs="?", help="Specify either singularity or docker asset to download from the latest release.")
    parser.add_argument("-o", "--output", nargs='?', help="Specify output folder for the downloaded images.",
        dest="outputPath", default=os.getcwd(), type=str)

    username = input("Enter GitHub username: ")
    password = getpass.getpass(prompt="Enter password: ")

    args = parser.parse_args()
    assetsIndices = [0, 1]

    if (args.assetType == 'singularity'):
        assetsIndices = [1]

    elif (args.assetType == 'docker'):
        assetsIndices[0]

    if username == ' ':
        printErrorMessage("Please enter non-empty username.")
        exit(1)

    if password == ' ':
        printErrorMessage("Please enter non-empty password.")
        exit(1)

    downloadAssets(username, password, assetsIndices, args.outputPath)
    printSuccessMessage("All commands executed\n\n")
#end main()

def downloadAssets(uname, pword, indices, outputPath):
    """ Downloads the latest assets from the moseq2-build repository.

    :type uname: String
    :param uname: GitHub username.

    :type pword: String
    :param pword: GitHub password.

    :type indices: List of Strings
    :param indices: Contains what assets we are going to download.
    Either singularity or docker image, or both.
    """
    url = "https://" + uname + ":" + pword + GITHUB_LINK
    x = requests.get(url + "/latest")

    msg = "Received release info"

    print("\nGetting latest release info")

    if x.status_code != 200:
        printErrorMessage(msg + '\n')
        exit(1)

    else:
        printSuccessMessage(msg)

    jsonData = x.json()
    for i in indices:
        asset = jsonData["assets"][i]
        releaseId = str(asset["id"])
        assetName = asset["name"]
        header = {'Accept': 'application/octet-stream'}
        finalCom = url + "/assets/" + releaseId
        msg = "Downloaded asset " + assetName

        x = requests.get(finalCom, headers=header)
        if (x.status_code != 200):
            printErrorMessage(msg + '\n')
            exit(1)
        else:
            printSuccessMessage(msg)

        assetOutput = os.path.join(outputPath, assetName)
        with open(assetOutput, 'wb') as f:
            f.write(x.content)
#end downloadAssets()

if __name__ == '__main__':
    main()
