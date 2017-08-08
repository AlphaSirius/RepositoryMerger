import difflib
import os

import re
from shutil import copyfile

magicNumberForContext = 50

from Git.FileStore.IndusFileChangeHelper import isLineIsChangedByIndus, isLineIsRemovedByIndus


def copyFile(src, dst):
    recursivelyCreateAFilePath(dst[:dst.rfind(os.path.sep)])
    copyfile(src, dst)


def recursivelyCreateAFilePath(filePath):
    if not os.path.exists(filePath):
        recursivelyCreateAFilePath(filePath[:filePath.rfind(os.path.sep)])
        os.mkdir(filePath)

def mergeFileOfFolder(baseFilePath, baseRepoPath, apexRepoPath, newApexRepoPath):
    apexFilePath = baseFilePath.replace(baseRepoPath, apexRepoPath)
    newApexFilePath = baseFilePath.replace(baseRepoPath, newApexRepoPath)
    # make a copy of newBaseFile
    newApexFilePathCopy = os.path.join(os.path.sep, newApexFilePath[:newApexFilePath.rfind(os.path.sep)],
                                       "copy.txt")
    copyFile(newApexFilePath, newApexFilePathCopy)
    mergeFile(baseFilePath, apexFilePath, newApexFilePath)
    os.remove(newApexFilePathCopy)

def createListFromnDiff(diffofFoles):
    return [item for item in diffofFoles]




def mergeFile(baseFilePath, apexFilePath, newApexFilePath):
    mergendiff13 = difflib.ndiff(open(newApexFilePath, encoding="utf-8").readlines(),
                                 open(apexFilePath, encoding="utf-8").readlines())

    mergendiffForList = difflib.ndiff(open(newApexFilePath, encoding="utf-8").readlines(),
                                 open(apexFilePath, encoding="utf-8").readlines())

    diffList = createListFromnDiff(mergendiffForList)
    with open(newApexFilePath, "w", encoding="utf-8") as textobj:
        index = 0
        for n in mergendiff13:

            contextOfLine = createContextOfLine(diffList,index)
            index = index +1

            writeLine(n, textobj, baseFilePath, contextOfLine)



def createContextOfLine(diffList,index):
    context = []
    counter = 1
    while index-counter >= 0 and magicNumberForContext-counter >0:
        context.append(diffList[index-counter])
        counter = counter +1
    counter = 1
    while index + counter < len(diffList) and magicNumberForContext-counter >0:
        context.append(diffList[index+counter])
        counter = counter +1
    return context

def writeLine(line, textobj, baseFilePath, contextOfLine):
    if len(line[2:].strip()) == 0:
        line = line[2:]
        textobj.write(line)
    elif (line.startswith("+ ")):
        if isLineIsChangedByIndus(line,baseFilePath, contextOfLine):
            line = line[2:]
            textobj.write(line)
        else:
            line = "  script?oldApex  " + line[2:]
            textobj.write(line)
    elif (line.startswith("- ")):
        if isLineIsRemovedByIndus(line,baseFilePath, contextOfLine):
            line = line[2:]
            #textobj.write(line)
        else:
            line = " script?newBase  " + line[2:]
            textobj.write(line)
    elif line.startswith("  "):
        line = line[2:]
        textobj.write(line)



