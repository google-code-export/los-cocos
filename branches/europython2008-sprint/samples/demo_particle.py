#
# cocos2d
# http://cocos2d.org
#

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import pyglet
from pyglet import image, font
from pyglet.window import key

from cocos.scene import Scene
from cocos.director import director
from cocos.layer import Layer 
from cocos.particle_systems import *


def get_particle_test( index ):
    d = tests[index]
    return Scene( FontLayer( title = d[0], subtitle=d[1]), ParticleLayer( index, d[2]() ) )

class FontLayer( Layer ):
    def __init__( self, title="Particle Exmaple #", subtitle ="XXX"  ):
        super( FontLayer, self ).__init__()

        self.title = title
        self.subtitle = subtitle

        self.batch = pyglet.graphics.Batch()

        self.text_title = pyglet.text.Label(self.title,
            font_size=32,
            x=5,
            y=director.get_window_size()[1],
            anchor_x=font.Text.LEFT,
            anchor_y=font.Text.TOP,
            batch=self.batch)

        self.text_subtitle = pyglet.text.Label(self.subtitle,
            multiline=True,
            width=600,
            font_size=16,
            x=5,
            y=director.get_window_size()[1] - 80,
            anchor_x=font.Text.LEFT,
            anchor_y=font.Text.TOP,
            batch=self.batch )

        self.text_help = pyglet.text.Label("Press LEFT / RIGHT for prev/next test, ENTER to restart example",
            font_size=16,
            x=director.get_window_size()[0] /2,
            y=20,
            anchor_x=font.Text.CENTER,
            anchor_y=font.Text.CENTER,
            batch=self.batch )

    def draw( self ):
        pyglet.gl.glPushMatrix()
        self.transform()
        self.batch.draw()
        pyglet.gl.glPopMatrix()

class ParticleLayer( Layer ):

    is_event_handler = True     #: enable pyglet's events

    def __init__( self, index, particle_instance ):
        super(ParticleLayer, self ).__init__()
        self.index = index
        self.particle_instance = particle_instance
        self.particle_instance.position = (320,200)

    def on_enter( self ):
        super( ParticleLayer, self).on_enter()
        self.add( self.particle_instance )

    def on_key_release( self, keys, mod ):
        # LEFT: go to previous scene
        # RIGTH: go to next scene
        # ENTER: restart scene
        if keys == key.LEFT:
            self.index -= 1
            if self.index < 1:
                self.index = len( tests )
        elif keys == key.RIGHT:
            self.index += 1
            if self.index > len( tests ):
                self.index = 1

        if keys in (key.LEFT, key.RIGHT, key.ENTER):
            director.replace( get_particle_test( self.index ) )
            return True

tests = {
 1: ("Particles #1- Fireworks", "", Fireworks),
 2: ("Particles #2 - Spiral", "", Spiral),
 3: ("Particles #3 - Sun", "", Sun),
 4: ("Particles #4 - Fire", "", Fire),
 5: ("Particles #5 - Galaxy", "", Galaxy),
 6: ("Particles #6 - Flower", "", Flower),
 7: ("Particles #7 - Meteor", "", Meteor),
 8: ("Particles #8 - Explosion", "", Explosion),
 9: ("Particles #9 - Smoke", "", Smoke),
}

if __name__ == "__main__":
    director.init( resizable=True, caption='cocos2d - Particle demo' )
#    director.window.set_fullscreen(True)
    director.run( get_particle_test( 1 ) )
