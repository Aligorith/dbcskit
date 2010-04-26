# DBCSKIT - EER Modelling Toolkit
# Copyright 2010, Joshua Leung (aligorith aT gmail DoT com)
#
# Prototypes of the various datatypes for EER Schema Representations
# TODO: Split these out into separate files as needed...

from dbcsUtils import *

###############################
# CONSTANTS

# cardinality
MANY = 'N' # XXX

# 'structural constraints'
PARTIAL_SINGLE	= (0, 1);
PARTIAL_MANY 	= (0, MANY);
TOTAL_SINGLE	= (1, 1);
TOTAL_MANY  	= (1, MANY);

###############################
# TYPE DEFINES

# The container for everything we do
class Model:
	__slots__ = [
		# Simple MetaData 
		'name', 
		'description', 
		'authors',
		
		# Data in the model
		'entities',
		'relationships'
	]
	
	# Constructor 
	def __init__ (self, name, description, authors):
		# store given metadata
		self.name = name;
		self.description = description;
		self.authors = authors;
		
		# init lists for user data defined later
		self.entities = [];
		self.relationships = [];

	# Add item
	def add (self, item):
		# entity?
		if isinstance(item, Entity):
			# TODO: check if exists yet before adding...
			self.entities.append(item);
		# relationship?
		elif isinstance(item, Rel):
			# TODO: check if exists yet before adding...
			self.relationships.append(item);
		else:
			raise TypeError, "Cannot add unrecognised type to Model"
			
		# must return self for add ops
		return self;
		
	# Add item alias/shortcut
	__add__ = add;
	
	# Get a string containing the author names
	def getAuthorsString (self):
		# number of authors?
		numNames = len(self.authors);
		
		# handle the various cases
		if numNames >= 3:
			result = "";
			for i,name in enumerate(self.authors):
				# 'and' before name?
				if i == (numNames-1):
					result += "and ";
					
				# the name
				result += name;
				
				# comma (if needed)
				if i != (numNames-1):
					result += ", ";
			
			return result;
		elif numNames == 2:
			return "%s and %s" % self.authors;
		elif numNames:
			return self.authors[0][:];
		else:
			return "";

# -----------

# An entity type
class Entity:
	__slots__ = [
		# Simple MetaData
		'name',
		
		# Data held by the entity
		'key',				# key attribute (primary key for normal entities, partial for weak)
		'attributes',		# non-key attributes
		'specialisations',	# specialisations (i.e. subclasses) of this Entity
	]
	
	# Constructor
	def __init__ (self, model, name, specs_of=[]):		
		# Own Initialisation -----------------
		# Name of the entity - must be validated
		self.name = validateERName(name);
		
		# init lists for user data later
			# primary key
		self.key = None;
			# attributes for this entity
		self.attributes = []
			# specialisations
		self.specialisations = []
		
		# Registration to rest of DB --------
		# Add entity to the model
		model.add(self);
		
		# Add entity to the specialistions that it is derived from
		for spec in specs_of:
			spec.add(self);
	
	# Add some attribute or related Entity type
	def add (self, item):
		# check if the data that's being added is some form of Attribute
		if isinstance(item, Attr):
			# TODO: check if exists yet before adding...
			self.attributes.append(item);
			
			# if this attribute is tagged as being a key...
			if item.key:
				# make it our key if we haven't got one yet
				if self.key == None:
					self.key = item;
				# otherwise, clear the key flag from the Attribute?
				else:
					#item.key = False;
					pass;
		# check if we're adding a specialisation
		elif isinstance(item, Specialisation):
			# TODO: check if exists yet before adding...
			self.specialisations.append(item);
		else:
			raise TypeError, "Cannot add unrecognised type to Entity"
			
		# must return self for add ops
		return self;
	
	# Overloaded concatenation operator - for adding attributes easier
	__add__ = add;

# A weak entity type
# NOTE: we could perform special validation to make identifying rel exist, but instead we'll just trust that it does
# TODO: perhaps that is still the better option, since then we can validate the graph..
class WeakEntity (Entity):
	pass;
	
# -----------

