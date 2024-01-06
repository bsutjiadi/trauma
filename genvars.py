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

    incsv = open(sys.argv[1], "r")
    # header, ptrows = compare(thedict, incsv)
    header, ptrows = compare_parallel(thedict, incsv)
    incsv.close()

    print(type(header))
    print(ptrows)

    # write_table_csv(header, ptrows)
    return


def compare_serial(dictionary, infile):
    rows = infile.readlines()[1:]

    header = ["inc_key", "mortality"]
    ptrows = []
    tmpcounter = 0

    for row in rows:
        brokeoutearly = False
        row = row.strip()
        array = row.split(",")

        tmparray = [0] * 1497
        tmparray[0] = int(array[0])
        tmparray[1] = int(array[-1])

        for diagnosis in array[1:]:
            # index starts at 2 because first two columns are already filled
            index = 2

            for key in dictionary:
                # only add to the header line on the first iteration through
                # the dictionary
                if tmpcounter == 0:
                    header.append(key)

                if diagnosis in dictionary[key]:
                    tmparray[index] = tmparray[index] + 1

                index += 1

            tmpcounter += 1

            # break out of the loop early to prevent unnecessary comparisons
            if diagnosis == '':
                ptrows.append(tmparray)
                brokeoutearly = True
                break

        if not brokeoutearly:
            ptrows.append(tmparray)

    return (header, ptrows)


def compare_parallel(dictionary, infile):
    rows = infile.readlines()[1:]
    ptrows = []

    # Generate header line
    header = ["inc_key", "mortality"]
    for key in dictionary:
        header.append(key)

    global globaldict
    globaldict = dictionary

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

    tmparray = [0] * 1497
    tmparray[0] = int(array[0])
    tmparray[1] = int(array[-1])

    for diagnosis in array[1:]:
        # index starts at 2 because first two columns are already filled
        index = 2

        for key in globaldict:
            if diagnosis in globaldict[key]:
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

    of = open("/src/injury_variables_only.csv", "w")
    csv.writer(of, delimiter=',', lineterminator='\n').writerows(megaarray)
    of.close()

    return


if __name__ == "__main__":
    main()
