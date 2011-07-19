"""
Implements some basic functionalities for level edition:
    select, change selection, move selection, scroll, zoom
Details:
    The operation is modeled after the Inkscape way.
    selection by mouse click or mouse drag (elastic box selection)
    selection with modifier key adds or subtract to selection
    move selected by mouse drag or keys
    when drag moving, pressing the appropriate modifier restricts to orto moves
    when moving by keys, pressing the appropriate modifier changes fastness
    zoom by mouse wheel or keys (default '+', '-' in keypad)
    scroll by keys: default ctrol + arrows (win), COMMAND + arrows (mac)
    autoscroll when mouse pointer near border
"""
import random
import weakref

import pyglet
from pyglet.window import key
from pyglet.window import mouse
from pyglet.gl import *

import cocos
from cocos.director import director
import cocos.collision_model as cm
import cocos.euclid as eu

fe = 1.0e-4
consts = {
    "window": {
        "width": 640,
        "height": 480,
        "vsync": True,
        "resizable": True
        },
    "world": {
        "width": 1200,
        "height": 1000,
        "rPlayer": 8.0,
        },
    "edit": {
        "bindings": {
            key.LEFT: 'left',
            key.RIGHT: 'right',
            key.UP: 'up',
            key.DOWN: 'down',            
            key.NUM_ADD: 'zoomin',
            key.NUM_SUBTRACT: 'zoomout',
            },
        "mod_modify_selection": key.MOD_SHIFT,
        "mod_restricted_mov": key.MOD_ACCEL,
        "keyscroll_relative_fastness": 0.5, # relative to autoscrolling_max_fastness
        "keymove_fastness_slow": 160.0,
        "keymove_fastness_fast": 320.0,
        "autoscroll_border": 20.0, #in pixels, float; None disables autoscroll
        "autoscrolling_max_fastness": 320.0 ,
        "wheel_multiplier": 2.5,
        "zoom_min": 0.1,
        "zoom_max": 2.0,
        "zoom_fastness": 1.0
        },
    }

class Actor(cocos.sprite.Sprite):
    colors = [(255, 255, 255), (0, 80, 0) ] 
    def __init__(self):
        super(Actor, self).__init__('ball32.png')
        radius = self.image.width / 2.0
        assert abs(radius-16.0)<fe
        self.cshape = cm.CircleShape(eu.Vector2(0.0, 0.0), radius)
#        self.cshape = cm.AARectShape(eu.Vector2(0.0, 0.0), radius, radius)

    def update_position(self, new_position):
        self.position = new_position
        self.cshape.center = new_position

class MinMaxRect(cocos.cocosnode.CocosNode):
    """ WARN: it is not a real CocosNode, it pays no attention to position,
        rotation, etc. It only draws the quad depicted by the vertexes.
        In other worlds, a nasty hack that gets the work done and you
        should not take as a CocosNode example"""
    def __init__(self):
        super(MinMaxRect, self).__init__()
        self.color3 = (0,0,255)
        self.vertexes = [(0.0, 0.0), (0.0, 0.0), (0.0, 0.0), (0.0, 0.0) ]
        self.visible = False

    def adjust_from_w_minmax(self, wminx, wmaxx, wminy, wmaxy):
        #asumes world to screen preserves order 
        sminx, sminy = world_to_screen(wminx, wminy) 
        smaxx, smaxy = world_to_screen(wmaxx, wmaxy)
        self.vertexes = [ (sminx, sminy), (sminx, smaxy), (smaxx, smaxy), (smaxx, sminy)] 
        
    def draw(self):
        if not self.visible:
            return
        glLineWidth(2) #deprecated
        glColor3ub(*self.color3)
        glBegin(GL_LINE_STRIP)
        for v in self.vertexes:
            glVertex2f(*v)
        glVertex2f(*self.vertexes[0])
        glEnd()

    def set_vertexes_from_minmax(self, minx, maxx, miny, maxy):
        self.vertexes = [ (minx, miny), (minx, maxy), (maxx, maxy), (maxx, miny)] 

