# The code in this file generates the injury variables only table
# This code will take in 1 argument from the command line:
#   the first argument is the input file, which is expected to be a .csv
#   containing patient identifiers and injury (ICD) codes
# This code will output a file called injury_variables_only.csv

# Input file can either include or omit mortality variable. If training a new
# model, mortality variable must be included. Otherwise, mortality variable can
# be omitted.
import csv
import json
import sys
from multiprocessing import Pool


def main():
    dictfile = open("variable_codes.json", "r")
    thedict = json.load(dictfile)
    dictfile.close()

    incsv = open(sys.argv[1], "r")
    # header, ptrows = compare_serial(thedict, incsv)
    header, ptrows = compare_parallel(thedict, incsv)
    incsv.close()

    write_table_csv(header, ptrows)
    return


def compare_serial(dictionary, infile):
    global NUM_INJURY_VAR
    NUM_INJURY_VAR = len(dictionary)

    is_mortality_var_present(infile)

    rows = infile.readlines()
    ptrows = []

    # generate header line
    header = ["inc_key"]
    if MORTALITY_VAR_PRESENT:
        header.append("mortality")
    for key in dictionary:
        header.append(key)

    # create global variable for access within dictionary_lookup()
    global GLOBALDICT
    GLOBALDICT = dictionary

    for row in rows:
        ptrows.append(dictionary_lookup(row)[0])

    return (header, ptrows)


def compare_parallel(dictionary, infile):
    global NUM_INJURY_VAR
    NUM_INJURY_VAR = len(dictionary)

    is_mortality_var_present(infile)

    rows = infile.readlines()
    ptrows = []

    # Generate header line
    header = ["inc_key"]
    if MORTALITY_VAR_PRESENT:
        header.append("mortality")
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
    index = 0

    brokeoutearly = False
    row = row.strip()
    array = row.split(",")

    # Initialize template array. Length is number of variables +2 for patient
    # ID and mortality variables. If statement to account for possibly omitted
    # mortality variable.
    if MORTALITY_VAR_PRESENT:
        # Assumptions: patient ID is first item in list, mortality variable is
        # the last element in the list
        tmparray = [0] * (NUM_INJURY_VAR + 2)
        tmparray[0] = array[0]
        tmparray[1] = int(array[-1])
        index = 2
    else:
        tmparray = [0] * (NUM_INJURY_VAR + 1)
        tmparray[0] = array[0]
        index = 1

    # Start at index 1 because it is assumed patient ID is the first item
    for diagnosis in array[1:]:
        tmpindex = index
        for key in GLOBALDICT:
            if diagnosis in GLOBALDICT[key]:
                tmparray[tmpindex] = tmparray[tmpindex] + 1

            tmpindex += 1

        # break out of the loop early to prevent unnecessary comparisons
        if diagnosis == '':
            ptrows.append(tmparray)
            brokeoutearly = True
            break

    if not brokeoutearly:
        ptrows.append(tmparray)

    return ptrows


def is_mortality_var_present(infile):
    global MORTALITY_VAR_PRESENT

    inputheader = infile.readline()
    MORTALITY_VAR_PRESENT = 'mortality' in inputheader

    return


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
