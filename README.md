# dbcskit
About
=====

This toolkit was initially quickly hacked together over a weekend to as a means of describing EER schemas born out of frustration over time lost tweaking schema diagrams visually.

It's primary focus is on being a somewhat efficient method of inputting and storing EER schemas, such that they provide a compact while readable format that can be easily edited by any human with a text editor. A mini-language built on top of the Python programming language is provided for this, allowing users to concentrate on the CONTENT and TOPOLOGY of the schema (entities, relationships, attributes) without worrying about details of layout (i.e. painstakingly aligning and realigning elements and links).

Included in the toolkit are:

 1. a tool which generates diagrams of the schemas described in .dbcs files, using GraphViz to determine the appropriate layout for the elements. The diagrams produced conform to the notation used in "Fundamentals of Database Systems" (4th Ed.) by Elmasri and Navathe (which appears to be the notation popularised in the original 1976 paper by Peter Chen ([1]), though min/max notation or structural constraints have been used in favor of participation+cardinality ratios for coding convenience).
 2. a tool which performs automated tests of the schemas described in .dbcs files, identifying common design flaws or errors in the schema design. In future, it would be interesting to be able to extend this to measure the appropriateness of a solution to a given requirements brief (potentially presented in a natural language format). 

Future extensions (not implemented yet) tentatively include:

 * A GUI facilitating an alternative interface for creating such schemas without burdening the user with graphical concerns still
 * Implementation of a converter to relational schemas and/or also a direct SQL generator (passing through the relational schema component) 

The current codebase has been tested to work with Python 2.6 on Windows (Vista SP1) and Linux (Fedora 12). No guarantees are made that it will work on Python 3.x, though this may still work.

References
---------
 * Peter Chen (March 1976). "The Entity-Relationship Model - Toward a Unified View of Data". ACM Transactions on Database Systems 1 (1): 9?36. doi:10.1145/320434.320440.
 * http://en.wikipedia.org/wiki/Entity-relationship_model#Diagramming_conventions 

Usage
=====

Before First Usage
------------------
 1. Download a distribution of this project, or grab the latest copy from svn trunk. As with all my software, there is NO INSTALLATION NEEDED (tm), since software that needs installation to work has severe failures already with their architecture!
 2. Make sure that you've got python and GraphViz installed and included in your PATH. It is assumed that these are available in this fashion... 

To Use
------
 1. Create a .dbcs file as per the templates in the examples folder.
 2. Run dbcs2Graph.py, and either supply the name of the file as an arg, or enter it when prompted. On Windows, simply run the dbcs2Graph.bat by double clicking on it. 
