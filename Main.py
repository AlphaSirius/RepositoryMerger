import filecmp
import timeit
from logging import warning

import os, sys
import datetime
import getpass
import shutil

import re

from multiprocessing import Process

from Git.FileStore.FileMerger import copyFile
from Git.FileStore.FileStoreHelper import mergeFiles
from Git.GitHelper import pullLatestChangesFromRemoteRepo, checkValidityOfBranch, cloneRepo, checkoutBranch, gitAddAll, \
    gitCommit
from Git.Log.LogHelper import verbose, errorList, error, info, infoList
from Helper import throwIfStringIsNullOrEmpty

remoteOriginBranchPrefix = "remotes/origin/"
repoEntrySeprator = ","
repoGitUrlSeprator = "#"
parentReferenceDirectoryNameForBaseBranchName = "oldBase"
parentReferenceDirectoryNameForApexBranchName = "oldApex"
parentReferenceDirectoryNameForNEWApexBranchName = "newApex"


def copyInFirst(first, second):
    for item in second:
        first.append(item)
    return first


def getFilesOfFolder(folderPath):
    filesInFolder = []
    for root, dirs, files in os.walk(folderPath):
        for name in files:
            filesInFolder.append(os.path.join(os.path.sep, root, name))
        for dir in dirs:
            filesInFolderAdv = getFilesOfFolder(os.path.join(os.path.sep, root, dir))
            if len(filesInFolderAdv) > 0:
                filesInFolder = copyInFirst(filesInFolder, filesInFolderAdv)
    return filesInFolder


def filesInOnlyFirstFolder(firstFolder, secondFolder):
    filesOnlyInFirst = []
    dirCompare = filecmp.dircmp(firstFolder, secondFolder)

    for item in dirCompare.common_dirs:
        updatedFirstFolder = os.path.join(os.path.sep, firstFolder, item)
        updatedSecondFolder = os.path.join(os.path.sep, secondFolder, item)
        filesOnlyInFirstAdv = filesInOnlyFirstFolder(updatedFirstFolder, updatedSecondFolder)
        if len(filesOnlyInFirstAdv) > 0:
            filesOnlyInFirst = copyInFirst(filesOnlyInFirst, filesOnlyInFirstAdv)
    for item in dirCompare.left_only:
        if os.path.isfile(os.path.join(os.path.sep, firstFolder, item)):
            filesOnlyInFirst.append(os.path.join(os.path.sep, firstFolder, item))
        elif os.path.isdir(os.path.join(os.path.sep, firstFolder, item)):
            filesOnlyInFirstAdv = getFilesOfFolder(os.path.join(os.path.sep, firstFolder, item))
            filesOnlyInFirst = copyInFirst(filesOnlyInFirst, filesOnlyInFirstAdv)
    return filesOnlyInFirst


def checkoutWorksspaceBranch(workSpacePath, branchName, repoListWithUrl):
    for repoWithUrl in repoListWithUrl:
        repoPath = os.path.join(os.path.sep, workSpacePath, getRepoNameFromRepoWithUrl(repoWithUrl))
        checkoutBranch(repoPath, branchName)


def makeAllReposAvailable(reposParentDirectory, repoListWithUrl):
    for repoWithUrl in repoListWithUrl:
        repoPath = os.path.join(os.path.sep, reposParentDirectory, getRepoNameFromRepoWithUrl(repoWithUrl))
        if os.path.exists(repoPath) and os.path.isdir(repoPath):
            verbose(repoPath + "is a present")
        else:
            cloneRepo(reposParentDirectory, getRepoURLFromRepoWithUrl(repoWithUrl))


