#
# Los Cocos: An extension for Pyglet
# http://code.google.com/p/los-cocos/
#

"""
Scene class and subclasses
"""
__docformat__ = 'restructuredtext'

__all__ = ['Scene']

from pyglet.gl import *

from interfaces import *
from director import director
import layer
import cocosnode

class Scene(cocosnode.CocosNode):
    """
    """
   
    def __init__(self, *children):
        """
        Creates a Scene with layers and / or scenes.
        
        Responsabilities:
            Control the dispatching of events to its layers
            
        :Parameters:
            `children` : list of `Layer` or `Scene`
                Layers or Scenes that will be part of the scene.
                They are automatically asigned a z-level from 0 to
                num_children.
        """

        super(Scene,self).__init__()
        self._handlers_enabled = False
        for i, c in enumerate(children):
            self.add( c, z=i )
        
    def add(self, child, *args, **kwargs):
        super(Scene, self).add(child, *args, **kwargs)
        if self._handlers_enabled:
            self.push_handlers_for(child)

    def remove(self, child):
        super(Scene, self).remove(child)
        if self._handlers_enabled:
            self.remove_handlers_for(child)

    def on_enter(self):
        super(Scene, self).on_enter()
        if self._handlers_enabled:
            self.push_all_handlers()
        
    def on_exit(self):
        super(Scene, self).on_exit()
        if self._handlers_enabled:
            self.remove_all_handlers()
        
    def push_handlers_for(self, who):
        if isinstance(who, layer.Layer):
            if who.push_handlers:
                director.window.push_handlers( who )
            for child in who.get_children():
                self.push_handlers_for( child )
                
    def remove_handlers_for(self, who):
        if isinstance(who, layer.Layer):
            if who.push_handlers:
                director.window.remove_handlers( who )
            for child in who.get_children():
                self.remove_handlers_for( child )
            
    def push_all_handlers(self):
        for child in self.get_children():
            self.push_handlers_for( child )
            
    def remove_all_handlers(self):
        for child in self.get_children():
            self.remove_handlers_for( child )
    
    def enable_handlers(self, value=True):
        """
        This function makes the scene elegible for receiving events
        """
        if value and not self._handlers_enabled and self.is_running:
            self.push_all_handlers()
        elif not value and self._handlers_enabled and self.is_running:
            self.remove_all_handlers()
        self._handlers_enabled = value
        
        
    def end(self, value=None):
        """Ends the current scene setting director.return_value with `value`
        
        :Parameters:
            `value` : anything
                The return value. It can be anything. A type or an instance.
        """
        director.return_value = value
        director.pop()

