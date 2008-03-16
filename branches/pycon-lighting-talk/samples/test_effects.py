#
# Los Cocos: Effect Example
# http://code.google.com/p/los-cocos/
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cocos.actions import *
from cocos.director import director
from cocos.layer import *
from cocos.scene import Scene
from cocos.effect import TextureFilterEffect, ColorizeEffect, RepositionEffect
import pyglet
from pyglet import font
from pyglet.window import key
from pyglet.gl import *


class PictureLayer(Layer):

    def __init__ (self, y):
        self.x = 100
        self.y = y
        self.speed = 35
        self.img = pyglet.image.load ('ball.png')
    
    def step (self, dt):
        self.x += self.speed * dt
        if self.x > 200 and self.speed > 0: self.speed = -self.speed
        if self.x < 100 and self.speed < 0: self.speed = -self.speed
        self.img.blit (self.x, self.y)
        
class SpriteSequence( AnimationLayer ):
    def on_enter( self ):
        sprite1 = ActionSprite("grossinis_sister1.png")
        sprite2 = ActionSprite("grossinis_sister2.png")
        sprite3 = ActionSprite("grossini.png")

        sprite1.place( (260,200,0) )
        sprite2.place( (380,200,0) )
        sprite3.place( (320,185,0) )

        self.add( sprite1, sprite2, sprite3 )

        move1 = Move( (-200,0,0), 1, time_func=accelerate )
        move2 = Move( (200,0,0), 1, time_func=accelerate )
        jump1 = Jump( 80,-200,3, 2, time_func=accelerate )
        jump2 = Jump( 80,200,3, 2, time_func=accelerate )
        rot1 = Rotate( 180 * 3, 2, time_func=accelerate )
        rot2 = Rotate( -180 * 3, 2, time_func=accelerate )
        fade = FadeOut( 1 ) + FadeIn( 1 )

        j1 = Spawn( Repeat(jump1,2), Repeat(rot1,2) )
        j2 = Spawn( Repeat(jump2,2), Repeat(rot2,2) )
        
        rot = Rotate( 360 * 7, 2, time_func=accelerate )
        rot2 = Rotate( 360 * -7, 2, time_func=accelerate )
        sca = Scale( 5, 2 )
        sca2 = Scale( 1/5, 2 )

        sprite3.do( Repeat( Sequence( Repeat( sca,2 ), Repeat( sca2, 2 ), mode=RepeatMode ) ) )
        sprite3.do( Repeat( Repeat(rot,2) + Repeat(rot2,2) ) )

        sprite1.do( Repeat( Sequence( j1, Repeat(move1,2), fade, mode=RepeatMode ) ) )
        sprite2.do( Repeat( j2 + Repeat(move2,2) + fade ) )
        

class DynamicColorizeEffect (ColorizeEffect):
    def __init__ (self):
        super (ColorizeEffect, self).__init__ ()
        self.color = (1,1,1,1)
        self.timer = 0

    def prepare (self, target, dt):
        super (ColorizeEffect, self).prepare (target, dt)
        self.timer += dt
        # red glow: 
        red = self.timer % 2
        if red > 1: red = 2-red
        # set color
        self.color = (red,1,1,1)
        
class ControlLayer(Layer):

    def on_enter( self ):
        ft_title = font.load( None, 48 )
        ft_subtitle = font.load( None, 32 )
        ft_help = font.load( None, 16 )

        self.text_title = font.Text(ft_title, "Effects Examples",
            x=5,
            y=480,
            halign=font.Text.LEFT,
            valign=font.Text.TOP)

        self.text_subtitle = font.Text(ft_subtitle, effects[current_effect][0],
            x=5,
            y=400,
            halign=font.Text.LEFT,
            valign=font.Text.TOP)
        
        self.text_help = font.Text(ft_help,"Press LEFT / RIGHT for prev/next example",
            x=320,
            y=20,
            halign=font.Text.CENTER,
            valign=font.Text.CENTER)

    def step(self, dt):
        self.text_title.draw()
        self.text_subtitle.text = effects[current_effect][0]
        self.text_subtitle.draw()
#        self.text_help.draw()
        
    def on_key_press( self, k , m ):
        global current_effect
        if k == key.LEFT:
            current_effect = (current_effect-1)%len(effects)
            ball.set_effect(effects[current_effect][1])
        if k == key.RIGHT:
            current_effect = (current_effect+1)%len(effects)
            ball.set_effect(effects[current_effect][1])
        if k == key.ESCAPE:
            director.scene.end()
            return True


current_effect = 0
effects = [
    ("Layer without effects ", None),
    ("Layer translated and scaled", RepositionEffect(width=director.window.width/2) ),
    ]


ball = None

if __name__ == "__main__":
    director.init()

#    ball = PictureLayer(240)
    ball = SpriteSequence()
    director.run( Scene (ColorLayer(0.1,0.1,0.2,1), ball, ControlLayer()) )
