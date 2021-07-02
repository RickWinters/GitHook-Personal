from FileClasses.Warning import Warning
from FileClasses.HelperFunctions import *

class Statements:
    """
    Class containing implemented coding standards in the "STATEMENTS" category
    """
    def __init__(self, filename = "none"):
        self.filename = filename
        self.warnings = []
        self.checkAssign = False
        self.assignisind = 0
        self.assignlinenumber = 0

        self.bracketcount = 0
        self.inIfStatement = False
        self.lastIfStatementEndLineNumber = 0
        self.doFindThen = False

    def newAnalyse(self, line, fullline, linenumber):
        self.ThenDoSameLineAsIf(line, linenumber, self.filename)
        self.AssignIsAlligned(line, linenumber, self.filename, fullline)

    def analyse(self, filename, lines, fulllines):
        """ Runs each line of source code in 'lines' against the implemented coding standards"""
        # for linenumber, line in enumerate(lines):
        #     self.ThenDoSameLineAsIf(line, linenumber, filename, lines)
        #     self.AssignIsAlligned(line, linenumber, filename, fulllines)


        return self.warnings

    #Checks if Then or Then do: is on correct line (at the end of if statement)
    def ThenDoSameLineAsIf(self, line, linenumber, filename):
        """ Checks at if-statements if the keyword 'then' / 'then do:' is not on a new line of code  """
        self.bracketcount = countCharInString("(", line) # counting brackets account for composite if statements, or methodcalls within if statement.
        self.bracketcount -= countCharInString(")", line)

        #check if statement start
        if line.startswith("if"):
            self.inIfStatement = True
            self.doFindThen = True

        #find if statement end
        if not ((self.bracketcount > 0 or
                line.endswith("and") or
                line.endswith("or") or
                line.startswith("or ") or
                line.startswith("and ") or
                line.startswith(":"))
                and self.inIfStatement):
            self.inIfStatement = False
            self.lastIfStatementEndLineNumber = linenumber

        #check if end is on same line number as ifstatement end
        if (self.doFindThen
                and "then" in line):
            self.doFindThen = False
            if not linenumber == self.lastIfStatementEndLineNumber:
                self.warnings.append(
                    Warning(
                        self.filename,
                        linenumber,
                        "STATEMENTS: 'Then' statement not found at end of 'if'"))

        #check if do: is on same line as then
        if ("do:" in line
                and not ("then" in line or
                         "else" in line)):
            self.warnings.append(
                Warning(
                    filename,
                    linenumber,
                    "STATEMENTS: 'Do:' not on correct line in 'if' statement"))

    #Check if assign statements are alligend TBI
    def AssignIsAlligned(self, line, linenumber, filename, fullline):
        """
        starting from each 'assign' checks if the variable assignments are outlined on " = "
        Incorrect:
            assign
              var1 = 0
              variable2 = 0
              .

            assign var1      = 0   --> assignments must start on next line
                   variable2 = 0

        Correct:
            assign
              var1      = 0
              variable2 = 0

            assign
                   var1 = 0 --> False positive, to be fixed
              variable2 = 0
        """
        if line.startswith("assign"):
            if (line.startswith("assign ")
                and " = " in line):
                self.warnings.append(
                    Warning(
                        filename,
                        linenumber,
                        "STATEMENTS: assignments must be on next line of 'assign' keyword"))
            self.checkAssign = True
            pass

        if self.checkAssign:
            if self.assignisind == 0:
                assignisind = fullline.find(" = ")
                self.assignlinenumber = linenumber
                if assignisind > -1:
                    self.assignisind = assignisind
            else:
                assignisind = fullline.find(" = ")
                if assignisind > -1 and assignisind != self.assignisind:
                    self.warnings.append(
                        Warning(
                            filename,
                            linenumber,
                            "STATEMENTS: assign statement not outlined correctly with line " + str(self.assignlinenumber + 1)))

        if line.endswith("."):
            self.checkAssign = False
            self.assignisind = 0
            self.assignlinenumber = 0

    # Help method