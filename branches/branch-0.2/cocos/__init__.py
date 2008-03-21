"""
Los Cocos: An extension for Pyglet 

http://code.google.com/p/los-cocos/
"""

__version__ = "0.2.0"
__author__ = "PyAr Team"
version = __version__

def check_pyglet_version():
    import pyglet
    if pyglet.version.find( '1.0' ) != -1:
        print "*" * 80
        print "\ncocos v%s does not work with pyglet v%s" % (__version__, pyglet.version )
        print "\nUse pyglet v1.1 or download to cocos-0.1.x\n"
        print "*" * 80
        raise Exception("Invalid pyglet version: %s" % pyglet.version)

check_pyglet_version()

import actions
import director
import effect
import layer
import menu
import path
import scene

