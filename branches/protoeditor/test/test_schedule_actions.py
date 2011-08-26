# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.actions import  *
from cocos.sprite import Sprite
import pyglet

class TestLayer(cocos.layer.Layer):

    def _step( self, dt ):
        super(TestLayer,self)._step(dt)
        print 'shall not happen'
        print self.rotation
         

if __name__ == "__main__":
    director.init()
    test_layer = TestLayer ()
    main_scene = cocos.scene.Scene()
    test_layer.do( RotateBy(360, duration=2) )
    director.run (main_scene)
