# DBCSKIT - EER Modelling Toolkit
# Copyright 2010, Joshua Leung (aligorith aT gmail DoT com)
#
# Load in a dbcs description, and create a GraphViz file from it
# Optionally, run graphviz too...

import sys
import os

from optparse import OptionParser

from dbcsTypes import *
import dbcsLoader

##################################

# write the given attribute to the graph file
def writeAttribute (f, owner_name, attr):
	# make name for this attribute node
	aName = "%s_a%s" % (owner_name, attr.name);
	
	# attribute itself
	#	- options
	# 	NOTE: graphviz DOESN'T DO UNDERLINE, so just change the color...
	opts = ['shape=ellipse'];
	opts.append('fillcolor="lightcyan1"');
	opts.append('label="%s"' % attr.name);
	if isinstance(attr, MultiAttr):
		# multivalued are always drawn with a double border
		opts.append('peripheries=2');
		opts.append('style="filled,solid"');
	elif isinstance(attr, DerivedAttr):	
		# derived keys are always drawn with dotted lines
		opts.append('style="filled,dashed"');
	elif attr.key:
		# keys cannot be multivalued (unique) or derived (we mustn't rely on calculation which may change)
		# TODO: we need care when dealing with keys on weak entities (which are partial!)
		opts.append('style="filled,solid,bold"');
	else:
		# normal attributes
		opts.append('style="filled,solid"');
	#	- write the attribute now
	f.write('\t\t"%s" [%s];\n' % (aName, ",".join(opts) ));
	
	# link to owner
	f.write('\t\t%s -- %s [len=0.5];\n' % (owner_name, aName));
	
	# for composite attributes, include the component attributes
	# NOTE: we simply define a composite attribute as one which can store 
	# 		a set of 'component' attributes...
	for subAttr in attr.components:
		writeAttribute(f, aName, subAttr);
	
# write the specialisation for the entity
def writeSpec (f, spec, index):
	# owner identifier to attach links to
	owner_name = spec.parent_entity.name
	
	# specialisation itself first - only if it has more than 1 derived attribute
	if len(spec.derived_entities) > 1:
		# name for this node
		my_name = "%s_s%d" % (owner_name, index);
		
		# write the spec itself
		# 	- options
		opts = ['shape=circle']
		opts.append('fillcolor="grey97"');
		opts.append('style="filled,solid"');
		if isinstance(spec, DisjointSpec):
			opts.append('label="d"');
		elif isinstance(spec, OverlapSpec):
			opts.append('label="o"');
		else:
			opts.append('label=""');
		# 	- write the spec item now
		f.write('\t"%s" [%s];\n' % (my_name, ",".join(opts) ));
		
		# write a link from spec to the entity that owns it
		# 	- options
		opts = [];
		if spec.total:
			# hack to get us total specialisation if there's only 1 specialisation for the class
			opts.append('color="black:black"');
		if spec.role:
			opts.append('label="%s"' % spec.role);
		opts.append('len=1.50');
		#	- write the link
		f.write('\t%s -- %s [%s];\n' % (owner_name, my_name, ",".join(opts) ));
		
		# make the name of this node the owner_name for subsequent entries
		owner_name = my_name
		
	# create links between derived entities and us
	for dEntity in spec.derived_entities:
		# write a link from spec to the entity that owns it
		# 	- options
		opts = ['shape="tee"', 'dir=forward'];
		opts.append('len=1.30');
		#	- write the link
		f.write('\t%s -- %s [%s];\n' % (owner_name, dEntity.name, ",".join(opts) ));

# write the links for specialisations for the given entity
# TODO: maybe we should just do all specs in one pass?
def writeEntitySpecs (f, entity):
	# write each specialisation and it's links
	for i,spec in enumerate(entity.specialisations):
		writeSpec(f, spec, i);
	f.write("\n");

# write the given entity to the graph file
def writeEntity (f, entity):
	# start a subgraph for entity and its attributes
	f.write('\tsubgraph {\n');

	# entity itself first
	#	- options
	opts = ['shape=box'];
	opts.append('fillcolor="lightblue2"');
	opts.append('style="filled,solid"');
	opts.append('label="%s"' % entity.name);
	if isinstance(entity, WeakEntity):
		opts.append('peripheries=2');
	#	- write the entity now
	f.write('\t\t"%s" [%s];\n' % (entity.name, ",".join(opts)));
	
	# entity attributes
	for attr in entity.attributes:
		writeAttribute(f, entity.name, attr);
		
	# close the subgraph
	f.write('\t}');
	
