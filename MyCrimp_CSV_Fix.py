# #########################################################################
# MyCrimp_CrimpSpecCSV_Fix: Python script make specific changes to CSV files
#
# Scott Thompson 11/12/14 : Updated to a single format for all crimp specs
#               Added split function to break up output into multiple files
#
# #########################################################################
import os
import csv
import datetime
import sys

# #########################################################################
# Define Constants and global variables
# #########################################################################
cross_ref_template = 'S:\MyCrimp\MyC_Customers\CSV_Templates\cross_ref_template.csv'
cspec_template = 'S:\MyCrimp\MyC_Customers\CSV_Templates\specification_template.csv'
location_template = 'S:\MyCrimp\MyC_Customers\CSV_Templates\location_template.csv'
fields = []
now = datetime.datetime.now()
count_updated = 0
repeat = True
DEEPDEBUG = False
DEBUG = False
ADD_INCH = False
INCH_CHAR = '\"'
split_file = False
split_cnt = 2500
split_cntinc = 2500
split_num = 1

# Setup common unicode subsitutions
from MyCrimp_ASCII_Subs import repls

# inch_repls = {'"':'', '-':' '}      # OLD - Inch Measurement Fixes  -
# still needed by Veyance 1.0
inch_repls = {'-': ' ', '" ': '"'}              # Inch Measurement Fixes
# #########################################################################
# Setup options directories for input files
# #########################################################################
from MyCrimp_Customers import DataDirs

# #########################################################################
# define Classes
# #########################################################################


class CSV_Field:
    def __init__(self, name, required, size, fieldtype, field_values=[], nozero=False, standinch=False, textfield=False, measurement=False, addinchchar=False):
        self.name = name
        self.required = required
        self.size = size
        self.fieldtype = fieldtype
        self.field_values = field_values
        self.nozero = nozero
        self.standinch = standinch
        self.measurement = measurement
        self.textfield = textfield
        self.addinchchar = addinchchar

    def name(self):
        return self.name

    def reqfieldmissing(self, testfield):
        return len(testfield) == 0 and self.required

    def isrequired(self):
        return self.required

    def checksize(self, fieldlength):
        return fieldlength > self.size

    def isstandinch(self):
        return self.standinch

    def isnozero(self):
        return self.nozero

    def ismeasurement(self):
        return self.measurement

    def istextfield(self):
        return self.textfield

    def isaddinchchar(self):
        return self.addinchchar

    def setaddinchchar(self, add):
        if add:
            self.addinchchar = True
        else:
            self.addinchchar = False

# #########################################################################
# define my functions
# ###################################################

# ###################################################
# Function: Cleanchar: function to replace characters
# ###################################################


def CleanChar(text, fixes):
    for i, j in fixes.items():
        text = text.replace(i, j)
    return text
# ###################################################
# Function: CleanUpTrailingSpace: function to remove trailing spaces from entries.
# ###################################################


def CleanUpTrailingSpace(text):
    return text.rstrip()
# ###################################################
# End Functions
# ###################################################

