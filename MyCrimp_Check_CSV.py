# #########################################################################
# Check_CrimpSpecCSV: Python script to check for valid Crimp Spec CSV Files
#
# Scott Thompson 5/22/14
#                8/29/14: Updated to support new upload file formats
#                11/7/14: Updated to use field class for information
#                11/14/14: Updated to support any type of MyCrimp CSV File
#
# #########################################################################
import os
import csv
import sys
import re

# #########################################################################
# Define Constants and global variables
# #########################################################################
cross_ref_template='S:\MyCrimp\MyC_Customers\CSV_Templates\cross_ref_template.csv'
cspec_template='S:\MyCrimp\MyC_Customers\CSV_Templates\specification_template.csv'
location_template='S:\MyCrimp\MyC_Customers\CSV_Templates\location_template.csv'
fields=[]
repeat = True
DEBUGDEEP = False
DEBUG = False
STATSBREAKS = 50
STATSLINEBREAK=200
WARNINGBREAKS=50
INCHQUOTECHECK = True
ZEROCHECK = False
DOASCIIFIX = True

# #########################################################################
# Setup options directories for input files
# #########################################################################
from MyCrimp_Customers import DataDirs

Temp_IntExt = ""
Temp_Title = ""
Temp_Link = ""
Temp_Insert = ""
Temp_ExtSkive = ""
Temp_IntSkive = ""
crimpdia_inch = ""
crimpdia_mm = ""
Temp_DSD = ""
dsdie = ""
dsring = ""
repeat = True
warnings = 0

# Setup and compile Regular Expressions needed
#  Crimp Diameter: (1.291"/32.80mm)
crimpdiam_pattern_txt = r'Crimp Diameter: \(([0-9]+.[0-9]+)"/([0-9]+.[0-9]+)mm\)'
crimpdiam_pattern = re.compile(crimpdiam_pattern_txt)

# Setup common unicode subsitutions
from MyCrimp_ASCII_Subs import repls

# #########################################################################
# define Classes
# #########################################################################
class CSV_Field:
    def __init__(self, name, required, size, fieldtype, field_values=[]):
        self.name = name
        self.required = required
        self.size = size
        self.fieldtype = fieldtype
        self.field_values = field_values

    def reqfieldmissing(self, testfield):
        return len(testfield) == 0 and self.required

    def isrequired(self):
        return self.required

    def checksize(self, fieldlength):
        return fieldlength > self.size

# #########################################################################
# define my functions
# ###################################################
# Function: printerror: Print error message
# ###################################################
def printerror(errnum, info, linenum):
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    if errnum == 'TooManyFields':
        print('Error(line:',linenum,'): Too many fields ', info, ': Check for extra commas: \",\")',sep='')
    elif errnum == 'TooFewFields':
        print('Error(line:',linenum,'): Too few fields ', info, ': Check for missing fields',sep='')
    elif errnum == 'ReturnInField':
        print('Error(line:',linenum,'): Newline in field ', info, ': Check for input file',sep='')
    elif errnum == 'DashInSize':
        print('Warning(line:',linenum,'): - in size ', info, ': Sizes should not use - ',sep='')
    elif errnum == 'PossibleDate':
        print('Warning(line:',linenum,'): Multiple / in size, ', info, ': Possible date?',sep='')
    elif errnum == 'MissingRequiredField':
        print('Error(line:',linenum,'): Missing a required field: ', info, ': Add this field to datafile',sep='')
    elif errnum == 'SizeExceedsLimit':
        print('Error(line:',linenum,'): Field exceeds field size limit: ', info, ': Edit datafile',sep='')
    elif errnum == 'ReferenceItemTriple':
        print('Error(line:',linenum,'): Incomplete Reference Item spec (all 3 values required): ', info, ': Edit datafile',sep='')
    elif errnum == 'LinkTypeError':
        print('Error(line:',linenum,'): Link Type must be Int or Ext: |', info, '| Edit datafile',sep='')
    elif errnum == 'MissingLinkTitle':
        print('Error(line:',linenum,'): Links must have a title|', info, '| Edit datafile',sep='')
    elif errnum == 'URLError':
        print('Error(line:',linenum,'): Link must start with http:// or https:// |', info, '| Edit datafile',sep='')
    elif errnum == 'InchANDMM':
        print('Error(line:',linenum,'): Inch and Metric value mismatch |', info, '| Edit datafile',sep='')
    elif errnum == 'DSD':
        print('Error(line:',linenum,'): DeadStop Die and Ring mismatch |', info, '| Edit datafile',sep='')
    elif errnum == 'IncorrectDateField':
        print('Error(line:',linenum,'): Date format is incorrect.  DD-MM-YYYY, not / format |', info, '| Edit datafile',sep='')
    elif errnum == 'NonPrintable':
        print('Error(line:',linenum,'): non printable characters in field |', info, '| Edit datafile',sep='')
        if DEBUGDEEP:
            for i in range (0, len(info)):
               print ("Char ",i," ", info[i], " ", info[i].isprintable())
    elif errnum == 'nonascii':
        print('Error(line:',linenum,'): non ascii characters in field |', info, '| Edit datafile',sep='')
    elif errnum == 'MeasurementRequired':
        print('Error(line:',linenum,'): Measurement Req Format Error |', info, '| Edit datafile',sep='')
    elif errnum == 'InchMissingQuote':
        print('Error(line:',linenum,'): Inch Measurement is missing Quote. |', info, '| Edit datafile',sep='')
    else:
        print('Error: Undefined')
    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
