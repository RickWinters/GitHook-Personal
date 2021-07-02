class Warning:
    def __init__(self, filename, linenumber, message):
        self.filename = filename
        self.linenumber = linenumber + 1
        self.message = message

    def __str__(self):
        return self.filename + ":" + str(self.linenumber) + " --> " + self.message

    def __lt__(self, other):
        return self.linenumber < other.linenumber