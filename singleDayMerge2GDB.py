#! /usr/bin/env python
# -*- coding: utf-8 -*-

#==============================================================================#
# HISTORY                                                                      #
# -------                                                                      #
# Developed by Philippe Muise, October 2017.                                   #
#                                                                              #
#==============================================================================#
"""USAGE
Module imported and used as part of the condition_darkTargets.py script. It is
executed after "evalAttributes.py" and is the final script executed as part of the
condition_darkTargets.py script.

SUMMARY
Merges the polygons

INPUT
- Total Overlap Feature Classes (automated input): Feature classes containing all
overlapping polygons with two sets of attributes. Provided as input in order to
access the combined targetID and assign it to the corresponding polygons in the
final output feature class.

- noOverlap Feature Classes (automated output): Feature classes containing all
regions from overlapping polygons that already had a single set of attributes.

- toMerge Feature Classes (automated output): Feature classes containing all
overlapping regions that have been evaluated with a single set of attributes.

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
        self.label = "2. singleDayMerge2GDB"
        self.description = "2. Merges dark targets feature classes into single \
        acquisition swathes by day."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = [None]*2

        params[0] = arcpy.Parameter(
            displayName="Dark Features Dataset",
            name="dark_featWorkspace",
            datatype=["DEWorkspace", "DEFeatureDataset"],
            parameterType="Required",
            direction="Input")

        params[1] = arcpy.Parameter(
            displayName="GDB Workspace",
            name="gdbWorkspace",
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
        gdbWorkspace = parameters[1].valueAsText

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

        arcpy.AddMessage("output of each date into the workspace" )
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
                         arcpy.AddMessage("Saving {} to {} in {}".format(fc,gdbWorkspace,outputString))
                     outputString = "RS2_" + key
                     #Saves the dark feature polygons for a specific date to a feature class for that date to the year GDB
                     arcpy.Merge_management(mergeFeatureClasses,os.path.join(gdbWorkspace,outputString))