def checkBranchExistanceInEachRepo(reposParentDirectory, repoListWithUrl, oldBaseBranch, oldApexBranch, newApexBranch):
    for repoWithUrl in repoListWithUrl:
        repoPath = os.path.join(os.path.sep, reposParentDirectory, getRepoNameFromRepoWithUrl(repoWithUrl))
        #checkValidityOfBranch(remoteOriginBranchPrefix + oldBaseBranch, repoPath)
        #checkValidityOfBranch(remoteOriginBranchPrefix + oldApexBranch, repoPath)
        #checkValidityOfBranch(remoteOriginBranchPrefix + newApexBranch, repoPath)
        pOBase = Process(target=checkValidityOfBranch,args=(remoteOriginBranchPrefix + oldBaseBranch, repoPath,))
        pOApex = Process(target=checkValidityOfBranch,args=(remoteOriginBranchPrefix + oldApexBranch, repoPath,))
        pNApex = Process(target=checkValidityOfBranch,args=(remoteOriginBranchPrefix + newApexBranch, repoPath,))
        pOBase.start()
        pOApex.start()
        pNApex.start()
        pNApex.join()
        pOApex.join()
        pOBase.join()


def getRepoNameFromRepoWithUrl(repoWithUrl):
    return repoWithUrl.split(repoGitUrlSeprator)[0]


def getRepoURLFromRepoWithUrl(repoWithUrl):
    return repoWithUrl.split(repoGitUrlSeprator)[1]


def pullLatestChangesFromRemote(reposParentDirectory, repoListWithUrl):
    for repoWithUrl in repoListWithUrl:
        repoPath = os.path.join(os.path.sep, reposParentDirectory, getRepoNameFromRepoWithUrl(repoWithUrl))
        repoUrl = getRepoURLFromRepoWithUrl(repoWithUrl)
        pullLatestChangesFromRemoteRepo(repoPath, repoUrl )