# ###################################################
# Function: printlinefields: printlinefields in nice tabbed format
# ###################################################
def printlinefields(inputline):
    j = 0

    # Print a nice tab format
    for field in inputline:
        if DEBUG:
            print('\tTitle len: ',len(fields[j]),'Field len:',len(field))
        if j >= len(fields):   # Too many fields
            print('Extra field:','\t|',field,'|', sep="")      
        else:                 # Print field as expected
            if len(fields[j]) <= 8:
                print(fields[j],'\t\t\t\t|',field,'|', sep="")
            elif len(fields[j]) <= 15:
                print(fields[j],'\t\t\t|',field,'|', sep="")
            elif len(fields[j]) <= 23:
                print(fields[j],'\t\t|',field,'|', sep="")
            else:
                print(fields[j],'\t|',field,'|', sep="")           
        j += 1
        
# ###################################################
# Function: generalfieldcheck: check for general issues for all fields
# ###################################################
def generalfieldcheck(field_info, field, lnum):
    # check field for return characters
    if field.find('\n') > 0: 
        printerror('ReturnInField',field,lnum)

    # check field for non printable characters
    if not field.isprintable():
        printerror('NonPrintable',field,lnum)
        if DEBUGDEEP:
            for i in range (0, len(field)):
                print ("Char NonPrintable? ",i," ", field[i], " ", field[i].isprintable())
        return -1

    # check fields for non ascii characters
    if DOASCIIFIX:                  # Do ascii subsitutions that fix will do
        for i, j in repls.items():
            field = field.replace(i,j)

    field = field.replace('?', 'X')                                 # Temporarily replace any valid '?' characters
    newfield = field.encode('ascii', 'replace')

    if (str(newfield).find('?') > field.find('?')):    # Non ascii found so fix...
        printerror('nonascii',field,lnum)
        if DEBUGDEEP:
            print("newfield:", newfield, "Position: ", str(newfield).find('?'), " length", len(newfield), " In question", newfield[str(newfield).find('?')])
            print("field:", field.find('?'), " length", len(newfield))
            for i in range (0, len(newfield)):
                print ("Char encoding? ",i," ",field[i], ":", str(newfield[i]))
        return -1

    # Verify required fields are present
    if field_info.reqfieldmissing(field):
        # required field is missing
        printerror('MissingRequiredField',field_info.name,lnum)
        return -1

    # Verify fields do no exceed thier allowable max size
    if field_info.checksize(len(field)):
        # Check field size
        printerror('SizeExceedsLimit',field_info.name+':'+repr(len(field))+'>'+str(field_info.size),lnum)
        return -1

    # Assuming all checks passed, return 1 indicating the field has passed these checks.
    return 1

