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
Imports and conditions dark targets shapefiles produced by the target feature
extraction process on RADARSAT-2 imagery. Organizes data as feature classes
in a file geodatabase by acquisition day.

INPUT
- Year Folder (user input): Folder containing the desired year's shapefiles produced by the
RADARSAT-2 dark target feature extraction process. File structure must meet the
agreed upon hierarchy in order for the script to find the shapefiles in the
appropriate locations. (shapefiles are located within the "Features" folder,
which are in turn located in its specific radar acquisition folder)

- Attribute Evaluation Criteria (user input): SQL expression which is used to determine
which set of attributes is selected and applied in those regions of overlapping
dark targets which contains two sets of attributes. A default value is entered,
however the parameter can be customized.

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

import singleDayMerge2GDB                           # get module reference for reload
reload(singleDayMerge2GDB)                          # reload step 1
from singleDayMerge2GDB import singleDayMerge2GDB   # reload step 2


class condition_darkTargets(object):
    """
    Calls on a series of scripts to import the shapefiles produced by the
    dark targets feature extraction process. Conditions the data into one
    feature class per acquisition day, organized by year in feature
    datasets.
    """
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "1b. Condition Yearly Dark Targets Data"
        self.description = "Imports dark target shapefiles produced from a \
        specific year's radar acquisition imagery. The data is conditioned for \
        subsequent analysis and exported into a file geodatabase."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        params0 = arcpy.Parameter(
            displayName="Input: NOS File to be converted to GEM2",
            name="year_workspace",
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

        # ================================ #
        # Merge dates into Feature Classes #
        # ================================ #

        loadMerge = singleDayMerge2GDB()
        loadMergeparams = loadMerge.getParameterInfo()
        # Define dark feature folder value
        loadMergeparams[0] = parameters[1]
        # Define GDB location to save values
        loadMergeparams[1] = parameters[2]

        logging.info("condition_darkTargets.py script finished.\n\n")

        return