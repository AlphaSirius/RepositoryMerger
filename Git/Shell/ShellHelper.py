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

linuxTerminalStartCommand = "gnome-terminal"
linuxTerminalExitCommand = " exit \""
linuxOutputRedirectionOperator = "  | "

commandLogicalAnd = " && "

def executeCommandOnWindows(command, directory):
    outputTempFileName = datetime.datetime.now().strftime("%B_%d_%Y_%H_%M_%S") + randomWord(12) + ".txt"
    tmpFile = os.path.join(os.path.sep, os.getcwd(), outputTempFileName)
    createFile(tmpFile)
    cmd = windowsTerminalStartCommand + command + windowsOutputRedirectionOperator + tmpFile + commandLogicalAnd + windowsTerminalExitCommand
    call(cmd, shell=True, cwd=directory)
    file = readFile(tmpFile)
    deleteFile(tmpFile)
    return file


def executeCommandOnLinux(command, directory):
    outputTempFileName = datetime.datetime.now().strftime("%B_%d_%Y_%H_%M_%S") + randomWord(12) + ".txt"
    tmpFile = os.path.join(os.path.sep, os.getcwd(), outputTempFileName)
    createFile(tmpFile)
    cmd = linuxTerminalStartCommand + command + linuxOutputRedirectionOperator + tmpFile + commandLogicalAnd + linuxTerminalExitCommand
    call(cmd, shell=True, cwd=directory)
    file = readFile(tmpFile)
    deleteFile(tmpFile)
    return file

def executeCommandOnShell(command, directory):
    if re.search("windows", platform.system(), re.IGNORECASE):
        return executeCommandOnWindows(command, directory)
    elif re.search("linux", platform.system(), re.IGNORECASE):
        return executeCommandOnLinux(command, directory)