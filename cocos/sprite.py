#
# ActionSprite
#

'''Action Sprite

Animating a sprite
==================

To execute any action you need to create an action::

    move = MoveBy( (50,0), 5 )

In this case, ``move`` is an action that will move the sprite
50 pixels to the right (``x`` coordinate), 0 pixel in the ``y`` coordinate,
and 0 pixels in the ``z`` coordinate in 5 seconds.

And now tell the sprite to execute it::

    sprite.do( move )
'''

__docformat__ = 'restructuredtext'

import interfaces
import rect
from director import director
import cocosnode

import pyglet
from pyglet import image
from pyglet.gl import *

__all__ = [ 'ActionSprite',                     # Sprite class
            'SpriteGroup',
            ]

class SpriteGroup(pyglet.graphics.Group):
    def __init__(self, sprite, group):
        super(SpriteGroup, self).__init__(parent=group)
        self.sprite = sprite

    def set_state(self):
        glPushMatrix()
        self.sprite.transform()

    def unset_state(self):
        glPopMatrix()

def ensure_batcheable(node):
    if not isinstance(node, BatchableNodeMixin):
        raise Exception("Children node of a batch must be have the batch mixin")
    for c in  node.get_children():
        ensure_batcheable(c)

class BatchNode( cocosnode.CocosNode ):
    def __init__(self):
        self.batch = pyglet.graphics.Batch()
        
    def add(self, child, z=0, name=None):
        ensure_batcheable(child)
        group = pyglet.graphics.OrderedGroup( z )
        child.set_batch( self.batch, group )
         
        super(Scene, self).add(child, z, name)
    
        
class BatchableNodeMixin( cocosnode.CocosNode ):
    def add(self, child, z=0, name=None):
        batchnode = self.get(BatchNode)
        if not batchnode: 
            # this node was addded, but theres no batchnode in the
            # hierarchy. so we proceed as normal
            super(Scene, self).add(child, *args, **kwargs)
            return
            
        # we are being batched, so we set groups and batch
        # pre/same/post will be set, because if we have a
        # batchnode parent, we already executed set_batch on self
        ensure_batcheable(child)
        if z < 0:
            group = self.pre_group
        elif z == 0:
            group = self.same_group
        else:
            group = self.post_group
            
        super(Scene, self).add(child, z, name)
        child.set_batch( self.batch, group )
        
                 
    def remove(self, child):
        child.set_batch( None, None )
        super(Scene, self).remove(child)
        
    def set_batch(self, batch, group):
        sprite_group = SpriteGroup(self, group)
        self.pre_group = SpriteGroup(self, OrderedGroup(-1, parent=group))
        self.group = OrderedGroup(0, parent=group)
        self.same_group = SpriteGroup(self, self.group)
        self.post_group = SpriteGroup(self, OrderedGroup(1, parent=group))
        self.batch = batch

        
        
class ActionSprite( cocosnode.CocosNode, pyglet.sprite.Sprite):
    '''ActionSprites are sprites that can execute actions.

    Example::

        sprite = ActionSprite('grossini.png')
    '''
    
    def __init__( self, image_name, *args, **kwargs ):
        img = pyglet.resource.image(image_name)
        img.anchor_x = img.width / 2
        img.anchor_y = img.height / 2
         
        pyglet.sprite.Sprite.__init__(self, img, *args, **kwargs)
        cocosnode.CocosNode.__init__(self)
        self.group = None
        self.children_group = None

    def on_draw(self):
        self._group.set_state()
        if self._vertex_list is not None:
            self._vertex_list.draw(GL_QUADS)
        self._group.unset_state()
        
ActionSprite.supported_classes = ActionSprite
