import re

filesCrossedIndusSection = []
filesCrossedIdhSection = []


def isLineIsChangedByIndus(line, fileName, contextOfLine):
    if re.search("added by indus", line, re.IGNORECASE):
        return True
    if re.search("changed by indus", line, re.IGNORECASE):
        return True
    if re.search("indus comment start", line, re.IGNORECASE):
        return True
    if re.search("indus comment end", line, re.IGNORECASE):
        return True
    if re.search("commented by indus", line, re.IGNORECASE):
        return True
    if re.search("by indus", line, re.IGNORECASE):
        return True
    if re.search("indus imports", line, re.IGNORECASE):
        return True
    if re.search("Add all Indus changes below this comment and use a functional call in above class", line,
                 re.IGNORECASE):
        filesCrossedIndusSection.append(fileName)
        return True
    if re.search("Add all Indus changes above this comment and use a functional call in above class", line,
                 re.IGNORECASE):
        filesCrossedIndusSection.remove(fileName)
        return True
    if re.search("Indus change", line, re.IGNORECASE):
        return True
    if fileName in filesCrossedIndusSection:
        return True
    return checkLineInContext(line,contextOfLine)


def isLineIsRemovedByIndus(line, fileName, contextOfLine):
    return checkLineInContext(line,contextOfLine)


def isLineIsAddedByOldIDH(line, fileName):
    if re.search("Idh change start", line, re.IGNORECASE):
        filesCrossedIdhSection.append(fileName)
        return True
    if re.search("Idh change end", line, re.IGNORECASE):
        filesCrossedIdhSection.remove(fileName)
        return True
    if re.search("Idh change", line, re.IGNORECASE):
        return True
    if fileName in filesCrossedIdhSection:
        return True

def checkLineInContext(line,lineContext):
    for item in lineContext:
        item = brushContextedLine(item)
        if re.search("indus", item, re.IGNORECASE) and line[2:].strip() in item:
            return True
    return False


def areLineSameWithOppositeSign(lineA, lineB):
    if lineA.startswith("+ ") and lineB.startswith("- "):
        return lineA[2:].strip() == lineB[2:].strip()
    elif lineA.startswith("- ") and lineB.startswith("+ "):
        return lineA[2:].strip() == lineB[2:].strip()
    return False


def isAFalseConflict(line, context):
    return areLineSameWithOppositeSign(line, context[0]) or areLineSameWithOppositeSign(line, context[1]) \
           or areLineSameWithOppositeSign(line, context[2]) or areLineSameWithOppositeSign(line, context[3]) \
           or areLineSameWithOppositeSign(line, context[4]) or areLineSameWithOppositeSign(line, context[5])


def brushContextedLine(line):
    if "/star*" in line and "*star/" in line:
        line = line.replace("/star*","/*")
        line = line.replace("*star/","*/")
    return line