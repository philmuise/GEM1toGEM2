#! /usr/bin/env python
# -*- coding: utf-8 -*-

#==============================================================================#
# HISTORY                                                                      #
# -------                                                                      #
# Developed by D. Hennessy, January 2017.                                      #
# Last modified: 31 March 2017 by D. Hennessy.                                 #
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


class mergeDates(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "mergeAreas"
        self.description = "Merges dark targets feature classes into single \
        acquisition swathes by day."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = [None]*2

        # params[0] = arcpy.Parameter(
            # displayName="Overlap Dataset",
            # name="overlapWorkspace",
            # datatype=["DEWorkspace", "DEFeatureDataset"],
            # parameterType="Required",
            # direction="Input")

        params[0] = arcpy.Parameter(
            displayName="GDB Workspace",
            name="gdbWorkspace",
            datatype=["DEWorkspace", "DEFeatureDataset"],
            parameterType="Required",
            direction="Input")

        params[1] = arcpy.Parameter(
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
        arcpy.AddMessage("\nPerforming overall merge...")
        logging.info("Starting mergeAreas.py script...\n")
        # Define variables from parameters
        # overlapWorkspace = parameters[0].valueAsText
        gdbWorkspace = parameters[0].valueAsText
        featWorkspace = parameters[1].valueAsText

        # Determine list of total overlap, no overlap and to merge feature classes in overlap feature dataset workspace to process.
        arcpy.env.workspace = overlapWorkspace
        # mergeList = arcpy.ListFeatureClasses("*_toMerge")
        # totalOverlapList = arcpy.ListFeatureClasses("*_TotalOverlap")
        # noOverlapList = arcpy.ListFeatureClasses("*_noOverlap")
        # if len(mergeList) > 0:
            # arcpy.AddMessage("Workspace contains the following " + str(len(mergeList)) + " feature classes to merge: " + str(mergeList))

        # # Organize toMerge feature classes by date
        # mergeDictbyDate = {}
        # for fc in mergeList:
            # fcPath = os.path.join(overlapWorkspace, fc)
            # fcDate = fc.split("_")[1]
            # mergeDictbyDate[fcDate] = [fcPath]

        # # Append no overlap feature classes toMerge feature classes by date
        # for noOverlapFc in noOverlapList:
            # noOverlapPath = os.path.join(overlapWorkspace, noOverlapFc)
            # noOverlapDate = noOverlapFc.split("_")[1]
            # mergeDictbyDate[noOverlapDate].append(noOverlapPath)

        # Organize dark targets feature classes by date
        arcpy.env.workspace = featWorkspace
        fcList = arcpy.ListFeatureClasses()
        fcDictByDate = {}
        for fc in fcList:
            fcPath = os.path.join(featWorkspace, fc)
            fcSplit = fc.split("_")
            if fcSplit[1] in fcDictByDate:
                fcDictByDate[fcSplit[1]].append(fcPath)
            else:
                fcDictByDate[fcSplit[1]] = [fcPath]