# write the given relationship to the graph file
def writeRelationship (f, rel):
	# start a subgraph for entity and its attributes
	f.write('\tsubgraph {\n');
	
	# add the relationship diamond
	#	- options
	opts = ['shape=diamond'];
	opts.append('fillcolor="lavenderblush2"');
	opts.append('style="filled,solid"');
	opts.append('label="%s"' % rel.name);
	if isinstance(rel, IdentifyingRel): 
		opts.append('peripheries=2');
	#	- write the node
	f.write('\t"%s" [%s];\n' % (rel.name, ",".join(opts) ));
	
	# relationship attributes
	for attr in rel.attributes:
		writeAttribute(f, rel.name, attr);
	
	# close the subgraph
	# NOTE: don't include links in this, since those can stretch further
	f.write('\t}');
	
	# add links from entities to relationship
	for link in rel.links:
		# build up list of options 
		opts = [];
		
		# NOTE: just use structural constraints instead of worrying about participation vs cardinality
		opts.append('label="(%s,%s)"' % link.structCon);
		opts.append('len=1.0');
		
		# write the link
		f.write('\t%s -- %s [%s];\n' % (link.entity.name, rel.name, ",".join(opts) ));

# ----------- 

# create the .dot graph file
def createGraph (fileN, model):
	# open graph file for writing
	f = open(fileN, 'w');
	
	# prefactory stuff...
	f.write('graph ER\n{\n');
	
	# write each entity to the file
	for entity in model.entities:
		writeEntity(f, entity);
		f.write("\n");
		
	# second pass over entity to add their specialisation links to the file
	for entity in model.entities:
		writeEntitySpecs(f, entity);
		
	# add some padding
	f.write("\n\n");
		
	# write each relationship to the file 
	for rel in model.relationships:
		writeRelationship(f, rel);
	
	# info about the graph
	#	- label string
	labelStr = "%s\\n" % (model.name);
	if len(model.description):
		labelStr += "%s\\n" % (model.description);
	labelStr += "by %s" % (model.getAuthorsString());
	f.write('\n\tlabel = "%s"\n' % (labelStr));
	# 	- other settings
	f.write('\toverlap = scalexy\n'); # very spaced out, but doesn't overlap... 
	
	# finishing up
	f.write('}\n');
	f.close();

##################################

# create a graph for the specified file
def convertSchema (fileN):
	print("$ Loading schema description...")
	
	# make sure filename is of the form *.dbcs
	# NOTE: this is just hack to allow entering filenames without extension
	fileN = dbcsLoader.changeExtension(fileN, "dbcs");
	
	# get the model used by the file
	model = dbcsLoader.readDBCS(fileN);
	if model is None:
		return False;
		
	# TODO: add a call to a module which helps validate the schema :)
	# 	-> could lead to this becoming a bit of an "la computadora tutor inteligente"
		
	print("$ Writing graphviz (.dot) version...")
	# get filename for graph representation
	fileG = dbcsLoader.changeExtension(fileN, "dot");
	
	# create a graph file for this
	createGraph(fileG, model);
	print("!! Done... :)");
	
	return True;
	
# run GraphViz on this if required
def run_graphviz(gv_engine, format, fileN):
	print("$ Running GraphViz (%s) to produce diagram..." % gv_engine)
	
	# get filename for graph representation
	fileG = dbcsLoader.changeExtension(fileN, "dot");
	# get filename for output image
	fileP = dbcsLoader.changeExtension(fileN, format);
	
	# run graphviz (specifically the 'neato' module), to produce a png of this...
	status = os.system("%s -T%s %s > %s" % (gv_engine, format, fileG, fileP));
	
	if status:
		print("!! Failed with %d! :( " % status)
	else:
		print("!! Done... :)");
	
##################################

# graphviz engines 
# TODO: no engine = skip?
gv_engines = ["neato", "fdp", "sfdp", "dot"];

# output formats
# TODO: what about other formats?
formats = ["png", "svg"];

# -----------

def main ():
	# always print version info first...
	# TODO: we should have a way to supress this for super-scripts...
	print("DataBase Conceptual Schema (EER) to Graphed Representation");
	print("Copyright 2010, Joshua Leung (aligorith@gmail.com)\n");
	
	# set up option parser for managing the commandline args
	usage = "usage: %prog [-e enginename] [-f format] [file1 [file2 [...]]]";
	parser = OptionParser(usage);
	parser.add_option("-e", "--engine", dest="gv_engine", 
			default="neato", type="string",
			help="Name of GraphViz engine to render the file with (out of %s)" % gv_engines)
	parser.add_option("-f", "--format", dest="format", 
			default="png", type="string",
			help="Name of output file format to render to (out of %s)" % formats)
	
	# parse commandline options
	(options, args) = parser.parse_args()
	
	# graphviz engine to use
	if (options.gv_engine) and (options.gv_engine in gv_engines):
		gv_engine = options.gv_engine;
	else:
		gv_engine = gv_engines[0]; # default to 'neato' again
	# output format
	if (options.format) and (options.format in formats):
		format = options.format;
	else:
		format = formats[0]; # default to 'png' again
	
	# parse filename arguments
	if len(args) >= 1:
		# argv[0] = scriptname...
		for fileN in sys.argv[1:]:
			# print info on file we're handling
			print("$ Processing file ===> %s ..." % fileN);
			
			# convert the file, then run graphviz on it 
			if convertSchema(fileN):
				run_graphviz(gv_engine, format, fileN);
			
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
			
			# try to process file
			if convertSchema(fileN):
				run_graphviz(gv_engine, format, fileN);
		
if __name__ == '__main__':
	main();
