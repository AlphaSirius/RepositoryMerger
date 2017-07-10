import filecmp
from distutils import dir_util
import os, sys
from shutil import copyfile
import difflib
import re


def inflateDirectoryContent(dirPath, list):
    for root, dirs, files in os.walk(dirPath):
        for name in files:
            list.append(os.path.join(os.path.sep, root, name))
        for dir in dirs:
            inflateDirectoryContent(os.path.join(os.path.sep, root, dir), list)


def inflateContent(pathList, list, basePath):
    for item in pathList:
        if os.path.isfile(os.path.join(os.path.sep, basePath, item)):
            list.append(os.path.join(os.path.sep, basePath, item))
        elif os.path.isdir(os.path.join(os.path.sep, basePath, item)):
            inflateDirectoryContent(os.path.join(os.path.sep, basePath, item), list)


def oldBaseAndOldApexBranchSanityCheck(oldBaseRepoPath, oldApexRepoPath, newBaseRepoPath, onlyInLeft, onlyInRight,
                                       commonInterestingFiles):
    dirCompare = filecmp.dircmp(oldBaseRepoPath, oldApexRepoPath)
    inflateContent(dirCompare.left_only, onlyInLeft, oldBaseRepoPath)
    inflateContent(dirCompare.right_only, onlyInRight, oldApexRepoPath)

    if len(dirCompare.left_only) > 0:
        print("Old base has few files which are not present in old Apex. Basic Sanity check failed")
        sys.exit(1)

    for everyCommonFile in dirCompare.common_files:
        fileComp = filecmp.cmp(os.path.join(os.path.sep, oldBaseRepoPath, everyCommonFile),
                               os.path.join(os.path.sep, oldApexRepoPath, everyCommonFile))

        if not fileComp:
            # print(everyCommonFile)
            oldBaseFilePath = os.path.join(os.path.sep, oldBaseRepoPath, everyCommonFile)
            oldApexFilePath = os.path.join(os.path.sep, oldApexRepoPath, everyCommonFile)
            newBaseFilePath = os.path.join(os.path.sep, newBaseRepoPath, everyCommonFile)
            threeWayMerge(oldBaseFilePath, oldApexFilePath, newBaseFilePath)
            # write a function to merge these files .

    if (len(dirCompare.common_dirs) > 0):

        for everyCommonDir in dirCompare.common_dirs:
            oldBaseCommonDirPath = os.path.join(os.path.sep, oldBaseRepoPath, everyCommonDir)
            oldApexCommonDirPath = os.path.join(os.path.sep, oldApexRepoPath, everyCommonDir)
            newBaseCommonDirPath = os.path.join(os.path.sep, newBaseRepoPath, everyCommonDir)
            oldBaseAndOldApexBranchSanityCheck(oldBaseCommonDirPath, oldApexCommonDirPath, newBaseCommonDirPath,
                                               onlyInLeft, onlyInRight, commonInterestingFiles)


def recursivelyCreateAFilePath(filePath):
    if not os.path.exists(filePath):
        recursivelyCreateAFilePath(filePath[:filePath.rfind(os.path.sep)])
        os.mkdir(filePath)


def processFilesOnlyInApex(listOfFilesOnlyPresentInApex, newBaseRepoPath, oldApexRepoPath):
    for item in list(set(listOfFilesOnlyPresentInApex)):
        if os.path.exists(item.replace(oldApexRepoPath, newBaseRepoPath, 1)):

            # error this should not happen, Rename this file and make it a case of  1,0,0 (oldApex,oldBase,newBase) and try again
            print(
                "This should not happen, Rename this file and make it a case of  1,0,0 (oldApex,oldBase,newBase) and try again" + item)

        else:
            # copy that file from old apex to new apex+
            src = item
            dst = item.replace(oldApexRepoPath, newBaseRepoPath, 1)
            recursivelyCreateAFilePath(dst[:dst.rfind(os.path.sep)])
            copyfile(src, dst)