# ###################################################
# Function: verify that both or none of the inch/metric values are provided
# ###################################################
def inchandmetric(inch, metric):
    # values passed in are length of the fields.  O length means no value was provided.
    return (inch == 0 and metric != 0) or (inch != 0 and metric == 0)

# ###################################################
# Function: Check Crimp Spec CSV
# ###################################################
def cspec_check(inputline, lnum, error, field, fnum):
    global warnings, Temp_IntExt, Temp_Title, Temp_Link, Temp_Insert, Temp_ExtSkive, Temp_IntSkive, Temp_DSD
    global crimpdia_inch, crimpdia_mm, dsdie, dsring

    # Verify that inch measurements don't include "-"      
    if fnum in [3, 8, 12, 15, 17]: 
        if field.find('-') >= 0 and field.find('+/-') == 0:
            printerror('DashInSize',field,lnum)
            error -= 1

    # Verify that dates don't include "/"      
    if fnum in [19]: 
        if field.find('/') >= 0:
            printerror('IncorrectDateField',field,lnum)
            error -= 1

    # Verify that inch measurements have dates (check for multiple "/"s)    
    if fnum in [3, 8, 11, 12, 15, 17]: 
        if field.count('/') >= 2 and field.count(' / ') == 0:
            printerror('PossibleDate',field,lnum)
            error -= 1

    # Determine if inch sizes have a double quote at the end.
    if fnum in [3, 8]:
        if INCHQUOTECHECK:
            if (len(field) > 0 and field.find('.') < 0 and  field.find('\"') < 0 and field.find('***') <0):       # No quote for inch found.
                # NOTE: "speical handling crimp specs include "***" in the crimp diameter so ingore these."
                print("\tWARNING: If possible, end factional inch measurements with a double quote.", lnum, "Field: ", csv_fields[fnum].name, "Data: ", field)
                warnings += 1
                if (warnings % WARNINGBREAKS == 0):
                    stop = input("Do you want to continue(c) or quit(q)?")
                    if stop == 'q':
                        sys.exit()

    # these fields may have inch values.  If so, chech for quote
    if fnum in [12, 15, 17]:
        if INCHQUOTECHECK:
            if (len(field) > 0 and field.find('.') < 0 and  field.find('\"') < 0 and not (field == "Full" or field == "Partial")):       # No quote for inch found.
                print("\tWARNING: If possible, end factional inch measurements with a double quote.", lnum, "Field: ", csv_fields[fnum].name, "Data: ", field)
                warnings += 1
                if (warnings % WARNINGBREAKS == 0):
                    stop = input("Do you want to continue(c) or quit(q)?")
                    if stop == 'q':
                        sys.exit()

    # Verify this is a dead stop crimper, both die and ring are provied.               
    if fnum in [6]: # Save length of Dead Stop Die
         Temp_DSD = len(field)
    if fnum in [7]: # Now check mm matches
        if ((Temp_DSD > 0 and len(field) == 0) or (Temp_DSD == 0 and len(field) > 0)):
            printerror('DSD',csv_fields[fnum].name,lnum)
            error -= 1          

    # Verify that if an inch value is provided, a mm value is also provided               
    if fnum in [8, 12, 15, 17 ]: # Save length of inch value
         Temp_Insert = len(field)
    if fnum in [9, 13, 16, 18]: # Now check mm matches
        if inchandmetric(Temp_Insert, len(field)):
            printerror('InchANDMM',csv_fields[fnum].name,lnum)
            error -= 1   

    # Check for the speical case notes that start with ***       
    if fnum in [21]: 
        if (len(field) != 0) and (field.find('***') == 0 ):
            # Special notes field that starts with ***
            if DEBUG:
                print("\tATTN: Speical Case Notes Field", lnum, "Field: ", csv_fields[fnum].name, "Data: ", field)
            # If this is a Measurement Required case
            if (field.find('Measurement Required') > 0 ):
                if DEBUG:
                    print("\tATTN: Measurment Required", lnum, "Field: ", csv_fields[fnum].name, "Data: ", field[165:])
                if (field.find('Measurement Required') > 0 ):

                    crimpdiam_str = crimpdiam_pattern.search(field)
                    if crimpdiam_str is None:
                        print("\tMeasurement Required Error")
                        printerror('MeasurementRequired',csv_fields[fnum].name,lnum)
                        error -= 1  
                    else:
                        CrimpDiam_mm = float(crimpdiam_str.group(2))
                        CrimpDiam_inch = float(crimpdiam_str.group(1))
                        CrimpDiam_Diff = abs(CrimpDiam_inch*25.4 - CrimpDiam_mm)
                        if (CrimpDiam_Diff >= 0.1):
                            print("\tCD: ", crimpdiam_str.groups(), "mm:", CrimpDiam_mm, " Inch:", CrimpDiam_inch, " Diff: ",CrimpDiam_Diff)
                            printerror('MeasurementRequired',csv_fields[fnum].name,lnum)
                            error -= 1          


    # for int/ext links, field checked in sets of 3
    if fnum in [22, 25, 28, 31, 34, 37, 40, 43, 46, 49] :
        Temp_IntExt = field
    if fnum in [23, 26, 29, 32, 35, 38, 41, 44, 47, 50]:
        Temp_Title = field
    if fnum in [24, 27, 30, 33, 36, 39, 42, 45, 48, 51]:
        Temp_Link = field
        if DEBUG:
            print("Checking Triple: Int/Ext |",Temp_IntExt,"| Title |",Temp_Title,"| URL",Temp_Link)
        # Now that we have all 3 values, perform the checks
        if (Temp_IntExt == "" and Temp_Title == "" and Temp_Link == ""):
            # All values are blank so this is valid but blank
            pass
        else:
            if (Temp_IntExt == "" or Temp_Title == "" or Temp_Link == ""):
                printerror('ReferenceItemTriple',field,lnum)
                return -1
            # Check Link Type
            if (Temp_IntExt != "Int" and Temp_IntExt != "Ext"):
                printerror('LinkTypeError',Temp_IntExt,lnum)
                return -1
            # There has to be a title
            if len(Temp_Title) == 0:
                printerror('MissingLinkTitle',Temp_Title,lnum)
                return -1                    
            # Check URL
            if (Temp_IntExt == "Ext"):
                if (Temp_Link.find('http://') == 0) and (Temp_Link.find('https://') == 0):
                    printerror('URLError',Temp_Link,lnum)
                    error -= 1

    # Warn user if important information is not included
    if fnum in [6]: 
        dsdie = field
    if fnum in [7]: 
        dsring = field
    if fnum in [8]: 
        crimpdia_inch = field
    if fnum in [9]: 
        crimpdia_mm = field
        if crimpdia_inch == "" and crimpdia_mm == "":
            print("\tWARNING: Important information missing: Crimp Diameter, Line:", lnum, "Field: ", csv_fields[fnum].name)
            warnings += 1
        if (crimpdia_inch == "" and crimpdia_mm != "") or (crimpdia_inch != "" and crimpdia_mm == ""):
            print("\tWARNING: Both inch and mm Crimp Diameters should be provided, Line:", lnum, "Field: ", csv_fields[fnum].name)
            warnings += 1    
    if fnum in [10]: 
        if field == "" and dsdie == "":
            print("\tWARNING: Important information missing: Die, Line:", lnum, "Field: ", csv_fields[fnum].name)
            warnings += 1
    if fnum in [11]: 
        if field == "" and dsring == "":
            print("\tWARNING: Important information missing: Crimper Setting, Line:", lnum, "Field: ", csv_fields[fnum].name) 
            warnings += 1         
    # Verify that inch measurements don'g include "-"      
    if fnum in [12, 13, 15, 16, 17, 18, 20]: 
        if ZEROCHECK:
            if field == "0" or field == "0.0":
                print("\tWARNING: blank fields display better in MyCrimp that zeros.  Line:", lnum, "Field: ", csv_fields[fnum].name)
                warnings += 1

    return error

