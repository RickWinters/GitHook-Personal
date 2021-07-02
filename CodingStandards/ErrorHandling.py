from FileClasses.Warning import Warning
from FileClasses.Variable import *

class ErrorHandling:
    """
    Class containing implemente coding standards in the "ErrorHandling" category
    """

    def __init__(self, filename = "none"):
        self.warnings = []
        self.filename = filename

    def newAnalyse(self, line, fullline, linenumber):
        self.useBlockLevelOnErrorUndoThrow(line, linenumber, self.filename)

    def analyse(self, filename, lines):
        for linenumber, line in enumerate(lines):
            self.useBlockLevelOnErrorUndoThrow(line, linenumber, filename)
            pass

        return self.warnings

    def useBlockLevelOnErrorUndoThrow(self, line, linenumber, filename):
        """
        Returns a warning when 'routine-level on error undo, throw.' is used
        instead of 'block-level on error undo, throw.'
        """
        if line.lower() == "routine-level on error undo, throw.":
            self.warnings.append(
                Warning(
                    filename,
                    linenumber,
                    "ERRORHANDLING: User 'block-level on error undo, throw.'"))