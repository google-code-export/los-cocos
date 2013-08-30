The branch's purpose is to migrate the cocos documentation from epydoc to sphinx.

Goals and scope:

  A functional sphinx builder

  No code changes allowed in the package cocos except for docstrings

  Avoid heavy sphinx customization (hard to mantain, entry barrier
  for new people)  

  Branch should be closed fast
    Polishing should be done later

    When parts not rendering in sphinx are limited to non critical components,
    close the branch and open issues for trunk
	
Changelog:

r1252 after running sphinx-quistart snapshoting doc 
r1251 doc\doc.css -> doc\doc.old.css
r1250 doc\index -> doc\index.old.txt
r1249 Added dev notes
r1248 Branch creation


Dev notes:

# Make room for generating sphinx skeleton with conventional names without
losing info

doc\index.txt -> doc\index.old.txt
doc\doc.css -> doc\doc.old.css
Commited r1250 & r1251

# run sphinx-quickstart
    cd D:\cocos_pristine\b_sphinx\doc
    c:\python26\scripts\sphinx-quickstart

It added 4 files:
    doc/Makefile
    doc/conf.py
    doc/index.txt
    doc/make.bat
And 3 empty directories:
    doc/_build
    doc/_static
    doc/_templates

No previous file modified.

Surely the new index and the old one would need to be convined; doc.old.css
probably should be deleted.

Checking in the new files / dirs without modifications for reference
Commited r1252

