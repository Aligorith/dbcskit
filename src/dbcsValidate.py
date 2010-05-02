# DBCSKIT - EER Modelling Toolkit
# Copyright 2010, Joshua Leung (aligorith aT gmail DoT com)
#
# Automated tool to analyse the dbcs and check that it is valid 
# (i.e. no missing keys, etc.)
# 
# Later on, we could investigate making this be able to parse 
# a requirements text, and check whether all major specs have been
# fulfilled.

import sys
import os

from optparse import OptionParser

from dbcsTypes import *
import dbcsLoader

###########################
# BASE TYPES

# Base template for errors
class ModelError:
	__slots__ = [
		'model',		# model where the error occurred
		'item_name',	# offending item identifier
		'error',		# description of why this failed
		'info',			# debug info of what failed
	]
	
	# Constructor 
	def __init__ (self, model, item_name, error, info):
		self.model = model;
		self.item_name = str(item_name);
		self.error = str(error);
		self.info = info;
		
	# Report an error into the stream specified
	def report (self, stream):
		stream.write("X -- %s | Item: %s | Info: %s \n" % (self.error, self.item_name, self.info));

# ------------

# Base template for validation checks
class ValidityCheck:
	# ID of the validity check
	check_id = "Validity Check";
	description = "Description of what check does";
	
	# instance variables
	__slots__ = [
		# errors found
		'errors',
		# was test successful
		'passed'
	]
	
	# constructor - perform the test on the given model
	def __init__ (self, model):
		# init the needed data
		self.errors = [];
		
		# perform the tests
		self.checkValid(model);
		
		# set the status of whether the test was passed
		# 	by definition, this can only happen when there are no errors!
		self.passed = (len(self.errors) == 0);
		
	# test procedure to perform on model
	# OVERRIDE THIS IN SUBCLASSES
	def checkValid (self, model):
		pass;
		
	# Add some errors found
	def add (self, item):
		# check if the data that's being added is an error message
		if isinstance(item, ModelError):
			# add error to the errors found
			self.errors.append(item);
		else:
			raise TypeError, "Cannot add unrecognised type to Entity"
			
		# must return self for add ops
		return self;
	
	# Overloaded concatenation operator - for adding attributes easier
	__add__ = add;
	
	
	# Iterator interface - get iterator over list of errors
	def __iter__ (self):
		return iter(self.errors);
	
###########################
# CHECKS TO PERFORM

# Check that each entity has a single primary key
class Test_Entity_Keys (ValidityCheck):
	# check id
	check_id = "Entity has Primary or Partial Key"
	description = "Does every entity have a single primary key, or a single partial for a weak entity"
	
	# API callback for check
	def checkValid (self, model):
		# check each entity
		for entity in model.entities:
			# check that the entity has a key attribute
			# FIXME: ignore if this is only a specialisation of types with keys...
			if entity.key is None:
				self += ModelError(model, entity.name, "Missing key attribute", None);

# Weak Entity
class Test_WeakEntity_ID (ValidityCheck):
	# check id
	check_id = "Weak Entity is Identified";
	description = "Does every weak entity have a single identifying relationship"
	
	# API callback for check
	def checkValid (self, model):
		# find a weak entity
		for entity in model.entities:
			# if this is a weak entity, perform checks
			if isinstance(entity, WeakEntity):
				self._check_entity(model, entity);
			
	def _check_entity (self, model, entity):
		# weak entity must be identified 
		if entity.identifying_rel == None:
			self += ModelError(model, entity.name, "Weak Entity has no identifying relationship", None);
			return;
		rel = entity.identifying_rel;
		
		# check how it relates to the other entities
		for i,link in enumerate(rel.links):
			# is this own link to this rel?
			if link.entity is entity:
				# check structural constraints:
				#	- must participate (min=1)!
				if link.structCon[0] < 1:
					debugInfo = "L=%d->%s, min=%d" % (i, link.entity.name, link.structCon[0]);
					self += ModelError(model, rel.name, "Weak Entity cannot NOT Participate in Identifying Relationship", debugInfo);
			else:
				# each other entity is free to participate at most once?
				# TODO: reconsider this!
				pass

