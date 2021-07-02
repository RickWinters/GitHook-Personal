def countCharInString(char, string):
    """
    :param char: single character to check
    :type char: Char
    :param string: String of text to count char
    :type string: String
    :return: amount of times char exists in string
    :rtype: Integer
    """
    amount = 0
    for letter in string:
        if char == letter:
            amount += 1
    return amount

def checkInLine(words, string):
    """
    :param words: List of words to check if any of those is in the string given
    :type words: String[]
    :param string: Single string to check list of words against
    :type string: String
    :return: True of one of the words is in string
    :rtype: Boolean
    """
    for word in words:
        if word in string:
            return True
    else:
        return False


def indexOfFirstMatch(words, string, start = 0):
    """
    :param words: list of words to check in string.
    :type words: String[]
    :param string: String to check against.
    :type string: String
    :param start: index to start searching
    :type start: INTEGER
    :return: Index first found word in string, word that matched
    :rtype: Integer, String
    """
    for word in words:
        if word in string:
            return string.find(word, start), word
    else:
        return -1, ""

def indexInString(ind, line, start = False):
    """
    simple check to see if a certain index of a line is within a string,
    assuming that lines starts out of string and each " changes in or out of string
    :param ind: index of line to check
    :type ind: INTEGER
    :param line: line to check
    :type line: STRING
    :param start: to start counting with True or False, optional, default = false
    :type start: BOOL
    :return: inString
    :rtype: BOOL
    """
    inString = start
    for i, char in enumerate(line):
        if char == "\"" or char == "'":
            inString = not inString
        if i == ind:
            break
    return inString

def indexInCanFind(ind, line):
    """
    simple check to see if the index of the line give is within a can-find( statement
    :param ind: index of line to check
    :type ind: INTEGER
    :param line: line to check
    :type line: STRING
    :return:
    :rtype: BOOL
    """
    canfindstartind = line.find("can-find(")
    if canfindstartind == -1:
        canfindstartind = line.find("can-find (")
    canfindendind = line.find(")", canfindstartind)
    if ((canfindendind == -1 and ind > canfindstartind > -1) or
            (canfindstartind < ind < canfindendind)):
        return True
    else:
        return False

def bracketLevelAtIndex(string, index = -1, currentLevel = 0):
    if index > -1:
        string = string[:index]
    localLevel = countCharInString("(", string)
    localLevel -= countCharInString(")", string)
    return localLevel + currentLevel


def parseBlobDataStream(blob):
    """
    Parses a diff.blob binary data to an array of lines split by "\n"
    :param blob: blob
    :type blob: Repo.Diff.Blob
    :return: lines
    :rtype: String[]
    """
    binarydata = ""
    try:
        binarydata = blob.data_stream.read().decode('utf-8')
    except:
        pass
    lines = binarydata.split("\n")

    return lines