class EditLayer(cocos.layer.Layer):
    is_event_handler = True

    def __init__(self, scroller, worldview,
                 bindings=None, keyscroll_relative_fastness=None, autoscroll_border=10,
                 autoscrolling_max_fastness=None, wheel_multiplier=None,
                 zoom_min=None, zoom_max=None, zoom_fastness=None,
                 mod_modify_selection=None, mod_restricted_mov=None,
                 keymove_fastness_slow=None, keymove_fastness_fast=None):
        super(EditLayer, self).__init__()

        self.bindings = bindings
        buttons = {}
        modifiers = {}
        for k in bindings:
            buttons[bindings[k]] = 0
            modifiers[bindings[k]] = 0
        self.buttons = buttons
        self.modifiers = modifiers

        self.keyscroll_relative_fastness = keyscroll_relative_fastness
        self.autoscroll_border = autoscroll_border
        self.autoscrolling_max_fastness = autoscrolling_max_fastness
        self.wheel_multiplier = wheel_multiplier
        self.zoom_min = zoom_min
        self.zoom_max = zoom_max
        self.zoom_fastness = zoom_fastness
        self.mod_modify_selection = mod_modify_selection
        self.mod_restricted_mov = mod_restricted_mov
        self.keymove_fastness_slow = keymove_fastness_slow
        self.keymove_fastness_fast = keymove_fastness_fast

        self.weak_scroller = weakref.ref(scroller)
        self.weak_worldview = weakref.ref(worldview)
        self.wwidth = worldview.width
        self.wheight = worldview.height

        self.screen_mouse = 1, 2
        self.autoscrolling = False
        self.drag_selecting = False
        self.drag_moving = False
        self.restricted_mov = False
        self.wheel = 0
        self.dragging = False

        self.mod_mask = mod_modify_selection | mod_restricted_mov
        # initialize move keys subsystem as inactive / oper do_nothing
        self.move_keys_active = False
        self.move_keys_oper = self.mod_mask
        self.move_keys_raw_delta = (0, 0)
        self.move_key_dpos = (0.0, 0.0)
        self.move_key_fastness = 0.0
        self.keyscrolling = False
        self.keymoving = False

        self.elastic_box = None
        self.selection = {}
        
        # before opers that change cshape must be set to False,
        # before selection opers must be set to True
        # use method set_selection_in_collman(value) to change state
        self.selection_in_collman = True
        
        #? Hardcoded here, should be obtained from level properties or calc
        # from available actors or current actors in worldview
        gsize = 32 * 1.25 
        self.collman = cm.CollisionManagerGrid(-gsize, self.wwidth + gsize,
                                               -gsize, self.wheight + gsize,
                                               gsize, gsize)
        for actor in worldview.actors:
            self.collman.add(actor)

        self.schedule(self.update)       

    def on_enter(self):
        super(EditLayer, self).on_enter()
        scene = self.get_ancestor(cocos.scene.Scene)
        if self.elastic_box is None:
            self.elastic_box = MinMaxRect()
            scene.add(self.elastic_box, z=10)
            self.selection_outlines = SelectionOutlines()
            scroller = self.weak_scroller()
            z = len(scroller.children)+1
            scroller.add(self.selection_outlines, z=z)            
        
    def update(self, dt):

        # autoscroll
        if self.autoscrolling:
            self.update_autoscroll(dt)
            
        if self.autoscrolling or self.dragging:
            # ignore move keys
            pass
        else:
            # process move keys
            # spec:
            # if any move key (left, right, up, down), then
            # if no modifier, move selection slow
            # if shift modifier, move selection fast
            # if mod_accel modifier, scroll window content
            # if both modifiers, do nothing
            mx = self.buttons['right'] - self.buttons['left'] 
            my = self.buttons['up'] - self.buttons['down']
            new_move_keys_active = (mx!=0 or my!=0)
            if not new_move_keys_active and not self.move_keys_active:
                # no key move cmd and not transition, nothing to do
                pass
            else:
                self.move_keys_active = new_move_keys_active
                # ensure base state for the oper (move, scroll, do_nothing)
                new_move_keys_oper = self.mod_mask & self.last_modifiers
                if not new_move_keys_active:
                    new_move_keys_oper = self.mod_mask
                if new_move_keys_oper != self.move_keys_oper:
                    # adjust base state
                    if self.keymoving:
                        if ( not new_move_keys_active or
                             new_move_keys_oper & self.mod_restricted_mov):
                            # terminate keymoving
                            self.end_selection_move()
                            self.keymoving = False
                    else:
                        if (new_move_keys_active and
                            not (new_move_keys_oper & self.mod_restricted_mov)):
                            # start keymoving
                            self.begin_selection_move()
                            self.move_key_dpos = eu.Vector2(0.0, 0.0)
                            self.keymoving = True

                    self.keyscrolling = (new_move_keys_oper == self.mod_restricted_mov)                        
                    assert not (self.keyscrolling and self.keymoving)

                    # force move_key_vel recalc
                    self.move_keys_raw_delta = None
                    
                    # recalc key_fastness for base state
                    if self.keyscrolling:
                        fastness = self.keyscroll_relative_fastness
                    elif self.keymoving:
                        if new_move_keys_oper & self.mod_modify_selection:
                            fastness = self.keymove_fastness_fast
                        else:
                            fastness = self.keymove_fastness_slow
                    else:
                        fastness = 0.0
                    self.move_key_fastness = fastness

                    # remember last oper
                    self.move_keys_oper = new_move_keys_oper 
                        
                # ensure vel needed is proper and stored as the oper needs
                if (mx, my) != self.move_keys_raw_delta:
                    # recalc vel
                    fastness = self.move_key_fastness
                    if mx!=0 and my!=0:
                        fastness *= 0.707106 # 1/sqrt(2)
                    vel = eu.Vector2(fastness*mx, fastness*my)
                    if self.keyscrolling:
                        self.autoscrolling_relative_fastness = vel
                    else:
                        self.move_key_vel = vel 
                    self.move_keys_raw_delta = (mx, my)

                # perform oper
                if self.keyscrolling:
                    self.update_autoscroll(dt)
                elif self.keymoving:
                    self.move_key_dpos += dt*self.move_key_vel
                    self.move_selection(self.move_key_dpos)

        # drag move
        if self.drag_moving:
            # update positions
            wx, wy = self.world_mouse
            dx = wx - self.wdrag_start_point[0]
            dy = wy - self.wdrag_start_point[1]
            if self.restricted_mov:
                if abs(dy) > abs(dx):
                    dx = 0
                else:
                    dy = 0
            dpos = eu.Vector2(dx, dy)
            self.move_selection(dpos)

        # zoom
        dz = self.buttons['zoomin'] - self.buttons['zoomout']
        zoom_change = (dz != 0 or self.wheel != 0)
        if zoom_change:
            self.update_zoom(dz)

    def update_zoom(self, dz):
        if self.mouse_into_world():
            wzoom_center = self.world_mouse
            szoom_center = self.screen_mouse
        else:
            # decay to scroller unadorned
            wzoom_center = None
        if self.wheel !=0:
            dt_dz = 0.01666666 * self.wheel
            self.wheel = 0
        else:
            dt_dz = dt * dz
        scroller = self.weak_scroller()
        zoom = scroller.scale + dt_dz * self.zoom_fastness
        if zoom < self.zoom_min:
            zoom = self.zoom_min
        elif zoom > self.zoom_max:
            zoom = self.zoom_max
        scroller.scale = zoom
        if wzoom_center is not None:
            # postprocess toward 'world point under mouse the same before
            # and after zoom' ; other restrictions may prevent fully comply
            wx1, wy1 = screen_to_world(*szoom_center)
            fx = scroller.restricted_fx + (wzoom_center[0] - wx1)
            fy = scroller.restricted_fy + (wzoom_center[1] - wy1)
            scroller.set_focus(fx, fy)

    def move_selection(self, dpos):
        for actor in self.selection:
            old_pos = self.selection[actor].center
            new_pos = old_pos + dpos
            #? clamp new_pos so actor into world boundaries ?
            actor.update_position(new_pos)

    def update_mouse_position(self, sx, sy):
        self.screen_mouse = sx, sy
        self.world_mouse = screen_to_world(sx, sy)
        # handle autoscroll
        border = self.autoscroll_border
        if border is not None:
            #sleft and companions includes the border
            scroller = self.weak_scroller()
            self.update_view_bounds() # si queda aca podria ponerlo inline
            sdx = 0.0
            if sx < self.sleft:
                sdx = sx - self.sleft
            elif sx > self.sright:
                sdx = sx - self.sright
            sdy = 0.0
            if sy < self.sbottom:
                sdy = sy - self.sbottom
            elif sy > self.s_top:
                sdy = sy - self.s_top
            self.autoscrolling = sdx != 0.0 or sdy != 0.0
            if self.autoscrolling:
                self.autoscrolling_relative_fastness = (sdx / border,
                                                        sdy / border)

    def update_autoscroll(self, dt):
        fraction_sdx, fraction_sdy = self.autoscrolling_relative_fastness
        scroller = self.weak_scroller()
        worldview = self.weak_worldview()
        f = self.autoscrolling_max_fastness
        wdx = (fraction_sdx * f * dt) / scroller.scale / worldview.scale
        wdy = (fraction_sdy * f * dt) / scroller.scale / worldview.scale
        # ask scroller to try scroll (wdx, wdy)
        fx = scroller.restricted_fx + wdx
        fy = scroller.restricted_fy + wdy
        scroller.set_focus(fx, fy)
        self.world_mouse = screen_to_world(*self.screen_mouse)
        if self.elastic_box.visible:
            self.adjust_elastic_box()

    def update_view_bounds(self):
        scroller = self.weak_scroller()
        scx , scy = world_to_screen(scroller.restricted_fx,
                                    scroller.restricted_fy)
        hw = scroller.view_w/2.0
        hh = scroller.view_h/2.0
        border = self.autoscroll_border
        self.sleft = scx - hw + border
        self.sright = scx + hw - border
        self.sbottom = scy - hh + border
        self.s_top = scy + hh - border

    def mouse_into_world(self):
        worldview = self.weak_worldview()
        #? allow lower limits != 0 ?
        return ( (0 <= self.world_mouse[0] <= worldview.width) and
                 (0 <= self.world_mouse[1] <= worldview.height))

    def on_key_press(self, k, m):
        self.last_modifiers = m
        binds = self.bindings
        if k in binds:
            self.buttons[binds[k]] = 1
            self.modifiers[binds[k]] = 1
            return True
        return False

    def on_key_release(self, k, m ):
        self.last_modifiers = m
        binds = self.bindings
        if k in binds:
            self.buttons[binds[k]] = 0
            self.modifiers[binds[k]] = 0
            return True
        return False

    def on_mouse_motion(self, sx, sy, dx, dy):
        self.update_mouse_position(sx, sy)

    def on_mouse_leave(self, sx, sy):
        self.autoscrolling = False

    def on_mouse_press(self, x, y, buttons, modifiers):
        pass

    def on_mouse_release(self, sx, sy, button, modifiers):
        wx, wy = screen_to_world(sx, sy)
        modify_selection = modifiers & self.mod_modify_selection
        if self.dragging:
            # ignore all buttons except left button
            if button != mouse.LEFT:
                return
            if self.drag_selecting:
                self.end_drag_selection(wx, wy, modify_selection)
            elif self.drag_moving:
                self.end_selection_move()
                self.drag_moving = False

            self.dragging = False
        else:
            if button == mouse.LEFT:
                self.end_click_selection(wx, wy, modify_selection)

    def end_click_selection(self, wx, wy, modify_selection):
        under_mouse_unique = self.single_actor_from_mouse()
        if modify_selection:
            # toggle selected status for unique
            if under_mouse_unique in self.selection:
                self.selection_remove(under_mouse_unique)
            elif under_mouse_unique is not None:
                self.selection_add(under_mouse_unique)
        else:
            # new_selected becomes the current selected
            self.selection.clear()
            if under_mouse_unique is not None:
                self.selection_add(under_mouse_unique)
        self.selection_changed()
            
    def selection_add(self, actor):
        self.selection[actor] = actor.cshape.copy()
        
    def selection_remove(self, actor):
        del self.selection[actor]
        
    def end_drag_selection(self, wx, wy, modify_selection):
        new_selection = self.collman.objs_into_box(*self.elastic_box_wminmax)
        if not modify_selection:
            # new_selected becomes the current selected
            self.selection.clear()
        for actor in new_selection:
            self.selection_add(actor)
        self.selection_changed()

        self.elastic_box.visible = False
        self.drag_selecting = False
        
    def on_mouse_drag(self, sx, sy, dx, dy, buttons, modifiers):
        #? should ignore if out of client area / scroller viewport ?
        self.update_mouse_position(sx, sy)
        if not buttons & mouse.LEFT:
            # ignore except for left-btn-drag
            return
        
        if not self.dragging:
            self.begin_drag(modifiers)
            return

        if self.drag_selecting:
            # update elastic box
            self.adjust_elastic_box()
        elif self.drag_moving:
            self.restricted_mov = (modifiers & self.mod_restricted_mov)

    def adjust_elastic_box(self):
        # when elastic_box visible this method needs to be called any time
        # world_mouse changes or screen_to_world results changes (scroll, etc)
        wx0, wy0 = self.wdrag_start_point
        wx1, wy1 = self.world_mouse
        wminx = min(wx0, wx1)
        wmaxx = max(wx0, wx1)
        wminy = min(wy0, wy1)
        wmaxy = max(wy0, wy1)
        self.elastic_box_wminmax = wminx, wmaxx, wminy, wmaxy
        self.elastic_box.adjust_from_w_minmax(*self.elastic_box_wminmax)

    def begin_drag(self, modifiers):
        self.dragging = True
        self.wdrag_start_point = self.world_mouse
        under_mouse_unique = self.single_actor_from_mouse()
        if ((under_mouse_unique is None) or
            (modifiers & self.mod_modify_selection)):
            # begin drag selection
            self.drag_selecting = True
            self.adjust_elastic_box()
            self.elastic_box.visible = True
        else:
            # want drag move
            if under_mouse_unique in self.selection:
                # want to move current selection
                pass
            else:
                # change selection before moving
                self.selection.clear()
                self.selection_add(under_mouse_unique)
                self.selection_changed()
            self.begin_selection_move()
            self.drag_moving = True

    def begin_selection_move(self):
        self.set_selection_in_collman(False)

    def end_selection_move(self):
        self.set_selection_in_collman(True)
        for actor in self.selection:
            self.selection[actor] = actor.cshape.copy()        

    def single_actor_from_mouse(self):
        under_mouse = self.collman.objs_touching_point(*self.world_mouse)
        if len(under_mouse)==0:
            return None
        # return the one with the center most near to mouse, if tie then
        # an arbitrary in the tie
        nearest = None
        near_d = None
        p = eu.Vector2(*self.world_mouse)
        for actor in under_mouse:
            d = (actor.cshape.center - p).magnitude_squared()
            if nearest is None or (d < near_d):
                nearest = actor
                near_d = d
        return nearest
        
    def set_selection_in_collman(self, bool_value):
        if self.selection_in_collman == bool_value:
            return
        self.selection_in_collman = bool_value
        if bool_value:
            for actor in self.selection:
                self.collman.add(actor)
        else:
            for actor in self.selection:
                self.collman.remove_tricky(actor)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        #? check if mouse over scroller viewport?
        self.wheel += scroll_y * self.wheel_multiplier

    def selection_changed(self):
        self.selection_outlines.selection = self.selection

