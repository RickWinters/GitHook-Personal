from FileClasses.Warning import Warning
from CodingStandards.Statements import Statements
from CodingStandards.Queries import Queries
from CodingStandards.General import General
from CodingStandards.Naming import Naming
from CodingStandards.ErrorHandling import ErrorHandling
from FileClasses.HelperFunctions import parseBlobDataStream
from git import Repo

class File:
    """
    Object for any file of Progress source code to be checked against coding standards.
    Reads the files from disk and keeps track of any warnings returned from code
    """
    def __init__(self, folder, file, diffobject = None):
        self.warnings = []
        self.lines = [] #trimmed lines
        self.fulllines = [] #not trimmed lines
        if folder: #append backslash to make folder + filename valid if folder is given
            folder += "/"
        self.folder = folder
        self.filename = file
        self.errormsg = ""
        self.getLines()
        if file.endswith(".cls"):
            self.isClassFile = True
        else:
            self.isClassFile = False
        self.filename = file
        self.diff = diffobject
        self.changedlines = []

    def analyse(self):
        """
        Runs the source code against all the classes in CodingStandards/
        Stores any warnings returned from the classes in self.warnings
        """
        if self.errormsg:
            self.warnings.append(Warning(self.folder + self.filename, -1, self.errormsg))
        else:
            naming = Naming(self.filename)
            general = General(self.filename)
            statements = Statements(self.filename)
            queries = Queries(self.filename)
            errorHandling = ErrorHandling(self.filename)

            for linenumber, line in enumerate(self.lines):
                fullline = self.fulllines[linenumber]
                naming.newAnalyse(line, fullline, linenumber)
                general.newAnalyse(line, fullline, linenumber)
                statements.newAnalyse(line, fullline, linenumber)
                queries.newAnalyse(line, fullline, linenumber)
                errorHandling.newAnalyse(line, fullline, linenumber)


            self.warnings += naming.warnings
            self.warnings += general.warnings
            self.warnings += statements.warnings
            self.warnings += queries.warnings
            self.warnings += errorHandling.warnings
            # self.warnings += Naming.analyse(Naming(), self.filename, self.lines, self.fulllines)
            # self.warnings += General.analyse(General(self.filename), self.filename, self.lines, self.fulllines)
            # self.warnings += Statements.analyse(Statements(), self.filename, self.lines, self.fulllines)
            # self.warnings += Queries.analyse(Queries(), self.filename, self.lines, self.fulllines)
            # self.warnings += ErrorHandling.analyse(ErrorHandling(), self.filename, self.lines)

    def getLines(self):
        """
        Reads the file from disk and stores the source code in the file object
        self.lines has the sourcecode with trailing and leading whitespace stripped
        self.fulllines includes leading and trailing whitespace
        Comments in Progress sourcecode are replaced by whitespace
        """
        inComment = False
        try:
            file = open(self.folder + self.filename)
            lines = file.readlines()
            file.close()
            self.lines = self.stripComments(lines)
            self.fulllines = self.lines
            self.lines = [line.strip() for line in self.lines]
        except:
            self.errormsg = "Could'nt open file: + " + self.filename

    def stripComments(self, lines):
        """
        Strip Progress comments from code
        :param lines: contains unedited code of Progress file
        :type lines: String[]
        :return: strippedLines, same code but without comments
        :rtype: String[]
        """
        strippedlines = []
        inComment = False
        for line in lines:
            ind1 = line.find("/*")
            ind2 = line.find("*/")
            ind3 = line.find("//")
            if ind1 > -1 and ind2 == -1:
                inComment = True
            if ind1 > -1 and ind2 > -1:
                line = line[:ind1]
            if ind3 > -1:
                line = line[:ind3]
            if not inComment:
                strippedlines.append(line)
            if inComment:
                strippedlines.append(" ")
            if ind1 == -1 and ind2 > -1:
                inComment = False

        return strippedlines

    def getChangedLines(self):
        """
        sets self.changedlines to an array of integers representing linenumbers that have changed.
        Works only for files that are staged for commit, so just before committing.
        If no diff can be obtained, all linenumbers are put in self.changedLines
        """
        if self.diff is None:
            repo = Repo(self.folder)
            files = [item for item in repo.index.diff("HEAD") if item.a_path == self.filename[1:]]
            if not files:
                files = [item for item in repo.index.diff(None) if item.a_path == self.filename[1:]]
            if files:
                self.diff = files[0]
        if self.diff is None:
            self.changedlines = range(len(self.lines))
            return

        if self.diff.b_blob:
            newlines = parseBlobDataStream(self.diff.a_blob)
            oldlines = parseBlobDataStream(self.diff.b_blob)
            diffs = set(newlines).difference(oldlines)
            difflines = self.stripComments(diffs)
            difflines = [line for line in difflines if line.strip()]
            self.changedlines = [i + 1 for (i, line) in enumerate(self.fulllines) if line.replace("\n","") in difflines]
        else:
            self.changedlines = range(len(self.lines)) #if new file (b_blob doesnt exist) put all lines as new line

    def filterWarnings(self):
        """
        only elements in self.warnings are retained if warning.linenumber is an element in self.changedlines.
        Filters out warnings that are not part of changed lines of code.
        """
        self.warnings = [warning for warning in self.warnings if warning.linenumber in self.changedlines]