#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
"""Layer class and subclasses

A `Layer` has as size the whole drawable area (window or screen),
and knows how to draw itself. It can be semi transparent (having holes
and/or partial transparency in some/all places), allowing to see other layers
behind it. Layers are the ones defining appearance and behavior, so most
of your programming time will be spent coding Layer subclasses that do what
you need. The layer is where you define event handlers.
Events are propagated to layers (from front to back) until some layer catchs
the event and accepts it.
"""

__docformat__ = 'restructuredtext'

import pyglet
from pyglet import gl

from cocos.director import *

__all__ = [ 'Layer', 'MultiplexLayer', 'AnimationLayer' ]

class Layer(object):
    """Class that handles events and other important game's behaviors"""

    effects = ()

    def __init__( self ):
        self.batch = pyglet.graphics.Batch()
        self.scheduled = False

    def set_effect (self, e):
        """
        Apply effect e to this layer. if e is None, current effect (if any)
        is removed

        :Parameters:
            `e` : `Effect` instance
                The effect that will be applied to the layer
        """
        if e is None:
            del self.effects
        else:
            self.effects = (e,)

    def on_draw( self ):
        """Draws every object that is in the batch and possible custom objets"""

        if self.effects:
            for e in self.effects:
                e.prepare (self)

            for e in self.effects:
                e.show ()
        else:
            self.batch.draw()
            self.draw()


    def draw( self ):        
        """Subclasses shall override this method if they want to draw custom objets"""
        pass           

    def on_enter( self ):
        """Called every time the layer enters into the scene"""
        pass 

    def on_exit( self ):
        """Called every time the layer quits the scene"""
        pass 

    def step( self, dt ):
        """Called every frame"""
        pass

    # helper functions
    def disable_step( self ):
        self.scheduled = False
        pyglet.clock.unschedule( self.step )

    def enable_step( self ):
        if not self.scheduled:
            self.scheduled = True 
            pyglet.clock.schedule( self.step )

#
# MultiplexLayer
class MultiplexLayer( Layer ):
    """A Composite layer that only enables one layer at the time.

     This is useful, for example, when you have 3 or 4 menus, but you want to
     show one at the time"""

    def __init__( self, *layers ):
        super( MultiplexLayer, self ).__init__()

        self.layers = layers 
        self.enabled_layer = 0

        for l in self.layers:
            l.switch_to = self.switch_to

    def switch_to( self, layer_number ):
        """Switches to another Layer that belongs to the Multiplexor.

        :Parameters:
            `layer_number` : Integer
                MUST be a number between 0 and the quantities of layers - 1.
                The running layer will receive an "on_exit()" call, and the
                new layer will receive an "on_enter()" call.
        """
        if layer_number < 0 or layer_number >= len( self.layers ):
            raise Exception("Multiplexlayer: Invalid layer number")

        # remove
        director.window.pop_handlers()
        self.layers[ self.enabled_layer ].on_exit()

        self.enabled_layer = layer_number
        director.window.push_handlers( self.layers[ self.enabled_layer ] )
        self.layers[ self.enabled_layer ].on_enter()

    def on_enter( self ):
        director.window.push_handlers( self.layers[ self.enabled_layer ] )
        self.layers[ self.enabled_layer ].on_enter()

    def on_exit( self ):
        director.window.pop_handlers()
        self.layers[ self.enabled_layer ].on_exit()

    def draw( self ):
        self.layers[ self.enabled_layer ].on_draw()


class AnimationLayer(Layer):
    """Useful class to handle animated (or alive) objects

    Each cycle it forwards the *step* call to all of its objects.
    """
    def __init__( self ):
        super( AnimationLayer, self ).__init__()

        self.objects = []

    def add( self, *o ):
        for i in o:
            self.objects.append( i )


class ColorLayer(Layer):
    """Creates a layer of a certain color"""
    def __init__(self, *color):
        self.color = color
        super(ColorLayer, self).__init__()

    def draw(self):
        gl.glColor4f(*self.color)
        x, y = director.get_window_size()
        gl.glBegin(gl.GL_QUADS)
        gl.glVertex2f( 0, 0 )
        gl.glVertex2f( 0, y )
        gl.glVertex2f( x, y )
        gl.glVertex2f( x, 0 )
        gl.glEnd()
        gl.glColor4f(1,1,1,1)    
