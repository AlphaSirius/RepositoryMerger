import re

filesCrossedIndusSection = []


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
    if fileName in filesCrossedIndusSection:
        return True
    return checkLineInContext(line,contextOfLine)


def isLineIsRemovedByIndus(line, fileName, contextOfLine):
    return checkLineInContext(line,contextOfLine)


def checkLineInContext(line,lineContext):
    for item in lineContext:
        if re.search("indus", item, re.IGNORECASE) and line[2:].strip() in item:
            return True
    return False