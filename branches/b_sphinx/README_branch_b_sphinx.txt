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

