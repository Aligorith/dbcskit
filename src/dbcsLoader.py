# DBCSKIT - EER Modelling Toolkit
# Copyright 2010, Joshua Leung (aligorith aT gmail DoT com)
#
# Module to read a dbcs description into memory for further manipulation

import sys
import os

from dbcsTypes import *

###############################
# READ FUNCTIONS

# Main API function for this, returning the created model
#	fileN: name of file to load
def readDBCS (fileN):
	# FIXME: temp hack - just eval all into global dict... otherwise we get too many type conflicts that won't work :/ 
	if False: # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
 		# create a new dict to hold the results of evaluating this file
		d = {}
		
		# now, firstly import the dbcs types into this dict so that
		# evaluating the file later will work
		try:
			execfile("dbcsTypes.py", d);
		except:
			# HACK: for convenience when running from same dir as the descriptions
			execfile("engine/dbcsTypes.py", d);
	else: # XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
		d = globals();
	
	# secondly, 'execute' the file the user has given us into this dict
	# too, but be prepared for errors:
	try:
		# check if the filename is valid before executing...
		if os.path.exists(fileN):
			# file exists, so try to process it
			execfile(fileN, d);
		else:
			# file doesn't exist, so we shouldn't throw a nasty error...
			sys.stderr.write("ERROR: invalid filename %s \n" % fileN);
			return None
	except:
		sys.stderr.write("ERROR: an error in the input file %s was encountered while reading. Details follow...\n" % fileN);
		# ...
		raise; # XXX: we should try to nicely format the error to expose only what the user needs to know...
		
	# try to return the model created
	if d.has_key('model'):
		return d['model'];
	else:
		sys.stderr.write("ERROR: no model with identifier 'model = Model(...)' was found\n");
		return None;

###############################
# FILENAME UTILITIES

# change extension of the filename
def changeExtension (fileN, newExt):
	return os.path.splitext(fileN)[0] + "." + newExt;

###############################
