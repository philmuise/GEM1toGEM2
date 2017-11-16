#! /usr/bin/env python
# -*- coding: utf-8 -*-

#==============================================================================#
# HISTORY                                                                      #
# -------                                                                      #
# Developed by Philippe Muise, October 2017                                    #
#                                                                              #
#==============================================================================#
"""USAGE
- 1st step following visual analysis of GEM1 step 5 output.

SUMMARY
- This modifies the GEM1 visualisation process dark feature shapefile developed
after Step 5 of the GEM1 process and prepares it to be compatible with the GEM2
process for chlorophyll and persistence analysis. The Radarsat-2 image information
is added to each polygon.

INPUT
- NOS File (user input): Polygon Shapefile of dark features for a specific year.

- Mosaic Datasets (user input): Collection of mosaic datasets for that specific year
found in a geodatabase. GEM1 Step 5 output.

OUTPUT
- Modified NOS File (automated output):"""

import arcpy
import os
import sys
import datetime
import logging


class getRSImageInfo(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1a-getRSImageInfo "
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params0 = arcpy.Parameter(
            displayName="Input: NOS File",
            name="working_folder",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")

        params1 = arcpy.Parameter(
            displayName="Mosaic Datasets from Year GDB",
            name="Mosaic Dataset",
            parameterType="Required",
            direction="Input",
            datatype= "DEDatasetType",
            multiValue = True
            )
        params = [params0, params1]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute. This script requires Spatial Analyst extension to function."""

        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        arcpy.env.overwriteOutput = True

        #script arguments specified by the user
        inputMaskShp = os.path.abspath(parameters[0].valueAsText)
        mosaicDatasets = os.path.abspath(parameters[1].valueAsText)
        mosaicList = mosaicDatasets.split(";")

        #Scratch Folder
        scratchFolder = os.path.join(os.path.dirname(inputMaskShp),"Scratch")
        if not os.path.exists(scratchFolder):
                os.makedirs(scratchFolder)
                arcpy.AddMessage("{} folder made".format(scratchFolder))
        #intermediate variables: will be deleted at the end
        #Output
        outMask = os.path.join(scratchFolder,"{}_RSImageInfo".format(os.path.splitext(os.path.basename(inputMaskShp))[0]))
        footprintShp = os.path.join(scratchFolder,"footprint.shp")
        footprintShpAll = os.path.join(scratchFolder,"footprint_all.shp")

        for mosaic in mosaicList:
            arcpy.AddMessage("Selecting images in the mosaic dataset " + os.path.basename(mosaic)\
                             + " and copying their attributes...")

            #Create the mosaic layer for each mosaic dataset
            mosaicLyr = os.path.basename(mosaic)+"_lyr"
            arcpy.MakeMosaicLayer_management(mosaic,mosaicLyr)

            #Select images in the mosaic dataset that intersect the mask and save each one to a shapefile
            arcpy.SelectLayerByLocation_management(mosaicLyr+"\Footprint","INTERSECT",inputMaskShp)
            arcpy.CopyFeatures_management(mosaicLyr+"\Footprint",footprintShp)

            #Append all the shapefiles created above into one shapefile
            if arcpy.Exists(footprintShpAll) == True:
                arcpy.Append_management(footprintShp,footprintShpAll,"NO_TEST")
            else:
                arcpy.CopyFeatures_management(footprintShp,footprintShpAll)

        #extract attributes of images and add them to the shapefile by joining images and the shapefile spatially
        arcpy.AddMessage("Saving the mask layer with attributes of all the selected images...")
        arcpy.SpatialJoin_analysis(inputMaskShp,footprintShpAll,outMask ,"JOIN_ONE_TO_MANY","KEEP_ALL",\
                                   "","INTERSECT","","")

        tempOutMask = '{}.shp'.format(outMask)

        #delete unnecessary fields
        dropFields = ["SAT_NAME","BEAM_MODE","PASS","POLARIZ","ACQ_DATE","YEAR","AREA_HA","DIAMETER_M",\
                      "DESCR","BeamMode","Polarizati","PixelSize","Projection","BitSize","FilterType",\
                      "Join_Count","TARGET_FID","JOIN_FID","MaskID_1","MinPS","MaxPS","LowPS","HighPS",\
                      "Category","CenterX","CenterY","ZOrder","SOrder","TypeID","StereoID","ItemTS","UriHash",\
                      "Shape_Leng","Shape_Area_1","RefImgName_1","GdbImgName_1","Date_1","BeamMode_1",\
                      "Polarizati_1","PixelSize_1","Projection_1","BitSize_1","FilterType_1"]
        arcpy.DeleteField_management(tempOutMask,dropFields)

        #new field for overlapping images
        arcpy.AddField_management(tempOutMask,'OVERLAP','SHORT',1)

        #Take out rows with satellite imagery that does not coincide with the date of the dark feature
        overlapexpression = 'overlapimage( !GDBIMGNAME!, !Date!)'
        codeblock = """def overlapimage(mosaicdate,radardate):
                           if (mosaicdate[7:] ==  radardate):
                             return '1'
                           else:
                             return '0'"""
        arcpy.CalculateField_management(tempOutMask, "OVERLAP", overlapexpression, "PYTHON_9.3", codeblock)

        #Change Radar imagery field name to GEM2 standard
        arcpy.AddField_management(tempOutMask,'RsatID','TEXT',100)
        arcpy.CalculateField_management(tempOutMask,'RsatID','!GdbImgNa_1!','Python_9.3')
        arcpy.DeleteField_management(tempOutMask,'GdbImgNa_1')

        #make layer from feature class for selection
        arcpy.MakeFeatureLayer_management(tempOutMask,'overlapping','OVERLAP = 1' )

        #Add 'Pid' field and populate for intergration into GEM2. Start counter at 1
        arcpy.AddField_management('overlapping','Pid','SHORT',4)
        arcpy.CalculateField_management('overlapping','Pid','int(!SEEP_ID!.split("_")[2]) + 2','PYTHON_9.3')

        #Declare final output path
        final_output = os.path.join(os.path.dirname(inputMaskShp),"{}_RSimageinfo".format(os.path.splitext(os.path.basename(inputMaskShp))[0]))

        #Save to Products folder
        arcpy.CopyFeatures_management('overlapping', final_output)

        #delete all the intermediate files from the scratch folder
        arcpy.AddMessage("Deleting all the intermediate files...")
        if arcpy.Exists(footprintShp):
            arcpy.Delete_management(footprintShp,"")
        if arcpy.Exists(footprintShpAll):
            arcpy.Delete_management(footprintShpAll,"")
        arcpy.AddMessage("All the intermediate files have been deleted.")

        arcpy.AddMessage("The mask layer with image attributes is created.")

        return final_output
