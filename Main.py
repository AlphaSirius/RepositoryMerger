import git
import os,sys
import datetime
import getpass
import shutil
from git import Repo
from Comparator.BranchComparator import oldBaseAndOldApexBranchSanityCheck, processFilesOnlyInApex

bareGitRepoMasterBranch = 'origin_master'

def main():

    if len(sys.argv) > 6 :
        repoGitUrl = sys.argv[1]
        oldBaseBranch = sys.argv[2]
        oldApexBranch = sys.argv[3]
        newBaseBranch = sys.argv[4]
        gitUserId = sys.argv[5]
        password = sys.argv[6]
    else:
        repoGitUrl = input("Please enter the Github repository Url : ")
        oldBaseBranch = input("Please enter old base branch : ")
        oldApexBranch = input("Please eneter old apex branch : ")
        newBaseBranch = input("Please enter new base branch : ")
        gitUserId = input("Please enter userId : ")
        password = getpass.getpass("Enter your Password:")

# create git repo clone url
    gitRepoClonableUrl = repoGitUrl[:8] + gitUserId+":"+password+"@" + repoGitUrl[8:]

# create a directory for merge operation
    mainDir = datetime.datetime.now().strftime("%B_%d_%Y_%H_%M_%S")
   # parentWorkingDirectory = os.getcwd()
    parentWorkingDirectory = "C:\\Users\\sunil\\Desktop\\Repos\\Del"
    os.makedirs(mainDir)

# clone git repo and switch to master
    #parentRepoPath = os.path.join(os.path.sep,parentWorkingDirectory,mainDir,bareGitRepoMasterBranch.replace("/","_"))
    #git.Git().clone(gitRepoClonableUrl.strip(),parentRepoPath)
    parentRepoPath ='C:\\Users\\sunil\\Desktop\\Repos\\DialerRepo\\origin_master'
    originalRepo = Repo(parentRepoPath)

# create a new repo and switch its branch to old base
    oldBaseRepoPath = os.path.join(os.path.sep,parentWorkingDirectory,mainDir,oldBaseBranch.replace("/","_"))
    shutil.copytree(parentRepoPath,oldBaseRepoPath)
    oldBaseBranchRepo = Repo(oldBaseRepoPath)
    oldBaseBranchRepo.git.checkout(oldBaseBranch)


# create a new repo and switch its branch to old apex
    oldApexRepoPath =  os.path.join(os.path.sep,parentWorkingDirectory,mainDir,oldApexBranch.replace("/","_"))
    shutil.copytree(parentRepoPath,oldApexRepoPath)
    oldApexBranchRepo = Repo(oldApexRepoPath)
    oldApexBranchRepo.git.checkout(oldApexBranch)

# create a new repo and switch its branch to new base
    newBaseRepoPath = os.path.join(os.path.sep,parentWorkingDirectory,mainDir,newBaseBranch.replace("/","_"))
    shutil.copytree(parentRepoPath, newBaseRepoPath)
    newBaseBranchRepo = Repo(newBaseRepoPath)
    newBaseBranchRepo.git.checkout(newBaseBranch)


# Sanity check

    onlyInBase = []
    onlyInApex = []
    commonInterestingFiles = []
    oldBaseAndOldApexBranchSanityCheck(oldBaseRepoPath, oldApexRepoPath,newBaseRepoPath,onlyInBase,onlyInApex,commonInterestingFiles)

    processFilesOnlyInApex(onlyInApex,newBaseRepoPath, oldApexRepoPath)

    print("merge completed")


if __name__=='__main__':
    main()