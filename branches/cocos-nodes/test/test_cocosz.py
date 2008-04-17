# This code is so you can run the samples without installing the package
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
#


import cocos
from cocos.director import director
from cocos.sprite import ActionSprite
import pyglet
from pyglet.gl import *

class Quad(cocos.cocosnode.CocosNode):
    def __init__(self, color, size):
        super(Quad, self).__init__()
        self.size = size
        self.qcolor = color
        
    def on_draw(self):
        glColor4ub(*self.qcolor)
        glBegin(GL_QUADS)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x+self.size, self.y)
        glVertex2f(self.x+self.size, self.y+self.size)
        glVertex2f(self.x, self.y+self.size)
        glEnd()
        glColor4ub(255,255,255,255)

class MultiQuadLayer(cocos.layer.Layer):
    def __init__(self):
        super(MultiQuadLayer, self).__init__()
        x, y = director.get_window_size()
        main = Quad((0,255,0,128), 200)
        for i in range(5):
            q = Quad((255,0,0,255), 30)
            q.position = (15*i, 15*i)
            main.add( q, z= i-2)
        main.position = ( x/2, y/2 )
        self.add( main )
        
        
if __name__ == "__main__":
    director.init()
    test_layer = MultiQuadLayer()
    main_scene = cocos.scene.Scene (test_layer)
    director.run (main_scene)
