from FileClasses.Warning import Warning
from FileClasses.Variable import *
from FileClasses.HelperFunctions import *
from CodingStandards.CommonLists import *

class Queries:
    """
    Class containing implemented coding standards in the "QUERIES" category
    """
    def __init__(self, filename = "none"):
        self.filename = filename
        self.warnings = []
        self.canfindbuffers = []
        self.whereind = 0
        self.breakbyind = 0
        self.queryoperatorind = 0
        self.queryoperatormatch = ""
        self.checkforeachoutline = False
        self.haswherestatement = False
        self.includeinforeach = 0
        self.querystartlinenumber = 0
        self.querywherelinenumber = 0
        self.querystartind = 0
        self.querystartmatch = ""

        #check lock-statements in queries
        self.doCheckLockStatement = False
        self.lockStatementFound = False
        self.lockStatementQueryStartMatch = ""


    def newAnalyse(self, line, fullline, linenumber):
        currentbuffer = extractBuffer(line, linenumber)
        if currentbuffer:
            self.canfindbuffers.append(currentbuffer)
        self.lockStatementAtQueries(line, linenumber, self.filename)
        self.doNotUseUseIndex(line, linenumber, self.filename)
        self.forEachKeyWordOutlining(line, linenumber, self.filename, fullline)


    def analyse(self, filename, lines, fulllines):
        """ Runs each line of source code in 'lines' against the implemented coding standards"""
        for linenumber, line in enumerate(lines):
            currentbuffer = extractBuffer(line, linenumber)
            if currentbuffer:
                self.canfindbuffers.append(currentbuffer)
            # self.lockStatementAtQueries(line, linenumber, filename, lines)
            self.doNotUseUseIndex(line, linenumber, filename)
            self.forEachKeyWordOutlining(line, linenumber, filename, fulllines)
            pass

        return self.warnings

    def lockStatementAtQueries(self, line, linenumber, filename):
        """
        For each query that starts with 'for each' or 'for first' on a table in the Cura database, or a buffer thereof,
        a warning will be returned when a 'no-lock' or 'exclusive-lock' is missing.
        Kennys database tables to be added in this check.
        """
        #check start of query
        if (checkInLine(queryStarts, line)):
            ind, self.lockStatementQueryStartMatch = indexOfFirstMatch(queryStarts, line)
            if (indexInString(ind, line) or
                    indexInCanFind(ind, line)):
                return
            startind = ind + len(self.lockStatementQueryStartMatch)
            spaceind = line.find(" ", startind)
            if spaceind > -1:
                tablename = line[startind:spaceind].replace("b-","")
            else:
                tablename = line[startind:].replace("b-","")
            if not tablename in tablelist:
                return
            self.doCheckLockStatement = True

        if self.doCheckLockStatement:
            if "-lock" in line:
                self.lockStatementFound = True
            if (line.endswith(":") or
                line.endswith(",")):
                if not self.lockStatementFound:
                    self.warnings.append(
                        Warning(
                            filename,
                            linenumber,
                            "QUERIES: 'no-lock' or 'exclusive-lock' statement missing in query \"" + self.lockStatementQueryStartMatch + "\" on db table"))
                self.doCheckLockStatement = False
                self.lockStatementFound = False

    def doNotUseUseIndex(self, line, linenumber, filename):
        """ Any line of source code containing 'use-index' returns a warning"""
        if "use-index" in line.lower():
            self.warnings.append(
                Warning(
                    filename,
                    linenumber,
                    "QUERIES: do not use \"use-index\""))

    def forEachKeyWordOutlining(self, line, linenumber, filename, fullline):
        """
        Checks outlining of keywords in a for each / for first statement.
        Ignorese any includes that are in a for each / for first statement:
        - 'where' --> if there is one, must be on same line of 'for each'
        - ' = ' must be right-outlined with first ' = ' in for each statement (or other binary operater)
            for each table where table.field   =| value
                             and table.field2 |=| value2    --> correct
                             and table.field3 >=| value3    --> wrong
                             and table.field4  >= value4    --> wrong
                             and table.fieldfive = value3 --> wrong
        - 'and' --> right-outlined of 'where' keyword on new line:
            for each table where| table.field  = value
                             and| table.field2 = value2 --> correct
                and| table.field3               = value3 --> wrong
        - 'or' --> right-outlined of 'where' keyword on new line:
        - 'no-lock' --> left-outlined of 'where' keyword on new line for queries starting with 'for'
                    --> left-outlined + 2 spaces of 'find' for queries starting with 'find':
            for [each / first] table |where table.field  = value
                                     |  and table.field2 = value2
                                     |no-lock.
            |find [first, last] table where table.field  = value
            |                           and table.field2 = value2
            |__no-lock
        - 'exclusive-lock' --> left-outlined of 'where' keyword on new line for queries starting with 'for'
                           --> left-outlined + 2 spaces of 'find' for queries starting with 'find'
        - 'break by' --> 1 tab (2 spaces) away from 'for each'
            |for each table where table.field  = value
            |                 and table.field2 = value2
            |               no-lock
            |**break by table.field2
        - 'by' --> if 'break by' is used earlier than outlined on 'by' of 'break by'
                   else 1 tab (2 spaces away from 'for each'
            for each table where table.field  = value
                             and table.field2 = value2
                           no-lock
              break |by table.field
                    |by table.field2 --> correct
              by table.anotherfield --> wrong

            |for each table where table.field  = value
            |                 and table.field2 = value2
            |               no-lock
            |**by table.field2 --> correct
               by table.field
        - 'on error' --> 1 tab (2 spaces) away from 'for each'
            |for each table where table.field  = value
            |               no-lock
            |**on error undo, throw:
        """
        #exclude comments
        self.includeinforeach += countCharInString("{", line)
        if self.includeinforeach > 0:
            self.includeinforeach -= countCharInString("}", line)
            return
        # start query tracking
        if checkInLine(queryStarts, fullline):
            ind, match = indexOfFirstMatch(queryStarts, fullline)
            if (indexInString(ind, fullline) or
                    indexInCanFind(ind, fullline)):
                return
            self.checkforeachoutline = True
            self.querystartind = ind
            self.querystartlinenumber = linenumber
            self.querystartmatch = match

        #set whereind and check on same line as querystart keyword
        if (" where " in fullline
                and self.checkforeachoutline):
            self.whereind = fullline.find(" where ")
            self.querywherelinenumber = linenumber
            self.haswherestatement = True
            if not linenumber == self.querystartlinenumber:
                self.warnings.append(
                    Warning(
                        filename,
                        linenumber,
                        "QUERIES: 'where' keyword not on same line as \"" + self.querystartmatch + "\" keyword on line " + str(self.querystartlinenumber + 1)))

        #set operator ind and match
        if (self.queryoperatorind == 0
                and checkInLine(operatorList, fullline)
                and self.checkforeachoutline):
            isind, match = indexOfFirstMatch(operatorList, fullline, self.querystartind)
            self.queryoperatorind = isind
            self.queryoperatormatch = match

        #check current operator ind with first operator ind
        if (checkInLine(operatorList, line)
                and self.checkforeachoutline):
            ind, match = indexOfFirstMatch(operatorList, fullline, self.querystartind)
            length = len(match)
            diff = length - len(self.queryoperatormatch)
            if not self.queryoperatorind == ind + diff:
                self.warnings.append(
                    Warning(
                        filename,
                        linenumber,
                        "QUERIES: '" + match + "' not outlined correctly with first '" + self.queryoperatormatch +
                        "' in '" + self.querystartmatch + "' statement on line " + str(self.querystartlinenumber + 1)))
        #check outline of AND
        if (" and " in fullline
                and self.checkforeachoutline):
            ind = fullline.find(" and ")
            if not (self.whereind + 2) == ind:
                self.warnings.append(
                    Warning(
                        filename,
                        linenumber,
                        "QUERIES: 'and' keyword not right-outlined with 'where' keyword on line "
                        + str(self.querywherelinenumber + 1)))
        #check outline of OR
        if (" or " in fullline
                and self.checkforeachoutline):
            ind = fullline.find(" or ")
            if not (self.whereind + 3) == ind:
                self.warnings.append(
                    Warning(
                        filename,
                        linenumber,
                        "QUERIES: 'or' keyword not right-outlined with 'where' keyword on line "
                        + str(self.querywherelinenumber + 1)))
        #check outline of 'no-lock'
        if ((" no-lock" in fullline or
             " exclusive-lock" in fullline)
                and self.checkforeachoutline
                and self.haswherestatement):
            nolockind = fullline.find(" no-lock")
            exlockind = fullline.find(" exclusive-lock")
            matchind = 0
            if nolockind > -1:
                matchind = nolockind
            elif exlockind > -1:
                matchind = exlockind
            if self.querystartmatch.strip().startswith("find"):
                if not matchind == self.querystartind + 2:
                    match = "*-lock"
                    if nolockind > -1:
                        match = "no-lock"
                    elif exlockind > -1:
                        match = "exclusive-lock"
                    self.warnings.append(
                        Warning(
                            filename,
                            linenumber,
                            "QUERIES: '" + match + "' not 2 spaces outlined with '" + self.querystartmatch.strip() +
                                "' on line " + str(self.querystartlinenumber)
                        )
                    )
            elif self.querystartmatch.strip().startswith("for"):
                if not matchind == self.whereind:
                    match = "*-lock"
                    if nolockind > -1:
                        match = "no-lock"
                    elif exlockind > -1:
                        match = "exclusive-lock"
                    self.warnings.append(
                        Warning(
                            filename,
                            linenumber,
                            "QUERIES: '" + match + "' not left-outlined with 'where' keyword on line " +
                                str(self.querystartlinenumber)
                        )
                    )

        #check outline of 'break by
        if (" break by " in fullline
                and self.checkforeachoutline):
            ind = fullline.find( " break by ")
            self.breakbyind = ind
            if not (self.querystartind + 2) == ind:
                self.warnings.append(
                    Warning(
                        filename,
                        linenumber,
                        "QUERIES: 'break by' not 1 tab outlined with '" + self.querystartmatch +
                        "' on line " + str(self.querystartlinenumber)))
        #check outline of 'by'
        if (" by " in fullline
                and self.checkforeachoutline):
            ind = fullline.find(" by ")
            if self.breakbyind > 0:
                if not (self.breakbyind + 6) == ind:
                    self.warnings.append(
                        Warning(
                            filename,
                            linenumber,
                            "QUERIES: 'by' keyword not correctly outlined with 'by' from earlier 'break by' on new line"))
            else:
                if not (self.querystartind + 2) == ind:
                    self.warnings.append(
                        Warning(
                            filename,
                            linenumber,
                            "QUERIES: 'by' keyword not 1 tab outlined with '" + self.querystartmatch
                            + "' keyword on new line"))
        #check outline of 'on error'
        if (" on error " in fullline
                and self.checkforeachoutline):
            ind = fullline.find(" on error ")
            if not (self.querystartind + 2) == ind:
                self.warnings.append(
                    Warning(
                        filename,
                        linenumber,
                        "QUERIES: 'on error' not 1 tab outlined with '" + self.querystartmatch + "' keyword on new line"))
        #reset query tracking
        if ((line.endswith(":") or line.endswith("."))
                and self.checkforeachoutline):
            self.queryoperatorind = 0
            self.queryoperatormatch = ""
            self.querystartind = 0
            self.querystartmatch = ""
            self.whereind = 0
            self.breakbyind = 0
            self.querywherelinenumber = 0
            self.checkforeachoutline = False
            self.haswherestatement = False

        if line.endswith(","):
            self.queryoperatorind = 0
            self.queryoperatormatch = ""
            self.whereind = 0
            self.querywherelinenumber = 0
            self.haswherestatement = False

