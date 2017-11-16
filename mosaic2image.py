import arcpy
import os
import sys
import datetime
import logging


class mosaic2image(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1. Prepare Shapefile to be reconstructed to GEM2 standards"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params0 = arcpy.Parameter(
            displayName="Input: NOS file",
            name="working_folder",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")

        params = [params0]

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
# structure
        filetochange = parameters[0].valueAsText
        path = os.path.dirname(filetochange)
        mosaicdate = 'mosaic_20160803'
#set up selection
        sqlexpression = "\"GDBIMGNAME\" =" "\'mosaic_20160803\'"
        changelyr = os.path.splitext(os.path.basename(filetochange))[0]+"_lyr"
#create layer and select proper date
        arcpy.MakeFeatureLayer_management(filetochange,changelyr)
        arcpy.AddMessage('made feature layer {}\n'.format(changelyr))
        arcpy.AddMessage('abs path = {},{}'.format(path,sqlexpression))
        arcpy.SelectLayerByAttribute_management(changelyr,"NEW_SELECTION",sqlexpression)
#save shape file
        arcpy.CopyFeatures_management(changelyr,"{}/mosaic_20160803".format(path))
        arcpy.AddMessage("Saved {} to {}".format(mosaicdate,path))
#Iterate through shapefiles to create feature classes

##        arcpy.SelectLayerByAttribute_management()