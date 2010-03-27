# Automated tool to analyse the dbcs and check that it is valid 
# (i.e. no missing keys, etc.)
# 
# Later on, we could investigate making this be able to parse 
# a requirements text, and check whether all major specs have been
# fulfilled.

from dbcsTypes import *

###########################
# TESTS TO PERFORM

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
	
	

###########################
# Public API 

# basic set of tests to perform
BASIC_TESTS = []

# ------------

# validate the provided model, checking that it passes
# the given integrity checks
def validateModel (model, checks):
	pass;

###########################
