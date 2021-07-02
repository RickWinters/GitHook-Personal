from FileClasses.Warning import Warning
from FileClasses.Variable import *
from FileClasses.HelperFunctions import *
from CodingStandards.CommonLists import *

class General:
    """
    Class containing implemented coding standards in the "GENERAL" category
    """
    class IfStatementBlock:
        def __init__(self, level, index, match, linenumber):
            self.level = level
            self.index = index
            self.match = match
            self.linenumber = linenumber


    def __init__(self, filename):
        self.filename = filename
        self.warnings = []

        self.allowedhandleassignments = [":get-buffer-handle(", ":before-buffer", ":handle"]
        self.classmethodvars = []
        self.toCompilePaths = []
        self.includes = []
        self.checkIfStatementOperatorOutline = False
        self.ifStatementBlocks = []
        self.currentIfStatementLevel = 0
        self.isDataset = False
        self.isTempTable = False
        self.hasDatasetMasterToCompile = True
        self.filename = filename
        self.doSubstituteCheck = False
        self.substituteLineNumber = 0
        self.substituteind = 0
        self.substituteassignee = ""
        self.substituteinstring = False
        self.substitutebracketlevel = 0

        slashind = filename.rfind("/")
        filename = filename[slashind + 1:]
        if filename.startswith("ds") and filename.endswith(".i"):
            self.isDataset = True
            self.hasDatasetMasterToCompile = False
        if filename.startswith("tt") and filename.endswith(".i"):
            self.isTempTable = True

    def newAnalyse(self, line, fullline, linenumber):
        self.trackmethodvars(line, linenumber)
        self.runWithPW(line, linenumber, self.filename)
        self.varCleanUpInClassMethod(line, linenumber, self.filename, fullline)
        self.noWriteXML(line, linenumber, self.filename)
        self.noViewBox(line, linenumber, self.filename)
        self.noSingleQuotesInHardcodedText(line, linenumber, self.filename)
        self.includeTTorDSMustHaveToCompileStatement(line, linenumber, self.filename)
        self.ifStatementOperatorOutline(line, linenumber, self.filename, fullline)
        self.SubstituteOutlining(line, linenumber, self.filename, fullline)


    def analyse(self, filename, lines, fulllines):
        """ Runs each line of source code in 'lines' against the implemented coding standards"""
        for linenumber, line in enumerate(lines):
            self.trackmethodvars(line, linenumber)
            self.runWithPW(line, linenumber, filename)
            self.varCleanUpInClassMethod(line, linenumber, filename, lines)
            self.noWriteXML(line, linenumber, filename)
            self.noViewBox(line, linenumber, filename)
            self.noSingleQuotesInHardcodedText(line, linenumber, filename)
            self.includeTTorDSMustHaveToCompileStatement(line, linenumber, filename)
            self.ifStatementOperatorOutline(line, linenumber, filename, fulllines)
            self.SubstituteOutlining(line, linenumber, filename, fulllines)
            pass

        if self.isDataset and not self.hasDatasetMasterToCompile:
            self.warnings.append(
                Warning(
                    filename,
                    0,
                    "GENERAL: Missing @mastertocompile(module='" + self.filename  + "'). Use single quotes."))

        return self.warnings

    def trackmethodvars(self, line, linenumber):
        currentvar = extractVar(line, linenumber)
        if currentvar:
            self.classmethodvars.append(currentvar)

        if line.startswith("end method."):
            self.classmethodvars.clear()

    def runWithPW(self, line, linenumber, filename):
        """ Run command only on files with .p extension or .w extension."""
        if line.startswith("run"):
            if ".r" in line:
                self.warnings.append(Warning(filename, linenumber, "GENERAL: Run statement may not call .r file"))
            if "\\" in line:
                self.warnings.append(Warning(filename, linenumber, "GENERAL: Backslash not allowed in Run statement"))

    def varCleanUpInClassMethod(self, line, linenumber, filename, lines):
        """
        Keeps track of any instatiated objects/handles in a class method and returns a warning if object / handle is
        not cleaned up.
        Any variable that has an object as type or of type 'handle' starting with "tt" in the name is not kept track of.
        """

        if checkInLine(self.allowedhandleassignments, line):
            isind = line.find("=")
            varname = line[:isind].strip()
            for i, var in enumerate(self.classmethodvars):
                if (var.name == varname
                        and var.type == "handle"):
                    self.classmethodvars.pop(i)
                    break

        if line.startswith("delete object"):
            startind = len("delete object")
            spaceind = line.find(" ", startind + 1)
            varname = line[startind + 1:spaceind]
            for i, var in enumerate(self.classmethodvars):
                if var.name == varname:
                    self.classmethodvars.pop(i)
                    break

        if line.startswith("end method."):
            vars = [var for var in self.classmethodvars if var.type not in allowedvartypes]
            for var in vars:
                if var.type == "handle":
                    self.warnings.append(
                        Warning(
                            filename,
                            var.linenumber,
                            "GENERAL: Handle \"" + var.name + "\" not cleaned up (check spelling (capital sensitive))"))
                    continue
                else:
                    self.warnings.append(
                        Warning(
                            filename,
                            var.linenumber,
                            "GENERAL: Variable \"" + var.name + "\" not cleaned up"))

    def noWriteXML(self, line, linenumber, filename):
        """ Any line of code containing 'write-xml' will return a warning."""
        if "write-xml" in line:
            self.warnings.append(Warning(filename, linenumber, "GENERAL: Delete write-xml statement"))

    def noViewBox(self, line, linenumber, filename):
        """ Any line of code containing 'view-as alert box' will return a warning."""
        if "view-as alert-box" in line:
            self.warnings.append(Warning(filename, linenumber, "GENERAL: Delete alert-box statement"))

    def noSingleQuotesInHardcodedText(self, line, linenumber, filename):
        """
        Character assignments or hardcoded text using single quotes will return a warning,
        except in @tocompile statements.
        """
        if "'" in line \
                and not (line.startswith("@tocompile") or
                         line.startswith("@mastertocompile")):
            self.warnings.append(
                Warning(filename, linenumber, "GENERAL: Use double quotes (\"\") instead of single quotes ('') "))

    def includeTTorDSMustHaveToCompileStatement(self, line, linenumber, filename):
        """
        If you include a file starting with 'ds' or 'tt', and there is no @tocompile statement for that
        a warning will be returned.
        """
        #@tocompile statements should always be before includes, so we can check for them seperately
        if ((line.startswith("@tocompile")
                and not self.isDataset) or
                (line.startswith("@mastertocompile")
                 and self.isDataset)):
            ind1 = line.find("'")
            ind2 = line.find("'", ind1 + 1)
            path = line[ind1 + 1:ind2]
            self.toCompilePaths.append(path.lower())
            if self.isDataset:
                filename = self.filename[1:-2]
                if path.lower() == filename.lower():
                    self.hasDatasetMasterToCompile = True

        if (line.startswith("{") and line.endswith("}")
                and not (self.isDataset or self.isTempTable)):
            path = line[1:-1]
            slashind = path.rfind("/")
            file = path[slashind + 1:]
            if file.startswith("tt") or file.startswith("ds"):
                dotind = path.rfind(".")
                path = path[:dotind]
                if not path.lower() in self.toCompilePaths:
                    self.warnings.append(
                        Warning(
                            filename,
                            linenumber,
                            "GENERAL: Missing \"@tocompile(module='" + path + "').\" Use single quotes."))

    def ifStatementOperatorOutline(self, line, linenumber, filename, fullline):
        """
        checks outlining of the operators in an if statement if there are multiple operators in an if statement.
        """

        if line.startswith("if "):
            self.checkIfStatementOperatorOutline = True
            self.currentIfStatementLevel = 1
            ind, match = indexOfFirstMatch(operatorList, fullline)
            self.ifStatementBlocks.append(
                self.IfStatementBlock(1,ind,match,linenumber))

        if self.checkIfStatementOperatorOutline:
            brackets = countCharInString("(", line)
            brackets -= countCharInString(")", line)
            if brackets > 0:
                self.currentIfStatementLevel += 1
                ind, match = indexOfFirstMatch(operatorList, fullline)
                self.ifStatementBlocks.append(
                    self.IfStatementBlock(self.currentIfStatementLevel,ind,match,linenumber))

            ifStatementBlocks = [block for block in self.ifStatementBlocks if block.level == self.currentIfStatementLevel]

            if len(ifStatementBlocks) > 0: #catch the error that self.isStatementBlocks is empty
                ifStatementBlock = ifStatementBlocks[0]
            else:
                return
            ind, match = indexOfFirstMatch(operatorList, fullline)
            if ifStatementBlock.index == -1:
                ifStatementBlock.index = ind
                ifStatementBlock.match = match
                ifStatementBlock.linenumber = linenumber
            else:
                length = len(match)
                diff = length - len(ifStatementBlock.match)
                if (not ifStatementBlock.index == ind + diff
                        and not ind == -1):
                    self.warnings.append(
                        Warning(
                            filename,
                            linenumber,
                            "GENERAL: Operator \"" + match + "\" not correctly outlined within if-statement with \"" + ifStatementBlock.match + "\" on line " + str((ifStatementBlock.linenumber + 1))))

            if brackets < 0:
                i = [i for i, block in enumerate(self.ifStatementBlocks) if block.level == self.currentIfStatementLevel][0]
                self.ifStatementBlocks.pop(i)
                self.currentIfStatementLevel -= 1

        if "then" in line:
            self.checkIfStatementOperatorOutline = False
            self.ifStatementBlocks.clear()
            self.currentIfStatementLevel = 0

    def SubstituteOutlining(self, line, linenumber, filename, fullline):
        """
        Checks if statements in substitute() are outlined correctly.
        The substitute string can consist of multiple lines of code and must follow other coding standards.
        Each parameter must be on a new line, left-outlined with the first letter of the substitute string.
        substitute parameters that are local variables as a character must be withing quoter()

        define variable fieldvalue as character no-undo.
        whereclause = substitute("|for each &1,
                                  |    each &2 where &2.field = &3
                                  |              and &2.oeuae = &4",
                                  |ttname1,
                                  |ttname2,
            quoter required -->   |quoter(fieldvalue),
                                  |"hardcoded string here").
        """
        skipcheck = False
        if "substitute(" in line and not line.endswith("."):
            self.doSubstituteCheck = True
            ind = fullline.find("substitute(")
            self.substituteind = fullline.find("\"", ind)
            self.substitutebracketlevel = bracketLevelAtIndex(fullline, self.substituteind)
            self.substituteLineNumber = linenumber
            self.substituteinstring = indexInString(len(line) - 1, line, self.substituteinstring)
            skipcheck = True
            isind = line.find(" = ", ind)
            if isind > -1:
                self.substituteassignee = line[:isind].strip()
            if (not line.endswith("\",")
                    and not self.substituteinstring):
                self.warnings.append(
                    Warning(
                        filename,
                        linenumber,
                        "GENERAL: Put substitute pararmeters on next line"))

        if self.substituteinstring:
            skipcheck = True
            self.substituteinstring = indexInString(len(line) -1, line, self.substituteinstring)
            if not self.substituteinstring:
                if not line.endswith("\","):
                    self.warnings.append(
                        Warning(
                            filename,
                            linenumber,
                            "GENERAL: Put substitute pararmeters on next line"))
            # self.substitutebracketlevel += countCharInString("(", line[self.substituteind:])
            # self.substitutebracketlevel -= countCharInString(")", line[self.substituteind:])
            # if self.substitutebracketlevel == 0:
            #     self.doSubstituteCheck = False:


        if (self.doSubstituteCheck
                and not skipcheck
                and not line == "."):
            ind = len(fullline) - len(fullline.lstrip())
            if ind != (self.substituteind + 1):
                self.warnings.append(
                    Warning(
                        filename,
                        linenumber,
                        "GENERAL: Substitute parameter not outlined correctly with substitute on line " + str(self.substituteLineNumber + 1)))
            var = [var for var in self.classmethodvars if var.name in line]
            if var:
                var = var[0]
                if (var.type == "character"
                        and not var.name == self.substituteassignee):
                    ind1 = line.find("quoter(")
                    ind2 = line.find(")",ind1)
                    matchind = line.find(var.name)
                    if ind1 == -1 or not (ind1 < matchind < ind2):
                        self.warnings.append(
                            Warning(
                                filename,
                                linenumber,
                                "GENERAL: variables of type character must be withing 'quoter([var]) in a substitute statement"))
                pass

        bracketLevel = bracketLevelAtIndex(fullline, -1, self.substitutebracketlevel)
        if (self.doSubstituteCheck
                and bracketLevel == self.substitutebracketlevel):
            self.doSubstituteCheck = False
            self.substituteind = 0
            self.substituteLineNumber = 0
            self.substituteassignee = ""
            self.substituteinstring = False
            self.substitutebracketlevel = 0

        pass
