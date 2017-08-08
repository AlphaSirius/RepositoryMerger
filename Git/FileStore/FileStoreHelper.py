import difflib
import time
import os
from shutil import copyfile

from Git.FileStore.FileMerger import mergeFile, recursivelyCreateAFilePath, mergeFileOfFolder


def deleteFile(filePath):
    #time.sleep(5)
    try:
        os.remove(filePath)
    except PermissionError:
        return deleteFile(filePath)


def createFile(filePath):
    recursivelyCreateAFilePath(filePath[:filePath.rfind(os.path.sep)])
    f = open(filePath, "w")
    f.close()


def readFile(filePath, outputRequired):
    #time.sleep(15)
    lines = []
    condition = True
    try:
        while condition:
            with open(filePath, encoding="utf-8") as file:
                content = file.readlines()
                lines = [line.strip() for line in content]
            if len(lines)!= 0 or outputRequired == False:
                condition = False
            else:
                time.sleep(2)
        deleteFile(filePath)
        return lines
    except PermissionError:
        return readFile(filePath)



def mergeFiles(listOfFiles, baseRepoPath, apexRepoPath, newApexRepoPath):
    for baseFilePath in listOfFiles:
        mergeFileOfFolder(baseFilePath, baseRepoPath, apexRepoPath, newApexRepoPath)

