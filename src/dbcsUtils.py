# DBCSKIT - EER Modelling Toolkit
# Copyright 2010, Joshua Leung (aligorith aT gmail DoT com)
#
# Assorted functions to validate input

# Validate entity and relationship names
def validateERName (name):
	# make sure it is a string first
	name = str(name);
	newName = "";
	
	# for each character, make sure it is valid
	# TODO: we can probably do this in a more efficient way without
	# 		making a copy of the string, but oh well...
	for ch in name:
		# if x is an alphanumeric character, convert to uppercase and add
		if ch.isalnum():
			newName += ch.upper();
		# if x is a space or underscore, add an underscore
		elif ch in (' ', '_'):
			newName += '_';
	
	# return the new name
	return newName;
	
# Validate attribute names
def validateAttrName (name):
	# make sure it is a string first
	name = str(name);
	newName = "";
	
	# for each character, make sure it is valid
	# TODO: we can probably do this in a more efficient way without
	# 		making a copy of the string, but oh well...
	for ch in name:
		# if x is an alphanumeric character add
		if ch.isalnum():
			# if first character, capitalise, others are all lower...
			if len(newName) == 0:
				newName += ch.upper();
			else:
				newName += ch.lower();
		# if x is a space or underscore, add an underscore
		elif ch in (' ', '_'):
			newName += '_';
	
	# return the new name
	return newName;
	
