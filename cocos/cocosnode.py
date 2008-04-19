#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#
"""
CocosNode: the basic ellement of cocos
"""

import bisect, copy

import pyglet
from pyglet.gl import *

from director import director
from mesh import Mesh

import weakref


__all__ = ['CocosNode']

class CocosNode(object):
    def __init__(self):
        # composition stuff
        self.children = []
        self.children_names = {}
        self.parent = None
        self.is_running = False

        # drawing stuff
        self.x, self.y = (0,0)
        self.scale = 1.0
        self.rotation = 0.0
        self.anchor_x = 0.5
        self.anchor_y = 0.5
        self.color = (255,255,255)
        self.opacity = 255
        self.mesh = Mesh()

        # actions stuff
        self.actions = []
        self.to_remove = []
        self.scheduled = False
        self.skip_frame = False


    def get(self, klass):
        """
        Walks the nodes tree upwards until it finds a node of the class `klass`
        or returns None
        """
        if isinstance(self, klass):
            return self
        parent = self.parent()
        if parent:
            return parent.get( klass )
            
    def _get_position(self):
        return (self.x, self.y)
    def _set_position(self, (x,y)):
        self.x, self.y = x,y
        
    position = property(_get_position, _set_position, doc="Get an (x,y) tuple")
        
    def add(self, child, z=0, name=None ):
        """Adds a child to the container

        :Parameters:
            `child` : object
                object to be added
            `z`: float
                the z index wrt self
            `name` : str
                Name of the child
        """
        # child must be a subclass of supported_classes
        #if not isinstance( child, self.supported_classes ):
        #    raise TypeError("%s is not istance of: %s" % (type(child), self.supported_classes) )

        if name:
            if name in self.children_names:
                raise Exception("Name already exists: %s" % name )
            self.children_names[ name ] = child

        child.parent = weakref.ref(self)

        elem = z, child
        bisect.insort( self.children,  elem )
        if self.is_running:
            child.on_enter()
        
    def remove( self, child ):
        """Removes a child from the container

        :Parameters:
            `child` : object
                object to be removed
        """
        l_old = len(self.children)
        self.children = [ (z,c) for (z,c) in self.children if c != child ]

        if l_old == len(self.children):
            raise Exception("Child not found: %s" % str(child) )

        if self.is_running:
            child.on_exit()

    def get_children(self):
        return [ c for (z, c) in self.children ]

    def __contains__(self, child):
        return  c in self.get_children()

    def remove_by_name( self, name ):
        """Removes a child from the container given its name

        :Parameters:
            `name` : string
                name of the reference to be removed
        """
        if name in self.children_names:
            child = self.children_names.pop( name )
            self.remove( child )
        else:
            raise Exception("Child not found: %s" % name )
            
    def on_enter( self ):
        """
        Called every time just before the node enters the stage.
        """
        self.is_running = True

        # start actions 
        self.resume()

        # propagate
        for c in self.get_children():
            c.on_enter()


    def on_exit( self ):
        """
        Called every time just before the node leaves the stage
        """
        self.is_running = False

        # pause actions
        self.pause()
        
        # propagate
        for c in self.get_children():
            c.on_exit()
                    
                     
    def transform( self ):
        """Apply ModelView transformations"""
        x,y = director.get_window_size()

        color = tuple(self.color) + (self.opacity,)
        if color != (255,255,255,255):
            glColor4ub( * color )

        if self.position != (0,0):
            glTranslatef( self.position[0], self.position[1], 0 )

        if self.scale != 1.0:
            glScalef( self.scale, self.scale, 1)

        if self.rotation != 0.0:
            glRotatef( -self.rotation, 0, 0, 1)
    
    def visit(self):
        position = 0
        # we visit all nodes that should be drawn before ourselves
        if self.children and self.children[0][0] < 0:
            glPushMatrix()
            self.transform()
            for z,c in self.children:
                if z >= 0: break
                position += 1
                c.visit()
                
            glPopMatrix()
            
        # we draw ourselves
        self.on_draw()
        
        # we visit al the remaining nodes, that are over ourselves
        if position < len(self.children):
            glPushMatrix()
            self.transform()
            for z,c in self.children[position:]:
                c.visit()
            glPopMatrix()
        
        
    def on_draw(self, *args, **kwargs):
        pass
                
    def do( self, action ):
        '''Executes an *action*.
        When the action finished, it will be removed from the sprite's queue.

        :Parameters:
            `action` : an `Action` instance
                Action that will be executed.
        :rtype: `Action` instance
        :return: A clone of *action*
        '''
        a = copy.deepcopy( action )

        a.target = self
        a.start()
        self.actions.append( a )

        if not self.scheduled:
            self.scheduled = True
            pyglet.clock.schedule( self._step )
        return a

    def remove_action(self, action ):
        """Removes an action from the queue

        :Parameters:
            `action` : Action
                Action to be removed
        """
        self.to_remove.append( action )

    def pause(self):
        if not self.scheduled:
            return
        self.scheduled = False
        pyglet.clock.unschedule( self._step )
        for c in self.get_children():
            c.pause()

    def resume(self):
        if self.scheduled:
            return
        self.scheduled = True
        pyglet.clock.schedule( self._step )
        self.skip_frame = True

        for c in self.get_children():
            c.resume()

    def flush(self):
        """Removes running actions from the queue"""
        for action in self.actions:
            self.to_remove.append( action )
        for c in self.get_children():
            c.flush()

    def actions_running(self):
        """Determine whether any actions are running."""
        return bool(set(self.actions) - set(self.to_remove))

    def _step(self, dt):
        """This method is called every frame.

        :Parameters:
            `dt` : delta_time
                The time that elapsed since that last time this functions was called.
        """
        for x in self.to_remove:
            if x in self.actions:
                self.actions.remove( x )
        self.to_remove = []

        if self.skip_frame:
            self.skip_frame = False
            return

        if len( self.actions ) == 0:
            self.scheduled = False
            pyglet.clock.unschedule( self._step )

        for action in self.actions:
            action.step(dt)
            if action.done():
                self.remove_action( action )
        

