#! /usr/bin/env python
# -*- coding: utf-8 -*-

#==============================================================================#
# HISTORY                                                                      #
# -------                                                                      #
# Developed by Philippe Muise, October 2017                                    #
# Script structure based off of D. Hennessey's GEM2 condition_darkTargets.py   #
#==============================================================================#
"""USAGE
Module imported and used as the "1_Condition Yearly Dark Targets Data" script
tool in the "GEM2_Oil_Seep_Detection_Analysis" Python Toolbox.

SUMMARY
This script separates all the dark targets from the 'NOS_XXXX_RSimageinfo'
shapefile for a selected year produced by the visual interpretation process
on RADARSAT-2 imagery following GEM1 development. The data is cleaned up and
same day acquisitions are merged together into a single feature class per day.
The data is conditioned and organized in a file geodatabase that is created
with the same name and located in the same directory as the selected folder.

INPUT
- NOS File (user input):'NOS_XXXX_RSimageinfo' shapefile developed by Step 1.

OUTPUT
- Yearly Data File Geodatabase (automated output): A file geodatabase is
produced in the same folder of the input year folder and is also named the same
as the input year folder. (e.g. 2010.gdb) The FGDB contains the feature classes
of all the dark targets per acquisition day, as well as the working files used
in the conditioning, which are placed in the "dark_features", "feature_overlap"
and "feature_union" feature datasets."""

# Libraries
# =========
import arcpy
import os
import logging

import convertGEM1toGEM2                                    # get module reference for reload
reload(convertGEM1toGEM2)                                   # reload step 1
from   convertGEM1toGEM2 import convertGEM1toGEM2           # reload step 2

# Reload steps required to refresh memory if Catalog is open when changes are made
import createGDBStruct                      # get module reference for reload
reload(createGDBStruct)                     # reload step 1
from createGDBStruct import createGDBStruct # reload step 2

import loadDarkTargets                      # get module reference for reload
reload(loadDarkTargets)                     # reload step 1
from loadDarkTargets import loadDarkTargets # reload step 2


import evalAttributes                       # get module reference for reload
reload(evalAttributes)                      # reload step 1
from evalAttributes import evalAttributes   # reload step 2

class condition_darkTargets(object):
    """
    Calls on a series of scripts to import the shapefiles produced by the
    dark targets feature extraction process. Conditions the data into one
    feature class per acquisition day, organized by year in feature
    datasets.
    """
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "2a. Condition Yearly Dark Targets Data"
        self.description = "Imports dark target shapefiles produced from a \
        specific year's radar acquisition imagery. The data is conditioned for\
        subsequent analysis and exported into a file geodatabase."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        params0 = arcpy.Parameter(
            displayName="Input: NOS File to be converted to GEM2",
            name="NOS File with RSid information",
            datatype="DEShapefile",
            parameterType="Required",
            direction="Input")

        params1 = arcpy.Parameter(
            displayName="Dark Features Dataset",
            name="dark_featDS",
            datatype="DEFeatureDataset",
            parameterType="Derived",
            direction="Output")

        params2 = arcpy.Parameter(
            displayName="GDB Workspace",
            name="gdbWorkspace",
            datatype=["DEWorkspace", "DEFeatureDataset"],
            parameterType="Derived",
            direction="Output")

        params3 = arcpy.Parameter(
            displayName="GDB Workspace",
            name="gdbWorkspace",
            datatype=["DEWorkspace"],
            parameterType="Derived",
            direction="Output")

        params = [params0, params1, params2, params3]

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
        # Set log configuration
        logPath = os.path.join(os.path.dirname(parameters[0].valueAsText), "logs")
        if not os.path.exists(logPath):
            os.makedirs(logPath)
        logFile = os.path.join(logPath, "conditionData.log")
        logging.basicConfig(filename=logFile, format='%(asctime)s -- %(message)s', datefmt='%d/%m/%Y %H:%M:%S', level=logging.INFO)
        logging.info("Starting condition_darkTargets.py script...\n")

        # ================================================================= #
        # Create Create Dark Feature Shapefiles From Visualisation Master   #
        # ================================================================= #
        arcpy.AddMessage("Running convertGEM1toGEM2.py for {}/n/n".format(parameters[0]))
        conversion = convertGEM1toGEM2()
        conversionparams = conversion.getParameterInfo()
        conversionparams[0] = parameters[0]
        feature_folder = conversion.execute(conversionparams)
        arcpy.SetParameterAsText(3, feature_folder)
        arcpy.AddMessage("Succesfully converted {} to GEM2 formatting/n/n".format(parameters[0]))

        # ========================= #
        # Create File GDB Structure #
        # ========================= #
        arcpy.AddMessage("Running createGDBStruct.py for {}/n/n".format(parameters[0]))
        createGDB = createGDBStruct()
        createGDBparams = createGDB.getParameterInfo()
        # Define products folder value (parent directory to year folder)
        createGDBparams[0] = os.path.dirname(parameters[3].valueAsText)
        # Define File GDB name value (based on year folder being processed)
        createGDBparams[1] = os.path.basename(parameters[3].valueAsText)
        # Execute Create File GDB script
        feat_DS, gdbWorkspace = createGDB.execute(createGDBparams, None)
        # Assign return dataset values to output parameters
        arcpy.SetParameterAsText(1, feat_DS)
        arcpy.SetParameterAsText(2, gdbWorkspace)
        arcpy.AddMessage("Completed createGDBStruct.py for {}/n/n".format(parameters[0]))

        # ============================ #
        # Load Dark Targets shapefiles #
        # ============================ #

        loadSHP = loadDarkTargets()
        loadSHPparams = loadSHP.getParameterInfo()
        # Define year workspace folder value
        loadSHPparams[0] = parameters[3]
        # Define dark features dataset value
        loadSHPparams[1] = parameters[1]
        # Execute Load Dark Targets script
        loadSHP.execute(loadSHPparams, None)

        logging.info("condition_darkTargets.py script finished.\n\n")

        return