# ###################################################
# Function: Check Crimp Spec CSV
# ###################################################
def loc_check(inputline, lnum, error, field, fnum):
    if fnum in [9]:
        print("Length of link field:", len(field))
        if (Temp_Link.find('http://') == 0) and (Temp_Link.find('https://') == 0):
            printerror('URLError',field,lnum)
            error -= 1
    return error

# ###################################################
# Function: Check Crimp Spec CSV
# ###################################################
def cref_check(inputline, lnum, error, field, fnum):
    if fnum in [5]:
        if (Temp_Link.find('http://') == 0) and (Temp_Link.find('https://') == 0):
            printerror('URLError',field,lnum)
            error -= 1
    return error

# ###################################################
# Function: checkinputline: validate input line
# ###################################################
# !!!! This will change as fields change !!!!
def checkinputline(inputline,lnum):
    global warnings, errors
    j = 0
    error = 0

    # check each field
    for field in inputline:
        if DEBUGDEEP:
            print('\tchecking field(',j,'):',field, sep='')

        # Execute standard field checks: size, non ascii, required, ...
        if generalfieldcheck(csv_fields[j],field,lnum) < 0:
            error -= 1       

        # Checking fields variable by csv type
        if csv_type == "CrimpSpec":
            if cspec_check(inputline, lnum, error, field, j) < 0:
                error -= 1
        elif csv_type == "Location":
            if loc_check(inputline, lnum, error, field, j) < 0:
                error -= 1
        elif csv_type == "CrossRef":
            if cref_check(inputline, lnum, error, field, j) < 0:
                error -= 1
        else:
            print ("Error: Unknown CSV Type: ", csv_type)
            error -= 1

        j += 1
    # return and let caller know if there was an error
    if DEBUG:
        print('CheckInputLine Error Cnt:',error)
    return error   

