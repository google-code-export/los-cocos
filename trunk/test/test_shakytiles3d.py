# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import pyglet
import cocos
from cocos.director import director
from cocos.actions import *
from cocos.layer import *


class BackgroundLayer( cocos.layer.Layer ):
    def __init__(self):
        super( BackgroundLayer, self ).__init__()
        self.img = pyglet.resource.image('background_image.png')

    def draw( self ):
        self.img.blit(0,0)

def main():
    director.init( resizable=True )
    main_scene = cocos.scene.Scene()

    main_scene.add( BackgroundLayer(), z=0 )

    main_scene.do( ShakyTiles3D( randrange=6, grid=(8,16), duration=5) )
    director.run (main_scene)

if __name__ == '__main__':
    main()
