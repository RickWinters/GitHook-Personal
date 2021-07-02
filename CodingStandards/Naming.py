from FileClasses.Warning import Warning


class Naming:
    """
    Class containing implemented coding standards in the "NAMING" category
    """
    def __init__(self, filename = "none"):
        self.filename = filename
        self.asloc = 0
        self.noundoloc = 0
        self.warnings = []

    def newAnalyse(self, line, fullline, linenumber):
        self.outlineVariableDefinitionsInClassMethods(line, linenumber, self.filename, fullline)


    def analyse(self, filename, lines, fullines):
        """ Runs each line of source code in 'lines' against the implemented coding standards"""
        for linenumber, line in enumerate(lines):
            self.outlineVariableDefinitionsInClassMethods(line, linenumber, filename, fullines)
            pass

        return self.warnings

    def outlineVariableDefinitionsInClassMethods(self, line, linenumber, filename, fullline):
        """
        For each block of code where a method, catch, procedure or function is defined
        checks the code if any 'define variable [varname] as [type]' is outlined the " as ".
        If a line of code with 'define variable' is not outlined the same as the first define variable in the current
        block than a warning is returned.
        """
        if line.lower().startswith("method")\
                or line.lower().startswith("catch")\
                or line.lower().startswith("procedure")\
                or line.lower().startswith("function"):
            self.asloc = 0
            self.noundoloc = 0

        if line.lower().startswith("define variable"):
            if self.asloc == 0 and self.noundoloc == 0:
                self.asloc = fullline.find(" as ")
                self.noundoloc = fullline.find(" no-undo")
            else:
                asloc = fullline.find(" as ")
                noundoloc = fullline.find(" no-undo")
                if not (asloc == self.asloc and noundoloc == self.noundoloc):
                    self.warnings.append(
                            Warning(
                                filename,
                                linenumber,
                                "NAMING: Define variable line not outlined correctly"))
