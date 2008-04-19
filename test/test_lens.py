# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.sprite import *
from cocos.actions import *
from cocos.layer import *
import pyglet
import random

from cocos.mesh import *

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()
        
        x,y = director.get_window_size()
        
        sprite1 = ActionSprite( 'grossini.png', (x/2, y/2) )
        sprite2 = ActionSprite( 'grossinis_sister1.png', (x/4,y/2) )
        sprite3 = ActionSprite( 'grossinis_sister2.png', (x/4*3, y/2) )

        self.add( sprite2 )
        self.add( sprite1 )
        self.add( sprite3 )


if __name__ == "__main__":
    director.init( resizable=True )
    director.show_FPS = True
    main_scene = cocos.scene.Scene()

    def rcol(): return int(random.random()*255)
    for i in range(32):
        l = ColorLayer(rcol(), rcol(), rcol(), 255)
        l.scale = (32-i)/32.0
        main_scene.add( l, z=i )

    tl1 = TestLayer()
    main_scene.add( tl1, z=33 )

    e = Lens( grid=(32,32), duration=100 )
    main_scene.do( e )

    director.run (main_scene)
