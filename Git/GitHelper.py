
import subprocess
from subprocess import check_output

from Git.Log.LogHelper import info, verbose, verboseList
from Git.Shell.ShellHelper import executeCommandOnShell

masterBranchName = "master"
import os
import time


def checkValidityOfBranch(branchName, repoPath):
    result = executeCommandOnShell("git branch -a",repoPath)
    verbose("git branch -a result in " +repoPath)
    verboseList(result)
    value = branchName in result
    info(branchName + "  exists in "+repoPath+":" + str(value))
    print(branchName + " exists in " + repoPath + ":" + str(value))
    return branchName



def pullLatestChangesFromRemoteRepo(repoPath,repoUrl):
    print(executeCommandOnShell("git pull -a",repoPath))


def cloneRepo(repoPath,repoUrl):
    cloneCommand = "git clone " + repoUrl
    executeCommandOnShell(cloneCommand, repoPath)


def checkoutBranch(repoPath, branchName):
    checkoutCommand = "git checkout -f " + branchName
    executeCommandOnShell(checkoutCommand, repoPath)


def gitAddAll(repoPath):
    executeCommandOnShell("git add -A",repoPath)

def gitCommit(repoPath, commitMessage):
    commitCommand = "git commit -m \"" + commitMessage +"\""
    executeCommandOnShell(commitCommand, repoPath)