class ColorRect(cocos.cocosnode.CocosNode):
    def __init__(self, width, height, color4):
        super(ColorRect,self).__init__()
        self.color4 = color4
        w2 = int(width/2)
        h2 = int(height/2)
        self.vertexes = [(0,0,0),(0,height,0), (width,height,0),(width,0,0)]

    def draw(self):
        glPushMatrix()
        self.transform()
        glBegin(GL_QUADS)
        glColor4ub( *self.color4 )
        for v in self.vertexes:
            glVertex3i(*v)
        glEnd()
        glPopMatrix()

class Worldview(cocos.layer.ScrollableLayer):
    def __init__(self, width=None, height=None, rPlayer=None):
        super(Worldview, self).__init__()
        self.width = width
        self.height = height
        self.px_width = width
        self.px_height = height

        # background
        self.add( ColorRect(width, height, (0,0,255,255)), z=-2)
        border_size = 10
        inner = ColorRect(width-2*border_size, height-2*border_size, (255,0,0,255))
        inner.position = (border_size, border_size)
        self.add(inner, z=-1 )

        #actors
        use_batch = True
        if use_batch:
            self.batch = cocos.batch.BatchNode()
            self.add(self.batch)
        self.actors = []
        m = height/float(width)
        i = 0
        #? issue: modifying step to 4*rPlayer*2 breaks keyscrolling (?)(!)
        # Quack!!! . The problem happens because:
        #   . more separation implies less visible actors
        #   . which renders faster
        #   . intel chipset don't honors pyglet vsync=True
        #   . produces small dt
        #   . ScrollerManager intifies focus at enter and exit
        #   . thus the small moves required by update_autoscroll are lost
        for x in xrange(0, int(width), int(4*rPlayer)):
            y = m*x
            actor = Actor()
            actor.update_position(eu.Vector2(float(x), float(y)))
            if use_batch:
                self.batch.add(actor, z=i)
            else:
                self.add(actor, z=i)
            self.actors.append(actor)
            i += 1

    def on_enter(self):
        super(Worldview, self).on_enter()
        scroller = self.get_ancestor(cocos.layer.ScrollingManager)
        scroller.set_focus(self.width/2.0, self.height/2.0) 
        

