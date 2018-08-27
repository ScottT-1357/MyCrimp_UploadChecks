# #########################################################################
# MyCrimp_CSpec_Fields: Field information for MyCrimp Cross Reference CSVs
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

while i <= 5:      # Current number of fields
    # Setup required fields
    if i in [0, 1, 2, 3]:
        required_fields.append(True)
    else:
        required_fields.append(False)

    # Setup field size limits
    if i == 4:
        field_lengths.append(1000)
    elif i in [5]:
        field_lengths.append(250)
    else:
        field_lengths.append(50)        # Most common value

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


