import arcpy
import os
import sys
import datetime
import logging


class convertGEM1toGEM2(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1b. Prepare Shapefile to be reconstructed to GEM2 standards"
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

    def execute(self, parameters):
# structure
        filetochange = parameters[0].valueAsText
        base_folder = os.path.dirname(filetochange)
        field = 'RsatID'

#make list of all dates to make into feature classes
        images = [row[0] for row in arcpy.da.SearchCursor(filetochange,field)]
        uniqueImage= sorted(list(set(images)))
        years = []
        for item in uniqueImage:
            years.append(item[33:37])
        uniqueYears= sorted(list(set(years)))
        arcpy.AddMessage("Modifying NOS File for the following year(s): {}".format(uniqueYears[0]))


#make folder for year

        for year in uniqueYears:
            year_folder = ("{}\{}".format(base_folder,year))
            if not os.path.exists(year_folder):
                os.makedirs(year_folder)
                arcpy.AddMessage("Created {} folder\n".format(year_folder))

            #create shapefile for each date
            for date in uniqueImage:
                image_folder = os.path.join(year_folder,date)
                if not os.path.exists(image_folder):
                 os.makedirs(image_folder)
                 arcpy.AddMessage("Created {} folder".format(date))
                features_folder = os.path.join(image_folder,'Features')
                if not os.path.exists(features_folder):
                 os.makedirs(features_folder)

                #set up selection
                sqlexpression = "\"RsatID\" =" "\'{}\'".format(date)
                changelyr = os.path.splitext(os.path.basename(filetochange))[0]+"_lyr"

                #create layer and select proper date
                arcpy.MakeFeatureLayer_management(filetochange,changelyr)
                arcpy.SelectLayerByAttribute_management(changelyr,"NEW_SELECTION",sqlexpression)

                #save layer as shape file
                arcpy.CopyFeatures_management(changelyr,os.path.join(features_folder,'dark_target'))
                arcpy.AddMessage("Saved {} to {}".format(date,year_folder))
            return year_folder