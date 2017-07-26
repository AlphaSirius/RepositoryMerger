import difflib
import time
import os
from shutil import copyfile

from Git.FileStore.FileMerger import mergeFile, recursivelyCreateAFilePath, mergeFileOfFolder


def deleteFile(filePath):
    time.sleep(5)
    try:
        os.remove(filePath)
    except PermissionError:
        return deleteFile(filePath)


def createFile(filePath):
    recursivelyCreateAFilePath(filePath[:filePath.rfind(os.path.sep)])
    f = open(filePath, "w")
    f.close()


def readFile(filePath):
    time.sleep(5)
    try:
        with open(filePath, encoding="utf-8") as file:
            content = file.readlines()
            return [line.strip() for line in content]
    except PermissionError:
        return readFile(filePath)



def mergeFiles(listOfFiles, baseRepoPath, apexRepoPath, newApexRepoPath):
    for baseFilePath in listOfFiles:
        mergeFileOfFolder(baseFilePath, baseRepoPath, apexRepoPath, newApexRepoPath)