# ###################################################
# Function: printsummary: print summary of the CSV file
# ###################################################
# !!!! This will change as fields change !!!!
def printsummary():
    print('\n======= File Summary ==========================')
    statcnt = 0
    i = 0
    for list in StatsLists:
        print('Unique ',fields[i],":",list.__len__(), "\t===>")
        list.sort()
        print ("\t|", end="", sep='')
        addreturn = 0
        for item in list:
            print (item,'|', end="", sep='')
            addreturn += len(item)
            if addreturn > STATSLINEBREAK:
                print("")
                print ("\t|", end="", sep='')
                addreturn = 0
            statcnt += 1
        i += 1
        print("")
        if statcnt > STATSBREAKS:
            statcnt = 0;
            mychoice = input("return to continue (q to quit)")
            if mychoice == "q":
                break

# ###################################################
# End Functions
# ###################################################  

# #################################################################################################
# #################################################################################################
# Main Program
# #################################################################################################
# #################################################################################################
# #########################################################################
# Main Loop through files until the user quits
# #########################################################################
while repeat:
    warnings = 0
    # ##########################################################################
    # Setup for CSV processing
    # ##########################################################################
    # Determine the type of CSV
    i=0
    tchoice = 1000
    cnt = 3
    print("\nProcess which type of MyCrimp CSV Input?")
    for csv_type in ['Crimp Specification', 'Location CSV', 'Cross Reference CSV']:
        print("\t", i, csv_type)
        i += 1
    print("\t", i, "Quit")   

    while (tchoice > cnt):
        tchoice = (input("\nCSV type to check? (0 - "+str(i)+"): "))
        if (tchoice == ""):
            tchoice = 1000 
        elif (int(tchoice) == cnt):
            sys.exit()
        else:
            tchoice = int(tchoice)

    if tchoice == 0:            # Crimp Spec
        csv_type = "CrimpSpec"
        template = cspec_template
        from MyCrimp_CSpec_Fields import required_fields, field_lengths
    elif tchoice == 1:          # Location CSV
        csv_type = "Location"
        template = location_template
        from MyCrimp_Loc_Fields import required_fields, field_lengths
    elif tchoice == 2:          # Cross Reference CSV
        csv_type = "CrossRef"
        template = cross_ref_template
        from MyCrimp_CRef_Fields import required_fields, field_lengths
    else:
        print("Error: Invalid choice", i)
        sys.exit()

    tfile = open(template,'r')
    firstline = tfile.readline()   # Read 1st line (the line with the headers
    fields = firstline.split(',')
    print("Processing template file: ",template)
    tfile.close()

    # Setup class for each field
    csv_fields = []
    i = 0 
    # Clean up headers by removing leading/trailing white space
    for field in fields:
        field = field.lstrip()
        field = field.rstrip()
        # Setup Class for each field
        csv_fields.append(CSV_Field(field, required_fields[i], field_lengths[i], "text"))
        if DEBUG:
            print("Creating CSV Field Object: ", field)
        i += 1
    Template_Fields = len(csv_fields) 
    if DEBUG:
        print("CSV records should have", Template_Fields, "records")
        
    # #########################################################################
    # Determine which Directory to work from
    # #########################################################################
    cnt = 0
    choice = 1000      #Default
    print('\nWhich Directory do you want to work from?\n')
    for dir in DataDirs:
        dir = dir[25:]
        print('\tOption',cnt,':',dir,'?')
        cnt += 1
    print('\tOption',cnt,' quit')

    while (choice >= cnt):
        choice = input('\nWhat Option # (< '+str(cnt)+'):')
        if (choice == ""):
            choice = 1000
        elif (int(choice) == cnt):
            sys.exit() 
        else:
            choice = int(choice)

    print('\nWorking from:',DataDirs[choice])
         
    os.chdir(DataDirs[choice])
    # #########################################################################
    # Now determine which file to process
    # #########################################################################
    files=[]
    cnt = 0
    choice=1000
    print('\nWhich Crimp Spec do you want to process?\n')
    # Display possible CSV files in this directory to process
    for file in os.listdir('.'):
        if file.endswith(".csv"):
            print('\tFile',cnt,': -',file)
            files.append(file)
            cnt += 1
    print('\tOption',cnt,' quit')

    while (choice >= cnt):
        choice = input('\nWhat Option # (< '+str(cnt)+'):')
        if (choice == ""):
            choice = 1000
        elif (int(choice) == cnt):
            sys.exit() 
        else:
            choice = int(choice)

    if DEBUG:
        print('\nWorking on file:',files[choice],"\n")
         
    # #########################################################################
    # Process each CSV file provided
    # #########################################################################
    for file in os.listdir('.'):
        if (file == files[choice]):
            # Setup Stats
            StatsLists = []            
            for field in fields:
                StatsLists.append([])
            
            # loop through lines in datafile
            i=0
            datafields=[]
            with open(file) as csvfile:
                filelines = csv.reader(csvfile, delimiter=',', quotechar='"')
                baddata=0
                for line in filelines:
                    # Check for valid field counts
                    if len(line) < Template_Fields:
                        printerror('TooFewFields',len(line),i)
                        print(line)
                        baddata += 1
                        printlinefields(line)
                        resp = input("Enter to continue or q to quit\n")
                        if (resp == "q"):
                            break
                    elif len(line) > Template_Fields:
                        printerror('TooManyFields',len(line),i)
                        print(line)
                        baddata += 1
                        printlinefields(line)
                        resp = input("Enter to continue or q to quit\n")
                        if (resp == "q"):
                            break
                    else:   # Correct number of fields so check each field in the line
                        if (i > 0):               # Process the data line (skip the header row)
                            if checkinputline(line,i) < 0:
                                baddata += 1
                                print(line)
                                if DEBUG:
                                    printlinefields(line)
                                resp = input("Enter to continue or q to quit\n")
                                if (resp == "q"):
                                    break
                            # Collect Stats
                            j = 0       # Reset Field counter
                            for field in line:
                                if StatsLists[j].count(field) == 0:    # Have we seen this item before?
                                    StatsLists[j].append(field)
                                j += 1         # Increment field counter

                    i += 1    # Increment line count

                csvfile.close() # Close the input file

                # Print File Summary
                print('=====================================================')
                print('File:', file, "Type: ", csv_type)
                print('Data lines:',i-1)
                print('Input lines with errors:',baddata)
                print("Total warnings (all lines):",warnings)
                print('Input lines without errors:',i-baddata-1)
                print('=====================================================')

                # Give user option for verbose output
                verbose = input('Do you want an input summary output (y/n)? ')
                if verbose == 'y':
                    printsummary()

    choice = input("\nProcess another file? (y/n) ")
    if choice != "y":
        repeat = False
        
# #########################################################################
# All Done
# #########################################################################

