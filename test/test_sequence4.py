# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import Place, MoveBy, Reverse
from cocos.sprite import Sprite

import pyglet

class TestLayer(cocos.layer.Layer):
    def __init__(self):
        super( TestLayer, self ).__init__()

        x,y = director.get_window_size()

        self.sprite = Sprite( 'grossini.png', (0,y/2)  )
        self.add( self.sprite )
        seq = MoveBy( (x/2, 0) )
        self.sprite.do( seq + Reverse(seq) )



if __name__ == "__main__":
    print " sprite starts at the left, goes to center screen and"
    print "then does the reverse action."
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)