def threeWayMerge(oldBaseFilePath, oldApexFilePath, newBaseFilePath):
    if not os.path.exists(newBaseFilePath):
        # print("This should not happen, file is removed in latest changes. Manualy needs to merge diffs")
        print(
            "This should not happen, file is removed in latest changes. Manualy needs to merge diffs" + oldApexFilePath)
    else:
        merger(newBaseFilePath, oldApexFilePath, oldBaseFilePath)


def merger(newBaseFilePath, oldApexFilePath, oldBaseFilePath):
    merge13 = difflib.ndiff(open(newBaseFilePath, encoding="utf-8").readlines(),
                           open(oldApexFilePath, encoding="utf-8").readlines())
    diff12 = strippedNdiffOfFiles(open(oldApexFilePath, encoding="utf-8"), open(oldBaseFilePath, encoding="utf-8"))
    diff13 = strippedNdiffOfFiles(open(newBaseFilePath, encoding="utf-8"), open(oldBaseFilePath, encoding="utf-8"))

    # make a copy of newBaseFile
    newBaseFilePathCopy = os.path.join(os.path.sep, newBaseFilePath[:newBaseFilePath.rfind(os.path.sep)], "copy.txt")
    copyfile(newBaseFilePath, newBaseFilePathCopy)

    with open(newBaseFilePath, "w", encoding="utf-8") as textobj:

        for n in merge13:

            if (n.startswith("+ ")):
                occuranceOfLineInOldBase = findOccuranceOfLine(n[2:], oldBaseFilePath)
                occuranceOfLineInOldApex = findOccuranceOfLine(n[2:], oldApexFilePath)
                if len(occuranceOfLineInOldBase) <= 0 or \
                                n.replace("+ ", "", 1).strip() == "/*" or \
                                n.replace("+ ", "", 1).strip() == "//" or \
                                n.replace("+ ", "", 1).strip() == "/**" or \
                                n.replace("+ ", "", 1).strip() == "*/":
                    n = n.replace("+ ", '', 1)
                    textobj.write(n)
                elif n.startswith("+ ") and len(n.replace("+ ", "", 1).strip()) == 0 or \
                                isLineInDiff(n, diff12) == False or \
                                        len(occuranceOfLineInOldBase) == 1 and len(occuranceOfLineInOldApex) == 1:
                    print(".")
                else:
                    n = n.replace("+ ", '?+INDUS*', 1)
                    textobj.write(n)

            elif (n.startswith("- ")):
                occuranceOfLineInOldBase = findOccuranceOfLine(n[2:], oldBaseFilePath)
                occuranceOfLineInNewBase = findOccuranceOfLine(n[2:], newBaseFilePathCopy)
                if len(occuranceOfLineInOldBase) <= 0:
                    n = n.replace("- ", '', 1)
                    textobj.write(n)
                elif n.startswith("- ") and len(n.replace("- ", " ", 1).strip()) == 0 or isLineInDiff(n, diff13) == False:
                    # print("line removed : " + n)
                    print("")
                else:
                    n = n.replace("- ", '?-IDH*', 1)
                    textobj.write(n)

            elif n.startswith("  "):
                n = n[2:]
                textobj.write(n)

    os.remove(newBaseFilePathCopy)


def strippedNdiffOfFiles(srcFile, dstFile):
    diff = difflib.ndiff(srcFile.readlines(), dstFile.readlines())
    return [l.strip() for l in diff if l.startswith('+ ') or l.startswith('- ')]


def findOccuranceOfLine(lineToSearch, srcFilePath):
    srcFile = open(srcFilePath, encoding="utf-8")
    return [num for num, line in enumerate(srcFile, 1) if line.strip() == lineToSearch.strip()]


def isListsAreCompitable(firstList, secondList, magicNumber):
    if len(firstList) != len(secondList):
        return False
    counter = 0
    diffList = []
    while counter < len(firstList):
        diffList.append(abs(firstList[counter] - secondList[counter]))
        counter = counter + 1

    while counter < len(firstList):
        if diffList[counter] > magicNumber:  # magic number
            return False
        counter = counter + 1

    return True


def isLineInDiff(line, diff):
    for item in diff:
        if item.startswith("+ ") or item.startswith("- "):
            item = item[2:]

        if line.startswith("+ ") or line.startswith("- "):
            line = line[2:]

        if line.strip() == item.strip():
            return True

    return False