# Check that each relationship has at least 2 links
# 	- links may refer to same target for recursive rels
class Test_Relationship_Degrees (ValidityCheck):
	# check id
	check_id = "Relationship has Participants"
	description = "Does every relationship have sufficient and valid participants"
	
	# API callback for check
	def checkValid (self, model):
		# check each relationship
		for rel in model.relationships:
			# check if at least 2 links are valid, and/or detect invalid links
			validLinks = 0;
			for i,link in enumerate(rel.links):
				# link entity cannot be none, otherwise is an error
				if link.entity is None:
					debugInfo = "i=%d" % (i);
					self += ModelError(model, rel.name, "Relationship link has missing participant", debugInfo);
				# structural constraint must exist, and have 2 elements (which must be +ve ints, or 'N')
				elif link.structCon is None:
					debugInfo = "i=%d" % (i);
					self += ModelError(model, rel.name, "Relationship link has missing structural constraint", debugInfo);
				elif (len(link.structCon) != 2) or \
						(type(link.structCon[0]) is not int) or \
						((type(link.structCon[1]) is not int) and (link.structCon[1] != 'N')):
					debugInfo = "i=%d, structCon=%s" % (i, link.structCon);
					self += ModelError(model, rel.name, "Relationship link has structural constraint of that isn't of the form (min,max), where min/max are integers", debugInfo); 
				# otherwise, link is ok...
				else:
					validLinks += 1;
			
			# does the relationship have at least 2 valid links?
			if validLinks < 2:
				debugInfo = "validLinks=%d/%d" % (validLinks, len(rel.links));
				self += ModelError(model, rel.name, "Relationship does not have at least 2 valid links", debugInfo);

###########################
# Public API 

# basic set of tests to perform
BASIC_TESTS = [
	Test_Entity_Keys,
	#Test_Entity_Descriptive,
	Test_Relationship_Degrees,
	Test_WeakEntity_ID,
]

# ------------

# validate the provided model, checking that it passes
# the given integrity checks
def validateModel (model, checks):
	# statistics
	failedTests = 0;
	passedTests = 0;
	totalTests = len(checks);
	
	# run each test, and see if it passes
	for check in checks:
		# verify that this is a valid check
		if ValidityCheck in check.__bases__:
			print("$$ Checking if %s ..." % check.check_id);
			try:
				# try to get result for test
				testResult = check(model);
				
				# check if passed or not
				if testResult.passed == False:
					print("!! Some errors found ...");
					failedTests += 1; # TODO: make this report the total number of errors instead?
					
					# dump the errors to stderr for now
					# TODO: later on, we could dump to a specified file instead
					for error in testResult:
						error.report(sys.stderr);
					print("!! ... carrying on ... \n");
				else:
					print("!! ... No sins here :) \n");
					passedTests += 1;
			except:
				sys.stderr.write("ERROR: An error occurred while trying to perform this validity test. Details follow... \n");
				# ...
				raise;
				
	# report statistics of testing
	print("\n$$ %d of %d tests passed. There were %d failure(s) to fix.\n" % (passedTests, totalTests, failedTests))

###########################

# create a graph for the specified file
def processSchema (fileN, mode):
	print("$ Loading schema description...")
	
	# make sure filename is of the form *.dbcs
	# NOTE: this is just hack to allow entering filenames without extension
	fileN = dbcsLoader.changeExtension(fileN, "dbcs");
	
	# get the model used by the file
	model = dbcsLoader.readDBCS(fileN);
	if model is None:
		return False;
	
	# get checks to use
	# FIXME: currently, can only use 'basic'
	#if mode == "basic":
	#	checks = BASIC_TESTS;
	checks = BASIC_TESTS;
	
	# perform the checking
	print("$ Validating Schema...")
	validateModel(model, checks);
	
	print("!! Done... :)");
	
	return True;

###########################

# test complexity
modes = ["basic"]

# -----------

def main ():
	# always print version info first...
	# TODO: we should have a way to supress this for super-scripts...
	print("DataBase Conceptual Schema (EER) Validator");
	print("Copyright 2010, Joshua Leung (aligorith@gmail.com)\n");
	
	# set up option parser for managing the commandline args
	usage = "usage: %prog [-m modename] [file1 [file2 [...]]]";
	parser = OptionParser(usage);
	parser.add_option("-m", "--modes", dest="mode", 
			default="basic", type="string",
			help="Set of tests to perform (out of %s)" % modes)
	
	# parse commandline options
	(options, args) = parser.parse_args()
	
	# mode to use
	if (options.mode) and (options.mode in modes):
		mode = options.mode;
	else:
		mode = modes[0]; # default to 'basic' again
	
	# parse filename arguments
	if len(args) >= 1:
		# argv[0] = scriptname...
		for fileN in sys.argv[1:]:
			# print info on file we're handling
			print("$ Processing file ===> %s ..." % fileN);
			
			# convert the file, then perform tests on it
			processSchema(fileN, mode);
			
			# insert linebreak before next file for clarity
			print("\n"); 
	else:
		# keep looping while user keeps supplying valid filenames 
		while True:
			# get file name to operate on 
			fileN = raw_input(">> File Name (or <Enter> to exit): ");
			
			# no filename given? any trigger to exit...
			if len(fileN) == 0: 
				break;
			
			# convert the file, then perform tests on it
			processSchema(fileN, mode);
		
if __name__ == '__main__':
	main();
