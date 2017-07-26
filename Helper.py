



def throwIfStringIsNullOrEmpty(str,name):
    if not str:
        raise Exception(name + "is null")
    elif len(str.strip())<=0:
        raise Exception(name + "is empty")


def isStringIsNullOrEmpty(str):
    if not str or len(str.strip())<=0:
       return True
    return False

