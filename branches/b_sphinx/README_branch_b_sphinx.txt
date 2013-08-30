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

r1254 edited conf.py for basic options
r1253 tweak builders make.bat and Makefile
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

# Tweak the builders make.bat and Makefile
    1. dirty fix in make.bat, set the sphinx.build path. Reason: I have mulple
    pythons, dont wan't to put python26\scripts in the path.
    Better solution should come later.

            if "%SPHINXBUILD%" == "" (
                    set SPHINXBUILD=c:\python26\scripts\\sphinx-build
		)

    2. log build warnings in doc\warnings.log for debug , change in make.bat
	%SPHINXBUILD% -w warnings.log -b html %ALLSPHINXOPTS% %BUILDDIR%/html

    3. same as in 2. but for Makefile
	$(SPHINXBUILD) -w warnings.log -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html

Commited r1253

# Edit doc\conf.py for basic configuration

    Agrego  ..\ al principio de sys.path para que cuando autodoc importe cocos
    lo haga desde la WC.
    
    seteo sys.is_epydoc para tener visibilidad de ciertas cosas mas amigables
    para documentar, tanto en pyglet como en cocos 
    
    agrego autosummary_generate = True
    
    agrego las extensions
      'sphinx.ext.autosummary',
      'sphinx.ext.inheritance_diagram'
      
    agrego dos params de extensiones que copie de pyglet
            inheritance_graph_attrs = dict(rankdir="LR", size='""')
            autodoc_member_order='groupwise'
            
    hago que la version de cocos se tome de cocos.version en vez de ponerla fija

    Hago que como fecha ponga * para que diffs entre corridas tengan menos ruido;
    es el setting today = ''
    
    Agrego _templates como patron a ignorar cuando recorre sourcedir

    Siguiendo a pyglet seteo add_module_names = False (para no agregar el module
    name a cosas como function)

    keep_warnings = True (creo que hace que los warnings se vean en el html)

    el titulo de la sidebar html_short_title = 'cocos'
	
Commited r1254
