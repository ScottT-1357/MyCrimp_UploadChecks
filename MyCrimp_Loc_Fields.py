# #########################################################################
# MyCrimp_Loc_Fields: Field information for MyCrimp Location CSVs
#
# Scott Thompson 11/7/14: Created
#
# #########################################################################

# #########################################################################
# Setup Array of required fields
# #########################################################################
required_fields = []
field_lengths = []
measurement_fields = []
istextfield = []
standinch_fields = []
nozero_fields = []
DEBUG = False
i = 0

while i <= 12:      # Current number of fields
    # Setup required fields
    if i in [0, 4, 5, 6]:
        required_fields.append(True)
    else:
        required_fields.append(False)

    # Setup field size limits
    if i == 0:
        field_lengths.append(150)
    elif i in [5, 8]:
        field_lengths.append(50)
    elif i in [11, 12]:
        field_lengths.append(14)
    elif i == 6:
        field_lengths.append(10)
    elif i == 9:
        field_lengths.append(250)
    else:
        field_lengths.append(100)        # Most common value

    # Setup for inch standardization and 0/0.0 cleanup
    if i in []:       # Cleanup 0/0.0
        measurement_fields.append(True)
    else:
        measurement_fields.append(False)
        
    if i in []:       # Use standard inch formating
        standinch_fields.append(True)
    else:
        standinch_fields.append(False)

    if i in []:
        nozero_fields.append(True)
    else:
        nozero_fields.append(False)
        
    if DEBUG:
        print("Field: ", i, "\tis required: ", required_fields[i], "\tmax length:", field_lengths[i],
              "  \tis measurement: ", measurement_fields[i], "\tStandard Inch: ", standinch_fields[i],
              "\tno zero:", nozero_fields[i])

    i += 1