# #################################################################################################
# #################################################################################################
# Main Program
# #################################################################################################
# #################################################################################################
while repeat:
    # ##########################################################################
    # Get template header names
    # #########################################################################
    # Determine the type of CSV file to check
    print("Check which type of CSV input file for MyCrimp?")
    i = 0
    choice = 1000
    for csvtype in ['Crimp Spec', 'Locations', 'Cross Refs']:
        print("\t", csvtype, "-->\t", i)
        i += 1

    while choice > len(csvtype):
        choice = int(input("File type to check? "))

    if choice == 0:
        template = cspec_template
        csv_type = 'Crimp Specifications'
        from MyCrimp_CSpec_Fields import required_fields, field_lengths, text_fields, measurement_fields, standinch_fields, nozero_fields
    elif choice == 1:
        template = location_template
        csv_type = 'Locations'
        from MyCrimp_Loc_Fields import required_fields, field_lengths, measurement_fields, standinch_fields, nozero_fields
    elif choice == 2:
        template = cross_ref_template
        csv_type = 'Cross References'
        from MyCrimp_cRef_Fields import required_fields, field_lengths, measurement_fields, standinch_fields, nozero_fields
    else:
        print("Error: Invalid template number:", choice)

    # Now process the the template and field information for this type of CSV
    tfile = open(template, 'r')
    firstline = tfile.readline()   # Read 1st line (the line with the headers
    fields = firstline.split(',')
    print("\nProcessing template file: ", template)
    tfile.close()

    Template_Fields = len(fields)
    print("\n\n------------------------------------------------------------------------")
    print("Checking ", csv_type, "files. ", str(Template_Fields),
          "fields per record. Which file do you want to check?")
    print("------------------------------------------------------------------------")
    # Setup class for each field 
    csv_fields = []
    i = 0
    # Clean up headers by removing leading/trailing white space
    for field in fields:
        field = field.lstrip()
        field = field.rstrip()
        if DEBUG:
            print("Working with", field, "input field: ", i)
        # Setup Class for each field
        csv_fields.append(CSV_Field(field, required_fields[i], field_lengths[i], "text", "", nozero_fields[
                          i], standinch_fields[i], text_fields[i], measurement_fields[i]))
        i += 1
    # #########################################################################
    # Determine which Directory to work from
    # #########################################################################
    cnt = 0
    choice = 1000  # Default
    print('\nWhich Directory do you want to work from?\n')
    for dir in DataDirs:
        dir = dir[25:]
        print('\tOption', cnt, ':', dir, '?')
        cnt += 1
    print('\tOption', cnt, ' quit')

    while choice >= cnt:
        choice = int(input('\nWhat Option #:'))
        if (choice == cnt):
            sys.exit()
    print('\nWorking from:', DataDirs[choice])

    os.chdir(DataDirs[choice])

    # #########################################################################
    # Now determine which file to process
    # #########################################################################
    files = []
    linedata = []
    cnt = 0
    choice = 1000
    print('\nWhich file do you want to process?\n')
    # Display possible CSV files in this directory to process
    for file in os.listdir('.'):
        if (file.endswith(".csv") and not file.startswith("Fixed")):
            print('\tFile', cnt, ': -', file)
            files.append(file)
            cnt += 1
    print('\tOption', cnt, ' quit')

    while choice >= cnt:
        choice = int(input('What Option #:'))
        if (choice == cnt):
            sys.exit()
    print('\nWorking on file:', files[choice])

    # #########################################################################
    # Determine Revision Date
    # #########################################################################
    if csv_type == 'Crimp Specifications':
        RevDate = ""
        d1choice = input("\nUpdate Revision Data in input file? (y/n):")
        if (d1choice == "y"):
            dchoice = input(
                "\tUse an alternate Revision Date? (Instead of current date/time) (y/n):")
            if (dchoice == "y"):
                RevDate = input(
                    "\tEnter Revision Date to use (YYYY-MM-DD HH:MM): ")
            else:
                RevDate = now.strftime("%Y-%m-%d %H:%M")
            print("Using Review Date: ", RevDate)

    # #########################################################################
    # Add inch char to end if missing?
    # #########################################################################
    if csv_type == 'Crimp Specifications':
        dchoice = input(
            "\nDo you want to add double quote to the end of inch measurements (y/n):")
        if (dchoice == "y"):
            ADD_INCH = True
            for field in csv_fields:
                if field.isstandinch():
                    print("\n\tStandard inch field:", field.name)
                    nchoice = input(
                        "\tDo you want to add this to all of these fields? (y/n) ")
                    if (nchoice == 'y'):
                        field.setaddinchchar(True)
                    else:
                        field.setaddinchchar(False)

        else:
            ADD_INCH = False
            print("No changes made to measurement fields")

    # #########################################################################
    # Split file into multiple output files
    # #########################################################################
    nchoice = input(
        '\nDo you need to break up the file into multiple input files (recommended for over 2500 reords? (y/n)')
    if (nchoice == 'y'):
        split_file = True
    else:
        split_file = False

    # ######################################################################### 
    # Process each CSV file provided
    # #########################################################################
    for file in os.listdir('.'):
        if (file == files[choice]):
            # loop through lines in datafile
            if (split_file):
                NewFile = "Fixed_P" + str(split_num) + "_" + files[choice]
            else:
                NewFile = "Fixed_" + files[choice]
            i = 0
            datafields = []
            print('\n=====================================================')
            print('Input File:', file, "  Output File:", NewFile)
            print('=====================================================')
            ofile = open(NewFile, 'w', newline="")
            outlines = csv.writer(ofile, delimiter=',', quotechar='"')
            with open(file) as csvfile:
                filelines = csv.reader(csvfile, delimiter=',', quotechar='"')
                for line in filelines:
                    if (i > 0):      # Don't change the 1st (header) line
                        # Process all lines
                        j = 0
                        for field in line:
                            if DEEPDEBUG:
                                print('checking field:', field,
                                      '\tField Number:', j)

                            # Remove trailing spaces for all entries (for
                            # consistency)
                            field = CleanUpTrailingSpace(field)

                            # Clean up non Unicode characters
                            # Temporarily replace any "?"s with "X"s for this
                            # check
                            tmpfield = field.replace('?', 'X')
                            newfield = tmpfield.encode('ascii', 'replace')
                            # Non ascii found so fix...
                            if (str(newfield).find('?') > tmpfield.find('?')):
                                field = CleanChar(field, repls)
                                # Double Check
                                # Temporarily replace any "?"s with "X"s for
                                # this check
                                newfield = field.replace('?', 'X')
                                newfield = field.encode('ascii', 'replace')
                                # Non ascii found so fix...
                                if (str(newfield).find('?') > field.find('?')):
                                    print(
                                        "ERROR (line:", i, "): Non Ascii found - NOT repaired:", field, newfield)
                                    stop = input(
                                        "Do you want to continue(c) or quit(q)?")
                                    if stop == 'q':
                                        sys.exit()
                                else:
                                    if DEBUG:
                                        print(
                                            "Non Ascii found - repaired:", field)
                                count_updated += 1

                            # Standardize inch measurement fields
                            if csv_fields[j].isstandinch():
                                field = CleanChar(field, inch_repls)
                                count_updated += 1

                            # clear zeros from fields that should only have
                            # text (replace with blanks)
                            if csv_fields[j].istextfield():
                                if (field == "0") or (field == "0.0") or (field == "0.00") or (field == "0.000"):
                                    field = ""
                                    count_updated += 1

                            # clear zeros in measurements (replace with blanks)
                            if csv_fields[j].ismeasurement():
                                if (field == "0") or (field == "0.0") or (field == "0.00") or (field == "0.000"):
                                    field = ""
                                    count_updated += 1

                            # Update Revision Date (as needed)
                            if (j == 19) and (RevDate != ""):
                                field = RevDate
                                count_updated += 1

                            # Clean up Working Pressure (as needed)
                            if csv_fields[j].isnozero():
                                if (field == "0"):
                                    field = ""
                                    count_updated += 1

                            # Add Inch char (") to inch dimenstions
                            if csv_fields[j].addinchchar:
                                if DEBUG:
                                    print("Adding ending inch char to",
                                          csv_fields[j].name)
                                # Only add inch char if the field has a value
                                # that does not already end with the inch char
                                if (len(field) > 0 and field.find(INCH_CHAR) < 0 and field.find("Full") < 0):
                                    field = field.lstrip().rstrip() + INCH_CHAR

                            linedata.append(field)
                            j += 1         # Increment field counter
                            if DEEPDEBUG:
                                print(linedata)
                                input()

                        outlines.writerow(linedata)
                    else:           # Just output the header line
                        outlines.writerow(line)
                        headerline = line        # Save Header lilne

                    i += 1              # Increment line count
                    linedata = []         # Clear line buffer

                    # Handle splitting output files. 
                    if (i > split_cnt and split_file):
                        ofile.close()                      # Close the current file
                        print("\nSplitting output file...")

                        split_num += 1                      # Increment split file number
                        NewFile = "Fixed_P" + \
                            str(split_num) + "_" + files[choice]
                        ofile = open(NewFile, 'w', newline="")
                        outlines = csv.writer(
                            ofile, delimiter=',', quotechar='"')
                        outlines.writerow(headerline)
                        print("Outputing to next file:", NewFile, "\n")

                        # setup to slit again.
                        split_cnt += split_cntinc

                print("Lines Processed: ", i - 1, "\tUpdates: ", count_updated)
                print(
                    "=============================================================================")

                # Close files
                csvfile.close()  # Close the input file
                ofile.close()

                # Process another file
                rchoice = input("Process another file (y/n)? ")
                if rchoice != "y":
                    repeat = False
# #########################################################################
# All Done
# #########################################################################
