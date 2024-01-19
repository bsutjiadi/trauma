# The code in this file generates the injury vairables only table
# This code will take in 1 argument from the command line:
#   the first argument is the input file, which is expected to be a .csv
#   containing patient identifiers and injury (ICD) codes
# This code will output a file called injury_variables_only.csv
import csv
import json
import sys
from multiprocessing import Pool


def main():
    dictfile = open("variable_codes.json", "r")
    thedict = json.load(dictfile)
    dictfile.close()

    global NUM_INJURY_VAR
    NUM_INJURY_VAR = len(thedict)

    incsv = open(sys.argv[1], "r")
    # header, ptrows = compare_serial(thedict, incsv)
    header, ptrows = compare_parallel(thedict, incsv)
    incsv.close()

    write_table_csv(header, ptrows)
    return


def compare_serial(dictionary, infile):
    rows = infile.readlines()[1:]
    ptrows = []

    # generate header line
    header = ["inc_key", "mortality"]
    for key in dictionary:
        header.append(key)

    # create global variable for access within dictionary_lookup()
    global GLOBALDICT
    GLOBALDICT = dictionary

    for row in rows:
        ptrows.append(dictionary_lookup(row)[0])

    return (header, ptrows)


def compare_parallel(dictionary, infile):
    rows = infile.readlines()[1:]
    ptrows = []

    # Generate header line
    header = ["inc_key", "mortality"]
    for key in dictionary:
        header.append(key)

    # create global variable for access within dictionary_lookup()
    global GLOBALDICT
    GLOBALDICT = dictionary

    with Pool() as pool:
        result = pool.map(dictionary_lookup, rows)

    for thing in result:
        ptrows.append(thing[0])

    return header, ptrows


def dictionary_lookup(row):
    ptrows = []

    brokeoutearly = False
    row = row.strip()
    array = row.split(",")

    # Initialize template array. Length is number of variables +2 for patient
    # ID and mortality variables
    tmparray = [0] * (NUM_INJURY_VAR + 2)
    tmparray[0] = int(array[0])     # patient identifier
    tmparray[1] = int(array[-1])    # mortality variable

    for diagnosis in array[1:]:
        # index starts at 2 because first two columns are already filled with
        # patient ID code and mortality
        index = 2

        for key in GLOBALDICT:
            if diagnosis in GLOBALDICT[key]:
                tmparray[index] = tmparray[index] + 1

            index += 1

        # break out of the loop early to prevent unnecessary comparisons
        if diagnosis == '':
            ptrows.append(tmparray)
            brokeoutearly = True
            break

    if not brokeoutearly:
        ptrows.append(tmparray)

    return ptrows


def write_table_csv(header, ptrows):
    megaarray = []
    megaarray.append(header)
    for row in ptrows:
        megaarray.append(row)

    of = open("injury_variables_only.csv", "w")
    csv.writer(of, delimiter=',', lineterminator='\n').writerows(megaarray)
    of.close()

    return


if __name__ == "__main__":
    main()
