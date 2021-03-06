import os
import platform
import time
from subprocess import call
import datetime
import random, string

import re


def randomWord(length):
   return ''.join(random.choice(string.ascii_lowercase ) for i in range(length))

from Git.FileStore.FileStoreHelper import readFile, createFile, deleteFile

windowsTerminalStartCommand = " start cmd /K \""
windowsTerminalExitCommand = " exit \""
windowsOutputRedirectionOperator =" > "

linuxTerminalStartCommand = "xterm -e \""
linuxTerminalExitCommand = " exit \""
linuxOutputRedirectionOperator = " > "

commandLogicalAnd = " && "

def executeCommandOnWindows(command, directory, outputRequired):
    outputTempFileName = datetime.datetime.now().strftime("%B_%d_%Y_%H_%M_%S") + randomWord(12) + ".txt"
    tmpFile = os.path.join(os.path.sep, os.getcwd(), outputTempFileName)
    createFile(tmpFile)
    cmd = windowsTerminalStartCommand + command + windowsOutputRedirectionOperator + tmpFile + commandLogicalAnd + windowsTerminalExitCommand
    call(cmd, shell=True, cwd=directory)
    file = readFile(tmpFile, outputRequired)
    #deleteFile(tmpFile)
    return file


def executeCommandOnLinux(command, directory, outputRequired):
    outputTempFileName = datetime.datetime.now().strftime("%B_%d_%Y_%H_%M_%S") + randomWord(12) + ".txt"
    tmpFile = os.path.join(os.path.sep, os.getcwd(), outputTempFileName)
    createFile(tmpFile)
    command = linuxCommandCleaner(command)
    cmd = linuxTerminalStartCommand + command + linuxOutputRedirectionOperator + tmpFile + commandLogicalAnd + linuxTerminalExitCommand
    call(cmd, shell=True, cwd=directory)
    file = readFile(tmpFile, outputRequired)
    #deleteFile(tmpFile)
    return file

def linuxCommandCleaner(comamnd):
    return comamnd.replace("\"","'")

def executeCommandOnShell(command, directory, outputRequired):
    time.sleep(2)
    if re.search("windows", platform.system(), re.IGNORECASE):
        return executeCommandOnWindows(command, directory, outputRequired)
    elif re.search("linux", platform.system(), re.IGNORECASE):
        return executeCommandOnLinux(command, directory, outputRequired)