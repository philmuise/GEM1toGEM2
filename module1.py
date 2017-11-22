with arcpy.da.SearchCursor(r'K:\Projects\GEM1\GEM1toGEM2\Products\NOS_2016_RSimageinfo.shp', 'SEEP_ID') as cursor:
    seepIDList = [row[0] for row in cursor]

duplicateSeepID = list(set(x for x in seep if seep.count(x)>1))

with arcpy.da.UpdateCursor(r'K:\Projects\GEM1\GEM1toGEM2\Products\NOS_2016_RSimageinfo.shp',['FID','SEEP_ID']) as cursor:
    for row in cursor:
         if row[1] in duplicateSeepID and (row[0] % 2 == 0):
                        row[1] = 0
                        cursor.updateRow(row)