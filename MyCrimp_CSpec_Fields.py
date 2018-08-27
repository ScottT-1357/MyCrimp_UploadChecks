# #########################################################################
# MyCrimp_CSpec_Fields: Field information for MyCrimp Crimp Spec CSVs
#
# Scott Thompson 11/7/14: Created
#                11/12/14: Updated to support file cleanup
#
# #########################################################################

# #########################################################################
# Setup Array of required fields
# #########################################################################
required_fields = []
field_lengths = []
measurement_fields = []
text_fields = []
standinch_fields = []
nozero_fields = []
DEBUG = False
i = 0

while i <= 51:      # Current number of fields
    # Setup required fields
    if i in [0, 1, 2, 3, 5]:
        required_fields.append(True)
    else:
        required_fields.append(False)

    # Setup field size limits
    if i == 0:
        field_lengths.append(250)
    elif i == 1:
        field_lengths.append(150)
    elif i in [2, 10, 11, 14]:
        field_lengths.append(100)
    elif i in [3, 22, 25, 28, 31, 34, 37, 40, 43, 46, 49]:
        field_lengths.append(10)
    elif i == 19:
        field_lengths.append(16)
    elif i == 20:
        field_lengths.append(20)
    elif i in [21, 24, 27, 30, 33, 36, 39, 42, 45, 48, 51]:
        field_lengths.append(1000)
    else:
        field_lengths.append(50)        # Most common value

    # Setup for inch standardization and 0/0.0 cleanup
    if i in [12, 13, 15, 16, 17, 18]:       # Cleanup 0/0.0
        measurement_fields.append(True)
    else:
        measurement_fields.append(False)
        
    # Setup for non measurment field clearnup -->  0/0.0 cleanup
    if i in [4, 6, 7, 19, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36,37, 39, 40, 41, 42, 43, 44, 45,46, 47, 48, 49, 50, 51]:       # Cleanup 0/0.0
        text_fields.append(True)
    else:
        text_fields.append(False)
        
    if i in [3, 12, 14, 15, 17]:       # Use standard inch formating
        standinch_fields.append(True)
    else:
        standinch_fields.append(False)

    if i in [6, 20]:
        nozero_fields.append(True)
    else:
        nozero_fields.append(False)
        
    if DEBUG:
        print("Field: ", i, "\tis required: ", required_fields[i], "\tmax length:", field_lengths[i],
              "  \tis measurement: ", measurement_fields[i], "\tStandard Inch: ", standinch_fields[i],
              "\tno zero:", nozero_fields[i], "\ttext field(no zero)", text_fields[i])
    i += 1


