import sys
import os
import re
import mimetypes

import constants

def main():
    infile = sys.argv[1]

    if validate_input(infile) != 0:
        print("Input file validation failed, see error message")
        return

    # TODO: divide input file into chunks

    # TODO: delegate processing of chunks

    # TODO: Aggregate results

    return

# Validate user input. See README for input file requirements
def validate_input(infile) -> int:
    # Check MIME type
    if mimetypes.guess_type(infile)[0] != "text/csv":
        print("Given file is not a csv. Please upload a csv file")
        return -1

    incsv = open(infile, "rt", encoding="utf-8")

    # Empty is defined as filesize 0
    if os.stat(infile).st_size == 0:
        print("input file is empty")
        return -1

    # case input file is not csv
        # definition of csv is arbitrary, will just define a collection of
        #  comma delimited strings. If can't be split by ',', reject file
    index = 0
    entries = []
    header_length = 0                   # used to check if entries match header
    header_entry_mismatch = False
    mismatch_indexes = []
    for line in incsv:
        line = line.strip()
        line_length = len(line.split(","))
        if line_length == 1:
            print("not csv")
            return -1
        if index == 0:
            header = line
            header_length = line_length
        else:
            entries.append(line)

        index += 1
        if line_length != header_length:
            header_entry_mismatch = True
            mismatch_indexes.append(index)  # Note: file lines are 1-indexed

    # TODO: case no header line/file only consisting of entries without header
        # might have to ask user for hint if header is given or not
        # current implementation ignores first line

    # case no entries
    if len(entries) == 0:
        print("no entries given")
        return -1

    # case max number of entries
    if index > constants.MAX_NUM_ENTRIES:
        print(f"too many entries (limit {constants.MAX_NUM_ENTRIES})")
        return -1

    # case header length != entry length
    if header_entry_mismatch:
        print(f"header-entry length mismatch at lines {mismatch_indexes}")
        return -1

    # enforce maximum number of input diagnoses, +1 column for the id
    if header_length > constants.MAX_NUM_DX + 1:
        print(f"too many diagnoses (limit {constants.MAX_NUM_DX})")
        return -1

    # Case patient ID is not the first column
        # TODO: can write function to re-order?
    # Case invalid patient ID (null/empty/length too long)
    # Case invalid diagnosis (ie. does not match ICD format)

    # Algorithm:
        # ICD-10-CM has defined structure
        # Regex for valid ICD-10-CM codes validates codes
        # Patient ID may/may not match the ICD-10-CM regex
        # Scan per entry for regex mismatches
            # allow 1 mismatch per line, note index of mismatch
                # assume index of mismatch is index of patient id
            # ensure mismatch always occurs at the same index

    # TODO: are codes starting with "U" really invalid?
    # TODO: codes in database do not have any ".", maybe should reject input
    #  codes that include the "."? Or could scrub out the "." at some point
    #  downstream
    # icd_code_re = re.compile(r'([a-t]|[v-z])[a-z0-9]{2}\.?[a-z0-9]{0,4}$' , re.I | re.A)
    icd_code_re = re.compile(r'([a-z])[a-z0-9]{2}\.?[a-z0-9]{0,4}$' , re.I | re.A)

    id_index = 0
    line_counter = 1
    invalid_entries = []
    invalid_ids = []
    found_id = False        # variable so that the id does not get reassigned multiple times in 1 row
    for entry in entries:
        entry_index = 0
        line_counter += 1
        entry_list = entry.split(",")
        for item in entry_list:
            if (re.match(icd_code_re, item) is None):
                # assume we found the patient id, if the id_index is 0, else
                #  we have already found an id and we now have an invalid icd
                #  code
                if id_index == 0 and line_counter == 2 and not found_id and item != "":
                    # only define id_index on the first line
                    id_index = entry_index
                    found_id = True
                    if len(item) == 0 or len(item) > constants.MAX_ID_LEN:
                        invalid_ids.append(line_counter)
                elif id_index == entry_index and found_id:
                    if len(item) == 0 or len(item) > constants.MAX_ID_LEN:
                        invalid_ids.append(line_counter)
                    pass
                elif item == "":
                    pass
                else:
                    invalid_entries.append(line_counter)
                    break
            entry_index += 1
        # case id matches code regex - assume id is at index 0
        if line_counter == 2 and not found_id:
            if len(entry_list[0]) == 0 or len(entry_list[0]) > constants.MAX_ID_LEN:
                invalid_ids.append(line_counter)
            found_id = True

    if id_index != 0:
        print("patient ID is not the first item in the list")
        print(f"patient id is at index {id_index}")
        return -1

    if len(invalid_ids) != 0:
        print(f"invalid id's present at lines {invalid_ids}")
        print(f"id cannot be empty, and id must be less than or equal to {constants.MAX_ID_LEN} characters long")
        return -1

    if len(invalid_entries) != 0:
        print(f"invalid codes at lines {invalid_entries}")
        return -1

    print(f"file has {index} lines")
    print("passed input validation")

    return 0


if __name__ == "__main__":
    main()
