import os

errorFileName = "errors.txt"
warrningFileName = "warrnings.txt"
infoFileName = "info.txt"
verboseFileName = "verbose.txt"


def error(stringMsg):
    with open(os.path.join(os.path.sep, os.getcwd(), errorFileName), "a") as myfile:
        myfile.write(stringMsg)
        myfile.write("\n")


def warrning(stringMsg):
    with open(os.path.join(os.path.sep, os.getcwd(), warrningFileName), "a") as myfile:
        myfile.write(stringMsg)
        myfile.write("\n")


def info(stringMsg):
    with open(os.path.join(os.path.sep, os.getcwd(), infoFileName), "a") as myfile:
        myfile.write(stringMsg)
        myfile.write("\n")


def verbose(stringMsg):
    with open(os.path.join(os.path.sep, os.getcwd(), verboseFileName), "a") as myfile:
        myfile.write(stringMsg)
        myfile.write("\n")


def infoList(list):
    with open(os.path.join(os.path.sep, os.getcwd(), infoFileName), "a") as myfile:
        for str in list:
            myfile.write(str)
            myfile.write("\n")

def errorList(list):
    with open(os.path.join(os.path.sep, os.getcwd(), errorFileName), "a") as myfile:
        for str in list:
            myfile.write(str)
            myfile.write("\n")


def verboseList(list):
    with open(os.path.join(os.path.sep, os.getcwd(), verboseFileName), "a") as myfile:
        for str in list:
            myfile.write(str)
            myfile.write("\n")
