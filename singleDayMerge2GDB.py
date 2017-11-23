#! /usr/bin/env python
# -*- coding: utf-8 -*-

#==============================================================================#
# HISTORY                                                                      #
# -------                                                                      #
# Developed by Philippe Muise, October 2017.                                   #
#                                                                              #
#==============================================================================#
"""USAGE
Lauched after condition_darkTargets.py, this tool populates the yearly geodatabase
with the dark features by day rather than by swath.

SUMMARY
Merges the polygons from the same date, but from different Radarsat-2 images.

INPUT
- Dark features dataset containing all dark features organised by Radarsat-2
image.

OUTPUT
- Acquisition day Feature Classes (automated output): Output feature classes
resulting from the Merge of the toMerge and noOverlap feature classes for each
acquisition day. The Total Overlap feature class is used to pull the combined
targetID value and apply it to this feature class. These feature classes are
placed in the Yearly Dark Targets geodatabase for the specified year."""

# Libraries
# =========
import arcpy
import os
import logging


class singleDayMerge2GDB(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2b. Merge Dark Feature Shapefiles to Single Dates"
        self.description = "2b. Merges dark targets feature classes into single \
        acquisition swathes by day."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = [None]

        params[0] = arcpy.Parameter(
            displayName="Dark Features Dataset",
            name="dark_featWorkspace",
            datatype=["DEWorkspace", "DEFeatureDataset"],
            parameterType="Required",
            direction="Input")

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
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
        """The source code of the tool."""
        # Define variables from parameters
        featWorkspace = parameters[0].valueAsText
        gdbWorkspace = os.path.dirname(featWorkspace)

        #Set workspace as dark features folder
        arcpy.env.workspace = featWorkspace
        fcList = arcpy.ListFeatureClasses()
        fcDictByDate = {}

        #Set up dictionary for each date
        for fc in fcList:
            fcPath = os.path.join(featWorkspace, fc)
            fcSplit = fc.split("_")
            if fcSplit[1] in fcDictByDate:
                fcDictByDate[fcSplit[1]].append(fcPath)

            else:
                fcDictByDate[fcSplit[1]] = [fcPath]

        for key in fcDictByDate:

                #Check if only one shapefile for a specific date
                if len(fcDictByDate[key]) == 1:
                    arcpy.AddMessage("Saving shapefile as Feature class in {}".format(gdbWorkspace))
                    fc = fcDictByDate[key][0]
                    outputString = "RS2_" + key
                    arcpy.AddMessage("Saving {} to {} as {}".format(fc,gdbWorkspace,outputString))

                    #Saves the dark feature polygons for a specific date to a feature class for that date to the year GDB
                    arcpy.FeatureClassToFeatureClass_conversion(fc,gdbWorkspace,outputString)

                else:
                     mergeFeatureClasses = []
                     for fc in fcDictByDate[key]:
                         mergeFeatureClasses.append(fc)

                     outputString = "RS2_" + key
                     arcpy.AddMessage("Saving {} to {} in {}".format(fc,gdbWorkspace,outputString))
                     #Saves the dark feature polygons for a specific date to a feature class for that date to the year GDB
                     arcpy.Merge_management(mergeFeatureClasses,os.path.join(gdbWorkspace,outputString))