class SelectionOutlines(cocos.layer.ScrollableLayer):
    def __init__(self):
        super(SelectionOutlines, self).__init__()
        self.selection = {}
        
    def set_glstate(self):
        glPushAttrib( GL_ALL_ATTRIB_BITS )
        glPolygonMode( GL_FRONT_AND_BACK, GL_LINE )
        glLineWidth( 2.0 )
        glColor3f( 1.0, 1.0, 1.0 )
        
        # uncomment for line dashed / dotted
        #glEnable(GL_LINE_STIPPLE)
        #glLineStipple(1, 0x00FF) # 0x00FF dashed, 0x0101 dotted

    def unset_glstate(self):
        # uncomment for line dashed / dotted
        #glDisable(GL_LINE_STIPPLE)

        glPopAttrib()

    def visit(self):
        self.set_glstate()
        glPushMatrix()
        self.transform()
        for actor in self.selection:
            actor._vertex_list.draw(GL_QUADS)
        glPopMatrix()
        self.unset_glstate()

print __doc__
director.init(**consts["window"])
scene = cocos.scene.Scene()
scrolling_manager = cocos.layer.ScrollingManager()
scene.add(scrolling_manager)
playview = Worldview(**consts['world'])
scrolling_manager.add(playview, z=0)
world_to_screen = scrolling_manager.pixel_to_screen
screen_to_world = scrolling_manager.pixel_from_screen
editor = EditLayer(scrolling_manager, playview, **consts['edit'])
scene.add(editor)
director.run(scene)