# Specialisation
class Specialisation:
	__slots__ = [
		'role',				# attribute or whatever which determines which specialisation to take 
		'total',			# total or partial specialisation (defualts to total)
		
		'parent_entity',	# parent entity (i.e. superclass of the subclasses)
		'derived_entities',	# list of entities derived from the parent (i.e. subclasses) 
	]

	# Constructor 
	def __init__ (self, parentEntity, role=None, total=True):
		# store the parent entity
		if parentEntity:
			# store reference, and also link this specialisation back ot the owner
			self.parent_entity = parentEntity;
			parentEntity.add(self);
		else:
			raise ValueError, "No parent entity for specialisation!"
		
		# prepare the list for the derived entities
		self.derived_entities = [];
		
		# attribute or so which determines how this is determined
		if role:
			self.role = validateAttrName(role);
		else:
			self.role = None;
			
		# store the participation
		self.total = total;
		
	# Add some Entity type to the specialisation...
	def add (self, item):
		# check if the data that's being added is some form of Attribute
		if isinstance(item, Entity):
			# TODO: check if exists yet before adding...
			self.derived_entities.append(item);
		else:
			raise TypeError, "Cannot add unrecognised type to Specialisation"
			
		# must return self for add ops
		return self;
	
	# Overloaded concatenation operator - for adding attributes easier
	__add__ = add;
		
# Disjoint Specialisation
# NOTE: for now, just a complete copy of the parent
class DisjointSpec (Specialisation):
	pass;

# Overlapping Specialisation
# NOTE: for now, just a complete copy of the parent
class OverlapSpec (Specialisation):
	pass;

# -----------

# Relationship
class Rel:
	__slots__ = [
		# MetaData 
		'name',
		
		# Data held by the entity
		'links',
		'attributes'
	]	
	
	# Constructor 
	def __init__ (self, model, name, links):
		# Own Initialisation -----------------
		# Name of the entity - must be validated
		self.name = validateERName(name);
		
		# Store the list of links (to entities) relationship has
		self.links = links;
		# Create list of attributes
		self.attributes = [];
		
		# Registration to rest of DB --------
		# Add relationship to the model
		model.add(self);
		
	# Add some attribute
	def add (self, item):
		# check if the data that's being added is some form of Attribute
		if isinstance(item, Attr):
			# TODO: check if exists yet before adding...
			self.attributes.append(item);
		else:
			raise TypeError, "Cannot add unrecognised type to Relationship"
			
		# must return self for add ops
		return self;
	
	# Overloaded concatenation operator - for adding attributes easier
	__add__ = add;
	
# Identifying Relationship
# NOTE: this is really just a direct copy of Relationship...
# TODO: need to override the constructor to validate constraints!
class IdentifyingRel (Rel):
	pass;
	
# Link
class Link:
	__slots__ = [
		'role_name',			# name of the role played 
		'entity',				# entity that this link attaches to
		'structCon',			# structural constraint (as 2-ary tuple)
	]
	
	# Constructor
	def __init__ (self, entity, structuralConstraint, role_name=""):
		# validate role name
		self.role_name = role_name.lower(); # XXX
		
		# store other details
		self.entity = entity;
		self.structCon = structuralConstraint;

# -----------

# Attribute
class Attr:
	__slots__ = [
		# MetaData
		'name',			# name of attribute
		'key'			# is attribute a Primary or Partial key (to be checked against the entity)
		
		# Composite attributes only (but compound can be used in conjunction with others)
		'components'	# attributes which form the composite
	]
	
	# Constructor
	def __init__ (self, name, components=[], key=False):
		# validate attribute name
		self.name = validateAttrName(name);
		
		# store key status
		self.key = key;
		
		# store the components
		# TODO: should verify that they're all valid...
		self.components = components;
		
	# Add some attribute (to make composite)
	def add (self, item):
		# check if the data that's being added is some form of Attribute
		if isinstance(item, Attr):
			# TODO: check if exists yet before adding...
			self.components.append(item);
		else:
			raise TypeError, "Cannot add unrecognised type to Composite Attribute"
			
		# must return self for add ops
		return self;
	
	# Overloaded concatenation operator - for adding attributes easier
	__add__ = add; 
		
	
# Derived Attribute
# NOTE: this is simply a copy of the basic Attribute type for now
class DerivedAttr (Attr):
	pass;
	
# MultiValued Attribute
# NOTE: this is simply a copy of the basic Attribute type for now
class MultiAttr (Attr):
	pass;

###############################