def main():
    if len(sys.argv) > 5:
        reposParentDirectory = sys.argv[1]
        reposListInputStr = sys.argv[2]
        oldBaseBranch = sys.argv[3]
        oldApexBranch = sys.argv[4]
        newApexBranch = sys.argv[5]
    else:
        reposParentDirectory = input("Please enter the parent directory path for  repositories : ")
        reposListInputStr = input("Please enter list of repositories(comma seprated) : ")
        oldBaseBranch = input("Please enter old base branch : ")
        oldApexBranch = input("Please eneter old apex branch : ")
        newApexBranch = input("Please enter new apex branch : ")

    throwIfStringIsNullOrEmpty(reposParentDirectory, "reposParentDirectory")
    throwIfStringIsNullOrEmpty(reposListInputStr, "reposListInputStr")
    throwIfStringIsNullOrEmpty(oldBaseBranch, "oldBaseBranch")
    throwIfStringIsNullOrEmpty(oldApexBranch, "oldApexBranch")
    throwIfStringIsNullOrEmpty(newApexBranch, "newApexBranch")

    repoListWithUrl = reposListInputStr.split(repoEntrySeprator)
    makeAllReposAvailable(reposParentDirectory,repoListWithUrl)                       # check weather all repo specified are available in parent directory, clone if not present
    pullLatestChangesFromRemote(reposParentDirectory,repoListWithUrl)  # just to fetch latest code in all repos
    checkBranchExistanceInEachRepo(reposParentDirectory, repoListWithUrl, oldBaseBranch, oldApexBranch, newApexBranch) # check for branch info

    # Primary conditions are good to go. Create a ref workspace

    # 1. Workspace containing all repos base branches
    parentReferenceDirectoryPathForBaseBranch = os.path.join(os.path.sep, os.getcwd(), "..",
                                                             parentReferenceDirectoryNameForBaseBranchName)
    #shutil.copytree(reposParentDirectory, parentReferenceDirectoryPathForBaseBranch)  # copy
    #checkoutWorksspaceBranch(parentReferenceDirectoryPathForBaseBranch, oldBaseBranch, repoListWithUrl)

    # 2. Workspace containing all repos apex branches
    parentReferenceDirectoryPathForApexBranch = os.path.join(os.path.sep, os.getcwd(), "..",
                                                             parentReferenceDirectoryNameForApexBranchName)
    #shutil.copytree(reposParentDirectory, parentReferenceDirectoryPathForApexBranch)  # copy
    #checkoutWorksspaceBranch(parentReferenceDirectoryPathForApexBranch, oldApexBranch, repoListWithUrl)

    # 3. Workspace containing all repos new apex branches
    parentReferenceDirectoryPathForNEWApexBranch = os.path.join(os.path.sep, os.getcwd(), "..",
                                                                parentReferenceDirectoryNameForNEWApexBranchName)
    #shutil.copytree(reposParentDirectory, parentReferenceDirectoryPathForNEWApexBranch)  # copy
    #checkoutWorksspaceBranch(parentReferenceDirectoryPathForNEWApexBranch, newApexBranch, repoListWithUrl)

    pOBase = Process(target=shutil.copytree, args=(reposParentDirectory,parentReferenceDirectoryPathForBaseBranch,))
    pOApex = Process(target=shutil.copytree, args=(reposParentDirectory, parentReferenceDirectoryPathForApexBranch,))
    pNApex = Process(target=shutil.copytree, args=(reposParentDirectory, parentReferenceDirectoryPathForNEWApexBranch,))
    pOBase.start()
    pOApex.start()
    pNApex.start()
    pNApex.join()
    pOApex.join()
    pOBase.join()

    # checkout branch
    pOBase = Process(target=checkoutWorksspaceBranch, args=(parentReferenceDirectoryPathForBaseBranch, oldBaseBranch,repoListWithUrl,))
    pOApex = Process(target=checkoutWorksspaceBranch, args=(parentReferenceDirectoryPathForApexBranch, oldApexBranch,repoListWithUrl,))
    pNApex = Process(target=checkoutWorksspaceBranch, args=(parentReferenceDirectoryPathForNEWApexBranch, newApexBranch,repoListWithUrl,))
    pOBase.start()
    pOApex.start()
    pNApex.start()
    pNApex.join()
    pOApex.join()
    pOBase.join()



    # now think in term of repos
    checkConstraintBetweenBaseAndApex(parentReferenceDirectoryPathForBaseBranch,
                                      parentReferenceDirectoryPathForApexBranch,
                                      repoListWithUrl)  # There must not be a file in base which is not available in Apex
    copyAllFilesAddedByIndus(parentReferenceDirectoryPathForBaseBranch, parentReferenceDirectoryPathForApexBranch,
                             repoListWithUrl, parentReferenceDirectoryPathForNEWApexBranch)
    mergeAllDiffFiles(parentReferenceDirectoryPathForBaseBranch, parentReferenceDirectoryPathForApexBranch, repoListWithUrl,parentReferenceDirectoryPathForNEWApexBranch)





def mergeAllDiffFiles(oldBaseWorkSpacePath, oldApexWorkSpacePath, repoListWithUrl,newApexWorkSpacePath):
    for repoWithUrl in repoListWithUrl:
        oldBaseRepoPath = os.path.join(os.path.sep, oldBaseWorkSpacePath, getRepoNameFromRepoWithUrl(repoWithUrl))
        oldApexRepoPath = os.path.join(os.path.sep, oldApexWorkSpacePath, getRepoNameFromRepoWithUrl(repoWithUrl))
        newApexRepoPath = os.path.join(os.path.sep, newApexWorkSpacePath, getRepoNameFromRepoWithUrl(repoWithUrl))
        diffFiles = findDiffFilesInFolders(oldBaseRepoPath,oldApexRepoPath)
        error("******* Below files are only present in old base ****")
        errorList(list(set(diffFiles)))
        error("*****************************************************")
        mergeFiles(list(set(diffFiles)), oldBaseRepoPath, oldApexRepoPath, newApexRepoPath)

def getFullPathNames(fullPath,fileNameList):
    return [os.path.join(os.path.sep, fullPath, name) for name in fileNameList]

