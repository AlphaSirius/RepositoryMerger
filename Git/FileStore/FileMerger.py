import difflib
import os

import re
from shutil import copyfile

magicNumberForContext = 50

from Git.FileStore.IndusFileChangeHelper import isLineIsChangedByIndus, isLineIsRemovedByIndus, isAFalseConflict, \
    isLineIsAddedByOldIDH


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

def getNeighbours(diffList, index):
    context = []
    pLine1 = ""
    pLine2 = ""
    pLine3 = ""
    nLine1 = ""
    nLine2 =""
    nLine3 =""
    counter = 3
    if index - counter >= 0:
        pLine3 = diffList[index - counter]
    counter = 2
    if index - counter >= 0:
        pLine2 = diffList[index - counter]
    counter = 1
    if index - counter >= 0:
        pLine1 = diffList[index - counter]
    if index + counter < len(diffList):
        nLine1 = diffList[index + counter]
    counter = 2
    if index + counter < len(diffList):
        nLine2 = diffList[index + counter]
    counter = 3
    if index + counter < len(diffList):
        nLine3 = diffList[index + counter]
    context.append(pLine3)
    context.append(pLine2)
    context.append(pLine1)
    context.append(nLine1)
    context.append(nLine2)
    context.append(nLine3)
    return context


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
            context = getNeighbours(diffList, index)
            index = index + 1
            writeLine(n, textobj, baseFilePath, contextOfLine, context, newApexFilePath)



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

def writeLine(line, textobj, baseFilePath, contextOfLine, context, newApexFilePath):
    if len(line[2:].strip()) == 0:
        line = line[2:]
        textobj.write(line)
    elif (line.startswith("+ ")):
        if isLineIsChangedByIndus(line,baseFilePath, contextOfLine):
            line = line[2:]
            textobj.write(line)
        elif isAFalseConflict(line, context) or isFileAndroidMk(newApexFilePath) or isLineIsAddedByOldIDH(line, baseFilePath):
            line = line[2:]
        else:
            line = "script?+oldApex:" + line[2:]
            textobj.write(line)
    elif (line.startswith("- ")):
        if isLineIsRemovedByIndus(line,baseFilePath, contextOfLine):
            line = line[2:]
            #textobj.write(line)
        elif isAFalseConflict(line, context) or isFileAndroidMk(newApexFilePath):
            line = line[2:]
            textobj.write(line)
        else:
            line = "script?-newBase:" + line[2:]
            textobj.write(line)
    elif line.startswith("  "):
        line = line[2:]
        textobj.write(line)



def isFileAndroidMk(filename):
    return re.search("Android.mk", filename, re.IGNORECASE)