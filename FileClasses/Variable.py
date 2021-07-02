class Variable:
    def __init__(self, name, type, linenumber):
        self.name = name
        self.type = type
        self.linenumber = linenumber

def extractVar(line, linenumber):
    if line.startswith("define variable"):
        vartype = ""
        varname = ""
        asind = line.find(" as ")
        spaceind = line.find(" ", asind + 4)
        if spaceind > -1:
            vartype = line[asind + 4:spaceind]
        else:
            vartype = line[asind:]
        varname = line[15:asind].strip()
        return Variable(varname, vartype, linenumber)

def extractBuffer(line, linenumber):
    if line.startswith("define buffer"):
        vartype = "buffer"
        spaceind = line.find(" ", 14)
        varname = line[14:spaceind]
        return Variable(varname, vartype, linenumber)