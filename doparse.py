import re
import unidecode
import json
import sys


def main():
    infile = open(sys.argv[1], "r")
    thedict = gen_dict(infile)
    infile.close()

    # Dump the dictionary to a json file
    dictfile = open("variable_codes.json", "w")
    json.dump(thedict, dictfile)
    dictfile.close()

    return


# Function to parse the stata .do file
# Creates a dictionary of variable names as keys and an array of ICD codes as
# the value
def gen_dict(fname):
    infile = open(fname, "r")

    array = []
    var = ""
    thedict = {}

    for line in infile:
        line = line.strip()

        if "gen " in line:
            var = (line.lstrip("gen ")).rstrip(" = 0 ")

        if "replace" in line:
            line = re.sub(r'^.*?\(', '(', line)
            line = re.sub(r'^.*?substr.*?\)', '(', line)
            line = line.lstrip("(").rstrip(")")
            line = line.replace("\"", "")
            unicodearray = line.split(",")
            prearray = []
            for item in unicodearray:
                item = unidecode.unidecode(item)
                item = item.strip()
                prearray.append(item)
            prearray = prearray[1:]
            array = array + prearray

        if "}" in line:
            if thedict.get(var) is not None:
                thedict[var] = thedict[var] + array
            else:
                thedict[var] = array

            var = ""
            array = []

    infile.close()

    return thedict


if __name__ == "__main__":
    main()