def filterIndusChagedFiles(fileList):
    filteredList = []
    for item in fileList:
        if re.search(".png", item, re.IGNORECASE) or  re.search("strings.xml", item, re.IGNORECASE) or  re.search("SpecialCharSequenceMgr.java", item, re.IGNORECASE):
            verbose(item)
        else:
            filteredList.append(item)

    return filteredList

def findDiffFilesInFolders(firstFolder,secondFolder):
    diffFiles = []
    dirCompare = filecmp.dircmp(firstFolder, secondFolder)
    if len(dirCompare.diff_files) > 0:
      diffFiles = copyInFirst(diffFiles, getFullPathNames(firstFolder,filterIndusChagedFiles(dirCompare.diff_files)))
    for item in dirCompare.common_dirs:
        firstFolderAdv = os.path.join(os.path.sep, firstFolder, item)
        secondFolderAdv = os.path.join(os.path.sep, secondFolder, item)
        diffFilesAdv = findDiffFilesInFolders(firstFolderAdv,secondFolderAdv)
        if len(diffFilesAdv)>0 :
            diffFiles = copyInFirst(diffFiles, diffFilesAdv)
    return diffFiles

def copyAllFilesAddedByIndus(oldBaseWorkSpacePath, oldApexWorkSpacePath, repoListWithUrl, newApexWorkSpacePath):
    for repoWithUrl in repoListWithUrl:
        oldBaseRepoPath = os.path.join(os.path.sep, oldBaseWorkSpacePath, getRepoNameFromRepoWithUrl(repoWithUrl))
        oldApexRepoPath = os.path.join(os.path.sep, oldApexWorkSpacePath, getRepoNameFromRepoWithUrl(repoWithUrl))
        newApexRepoPath = os.path.join(os.path.sep, newApexWorkSpacePath, getRepoNameFromRepoWithUrl(repoWithUrl))
        filesInOldApexOnly = filesInOnlyFirstFolder(oldApexRepoPath, oldBaseRepoPath)
        if len(filesInOldApexOnly) > 0:
            info("******* Below files are only present in old Apex ****")
            infoList(filesInOldApexOnly)
            info("*****************************************************")
        copyAllFilesToFolder(filesInOldApexOnly, oldApexRepoPath, newApexRepoPath)
        gitAddAll(newApexRepoPath) # add all files as they are added by Indus and there is no conflicts in those files
        gitCommit(newApexRepoPath,"Apex files added by script")


def copyAllFilesToFolder(listOfFile, oldApexRepoPath, newApexRepoPath):
    for item in list(set(listOfFile)):
        dst = item.replace(oldApexRepoPath, newApexRepoPath, 1)
        if os.path.exists(dst):
           warning("This should not happen, Rename this file and make it a case of  1,0,0 (oldApex,oldBase,newBase) and try again" + item)
        else:
           copyFile(item, dst)


def checkConstraintBetweenBaseAndApex(oldBaseWorkSpacePath, oldApexWorkSpacePath, repoListWithUrl):
    for repoWithUrl in repoListWithUrl:
        oldBaseRepoPath = os.path.join(os.path.sep, oldBaseWorkSpacePath, getRepoNameFromRepoWithUrl(repoWithUrl))
        oldApexRepoPath = os.path.join(os.path.sep, oldApexWorkSpacePath, getRepoNameFromRepoWithUrl(repoWithUrl))
        filesInOldBaseOnly = filesInOnlyFirstFolder(oldBaseRepoPath, oldApexRepoPath)
        if len(filesInOldBaseOnly) > 0:
            error("******* Below files are only present in old base ****")
            errorList(filesInOldBaseOnly)
            error("*****************************************************")
            sys.exit(1)


if __name__ == '__main__':
    start = timeit.default_timer()
    print("start time :" + str(start))
    main()
    stop = timeit.default_timer()
    print("total time taken : " + str(stop-start))
