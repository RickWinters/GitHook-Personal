import sys
import pathlib
from git import Repo
from git import NoSuchPathError
from FileClasses.File import File

"""
Author: R.M. Winters
project: CheckCodingStandars / githook
Summary: These python repo is a tool to automatically check Progress coding standards for Cura.

go to README for more information
"""

def HandleSysArgs():
    inputfilename = ""
    doInput = False
    doFullInput = False
    printHelp = False
    askForInput = False
    sortWarnings = False
    sortWarningsReversed = False
    fullFile = False
    Repeat = False
    githook = False

    if len(sys.argv) > 1:
        inputfilename = sys.argv[1]
        if inputfilename == "askInput":
            askForInput = True
            inputfilename = ""
        if inputfilename == "help":
            printHelp = True
            inputfilename = ""
        if inputfilename == "githook":
            githook = True
            inputfilename = ""

    for i, argument in enumerate(sys.argv):
        # print("checking: \"" + argument + "\" " + str(i))
        if i <= 1:
            continue
        if argument == "input":
            doInput = True
        elif argument == "fullinput":
            doFullInput = True
        elif argument == "help":
            printHelp = True
        elif argument == "sortWarnings":
            sortWarnings = True
        elif argument == "sortWarningsReversed":
            sortWarningsReversed = True
        elif argument == "fullFile":
            fullFile = True
        elif argument == "repeat":
            Repeat = True
        else:
            print("unknown system argument " + argument)

    if doFullInput and doInput:
        print("Only use sysarg 'input' or 'fullinput' not both")
        sys.exit(1)

    if doFullInput:
        fullFile = True

    if (printHelp and
            (doInput or
             doFullInput)):
        print("sysarg 'help' can only be used on its own, remove all other sysargs")
        sys.exit(1)

    if (askForInput and
            not (doFullInput or
                 doInput)):
        print("when Asking for input, use keyword 'input' or 'fullinput'")
        sys.exit(1)

    if sortWarnings and sortWarningsReversed:
        print("sortWarnings and sortWarningsReversed can not both be used, pick one")
        sys.exit(1)

    if githook:
        doInput = False
        doFullInput = False
        askForInput = False

    # print("inputfilename        = " + inputfilename)
    # print("doInput              = " + str(doInput))
    # print("doFullInput          = " + str(doFullInput))
    # print("askForInput          = " + str(askForInput))
    # print("printHelp            = " + str(printHelp))
    # print("sortWarnings         = " + str(sortWarnings))
    # print("sortWarningsReversed = " + str(sortWarningsReversed))

    return inputfilename, doInput, doFullInput, askForInput, printHelp, sortWarnings, sortWarningsReversed, fullFile, Repeat

warnings = []
repo = None
path = "c:/dev/cura-117/prj/cura10303"
debugMode = True
# if False, the sysargs (or lack thereof) will set doInput and doFullInput correctly. if True, sysargs are ignored.

doInput = True              # filename in repo input
doFullInput = False          # complete path input
askForInput = False          # manually ask for input
printHelp = False            # print the docstrings of the files
sortWarnings = True         # sort by linenumber ascending
sortWarningsReversed = False # sort by linenumber descending
fullFile = False             # analyse full file
Repeat = False

inputfilename = "client/server/dataaccess/daclient.cls"
files = []
exitCode = 0

if not debugMode:
    inputfilename, doInput, doFullInput, askForInput, printHelp, sortWarnings, sortWarningsReversed, fullFile, Repeat = HandleSysArgs()

if printHelp:
    from CodingStandards.Naming import Naming
    from CodingStandards.General import General
    from CodingStandards.Queries import Queries
    from CodingStandards.Statements import Statements
    from CodingStandards.ErrorHandling import ErrorHandling

    help(File)
    help(Naming)
    help(General)
    help(Queries)
    help(Statements)
    help(ErrorHandling)
    sys.exit(0)

# Handle sysargs
if askForInput:
    if doInput:
        inputfilename = input("please enter filename: --> ")
    elif doFullInput:
        inputfilename = input("pelase enter full path: --> ")

# set repo path and open repo if needed
if not doFullInput:
    try:
        file = open("path.txt")
        lines = file.readlines()
        file.close()
        if lines:
            path = lines[0].strip()
    except FileNotFoundError:
        pass  # path is already set before
    if not doInput:
        try:
            repo = Repo(path)
        except NoSuchPathError:
            print("No git repo found at " + path)
            sys.exit(1)


while True:
    # opens file given by inputfilename where inputfilename diskfile
    if doInput:
        print("Looking for file")
        for diskfile in pathlib.Path(path).rglob("**/*.*"):
            diskfile = str(diskfile).replace("\\", "/").replace(path, "")
            if inputfilename.lower() in diskfile.lower():
                files.append(File(path, diskfile))
                break
        else:
            print("no file found")
            sys.exit(1)
    elif doFullInput:
        files.append(File("", inputfilename))
    else:  # if not input get staged and trackedfiles in git repo, usefull for pre-commit hook.
        stagedFiles = [item for item in repo.index.diff("HEAD")]
        TrackedFiles = [item for item in repo.index.diff(None)]
        files = [File(path, file.a_path, file) for file in stagedFiles]
        files += [File(path, file.a_path, file) for file in TrackedFiles]

    print("Starting code standards check")
    if not (doFullInput or doInput):
        print("Using repo on " + path)
    print("")

    if len(files) == 0:
        print("No files found")
        sys.exit(0)

    for file in files:
        print("Checking " + file.filename)
        file.warnings.clear()
        file.analyse()
        if not fullFile:
            file.getChangedLines()
            file.filterWarnings()
        if sortWarnings:
            file.warnings.sort()
        if sortWarningsReversed:
            file.warnings.sort(reverse=True)
        warnings += file.warnings

    if warnings:
        print("")
        for warning in warnings:
            print(warning)
        print("")
        if (not doInput) and (not doFullInput):
            print("commit anyway with \"git commit -m [message] --no-verify \"")
            print("           or with \"git commit -m [message] -n \"")
            print(" ")
        exitCode = 1
    else:
        print("")
        print("Everything OK")
        print("")
        exitCode = 0

    if Repeat:
        try:
            doRepeat = input("check again? [y/n]: --> ")
        except EOFError:
            print("Automatically answered with 'n' since git-bash does not handle input promts")
            doRepeat = False
        if doRepeat == "y":
            files.clear()
            warnings.clear()
            doRepeat = True
        else:
            doRepeat = False
        if not doRepeat:
            sys.exit(exitCode)
    else:
        sys.exit(exitCode)

