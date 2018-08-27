# #########################################################################
# MyCrimp_Customers: ASCII subsitutions for MyCrimp data files
#
# Scott Thompson 8/25/15: Created
#
# #########################################################################

# #########################################################################
# Setup common unicode subsitutions
# #########################################################################
repls = {'à':'a','á':'a','â':'a','ä':'a','ã':'a','ò':'o','ó':'o','ô':'o','õ':'o','ö':'o'}       # Fix accented characters
newrepls = {'é':'e','ë':'e','ê':'e','ê':'e','ë':'e','ù':'u','û':'u','ú':'u','ü':'u' }
repls.update(newrepls)
newrepls = {'À':'A','Á':'A','Â':'A','Ã':'A','Ä':'A','È':'E','É':'E','Ê':'E','Ë':'E' }    
repls.update(newrepls)
newrepls = {'Ò':'O','Ó':'O','Ô':'O','Õ':'O','Ö':'O','Ù':'U','Û':'U','Ú':'U','Ü':'U','Ũ':'U' }    
repls.update(newrepls)
newrepls = {'Ñ':'N', ' ':' ', '–':'-', '±':'+/-', 'Â°':' deg ', 'A°':' deg ', 'A°':' deg '}    ## !!!!! Note this line contains non printable ascii in the subsitution!!!!!
repls.update(newrepls)

