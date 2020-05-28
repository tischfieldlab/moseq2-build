import getpass, argparse, requests, os, shutil
from tqdm import tqdm
import tarfile

# local imports
from moseq2_build.utils.commands import executeCommand, panicIfStderr, printSuccessMessage, printErrorMessage
from moseq2_build.utils.constants import ENVIRONMENT_CONFIG, GITHUB_LINK

def getUnamPword():
    """ Prompts the user for a username and password
    for GitHub to use to download the assets.

    :rtype: String username, String password.
    """
    username = input("Enter GitHub username: ")
    password = getpass.getpass(prompt="Enter password: ")
    return username, password
#ned getUnamPword()

def downloadAssets(uname, pword, indices, outputPath, version):
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
    if (version is None):
        x = requests.get(url + "/latest")

    else:
        x = requests.get(url + "/tags/" + version)

    msg = "Received release info"

    print("\nGetting release info")

    if x.status_code != 200:
        printErrorMessage(msg + '\n')
        exit(1)

    else:
        printSuccessMessage(msg + '\n\n')

    jsonData = x.json()
    for i in indices:
        asset = jsonData["assets"][i]
        releaseId = str(asset["id"])
        assetName = asset["name"]
        header = {'Accept': 'application/octet-stream'}
        finalCom = url + "/assets/" + releaseId
        msg = "Downloaded asset " + assetName

        x = requests.get(finalCom, headers=header, stream=True)
        if (x.status_code != 200):
            printErrorMessage(msg + '\n')
            exit(1)

        totalSize = int(x.headers.get('content-length', 0))
        blockSize = 1024 # 1KB
        t = tqdm(total=totalSize, unit='1B', unit_scale=True)

        result = []

        assetOutput = os.path.join(outputPath, assetName)
        with open(assetOutput, 'wb') as f:
            for data in x.iter_content(blockSize):
                t.update(len(data))
                f.write(data)
        t.close()

        tar = tarfile.open(assetOutput)
        p = os.path.splitext(assetOutput)[0]
        p = os.path.splitext(p)[0]
        # p = os.path.splitext(p)[0]
        tar.extractall(path=p)
        tar.close()
        print("Finished unzipping\n")
        os.remove(assetOutput)

        result.append(os.path.join(outputPath, p))

    if totalSize != 0 and t.n != totalSize:
        printErrorMessage(msg + '\n')

    return result
#end downloadAssets()
